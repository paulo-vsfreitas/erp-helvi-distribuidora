from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from financeiro.models import (
    BaixaPagar,
    ContaPagar,
    ContaReceber,
    HistoricoContaPagar,
    HistoricoContaReceber,
    MovimentacaoFinanceira,
    ParcelaPagar,
    ParcelaReceber,
    RecebimentoConta,
)


def _validar_motivo(motivo):
    motivo = (motivo or "").strip()

    if len(motivo) < 5:
        raise ValidationError(
            "Informe um motivo com pelo menos 5 caracteres."
        )

    return motivo


def _validar_usuario(usuario):
    if not usuario or not usuario.is_authenticated:
        raise ValidationError(
            "Não foi possível identificar o usuário responsável."
        )


def _atualizar_conta_pagar(conta):
    total_pago = (
        conta.parcelas.aggregate(total=Sum("valor_pago"))["total"]
        or 0
    )
    conta.valor_pago = total_pago
    conta.status = ContaPagar.STATUS_PENDENTE
    conta.atualizar_status()
    conta.save(update_fields=["valor_pago", "status", "atualizado_em"])


def _atualizar_conta_receber(conta):
    total_recebido = (
        conta.parcelas.aggregate(total=Sum("valor_recebido"))["total"]
        or 0
    )
    conta.valor_recebido = total_recebido
    conta.status = ContaReceber.STATUS_PENDENTE
    conta.atualizar_status()
    conta.save(
        update_fields=["valor_recebido", "status", "atualizado_em"]
    )


@transaction.atomic
def estornar_baixa(*, baixa, usuario, motivo):
    """Estorna uma baixa a pagar e registra a entrada financeira inversa."""
    _validar_usuario(usuario)
    motivo = _validar_motivo(motivo)
    baixa_id = baixa.pk if isinstance(baixa, BaixaPagar) else baixa

    baixa = (
        BaixaPagar.objects.select_for_update()
        .select_related("parcela__conta_pagar", "conta_financeira")
        .get(pk=baixa_id)
    )

    if baixa.estornada:
        raise ValidationError("Esta baixa já foi estornada.")

    parcela = ParcelaPagar.objects.select_for_update().get(
        pk=baixa.parcela_id
    )
    conta = ContaPagar.objects.select_for_update().get(
        pk=parcela.conta_pagar_id
    )

    if conta.status == ContaPagar.STATUS_CANCELADA:
        raise ValidationError(
            "Não é possível estornar uma baixa de uma conta cancelada."
        )

    movimentacao_original = (
        baixa.movimentacoes.select_for_update()
        .filter(
            tipo=MovimentacaoFinanceira.TIPO_SAIDA,
            estornada=False,
        )
        .first()
    )

    if movimentacao_original is None:
        raise ValidationError(
            "A movimentação original desta baixa não foi encontrada."
        )

    agora = timezone.now()

    MovimentacaoFinanceira.objects.create(
        conta_financeira=baixa.conta_financeira,
        categoria=conta.categoria,
        baixa_pagar=baixa,
        tipo=MovimentacaoFinanceira.TIPO_ESTORNO_SAIDA,
        data_movimentacao=timezone.localdate(),
        valor=baixa.valor_movimentado,
        descricao=(
            f"Estorno da baixa da conta #{conta.numero} — "
            f"parcela {parcela.numero}"
        ),
        origem="estorno_conta_pagar",
        criado_por=usuario,
    )

    baixa.estornada = True
    baixa.estornada_por = usuario
    baixa.estornada_em = agora
    baixa.motivo_estorno = motivo
    baixa.save(
        update_fields=[
            "estornada",
            "estornada_por",
            "estornada_em",
            "motivo_estorno",
        ]
    )

    parcela.valor_pago = max(parcela.valor_pago - baixa.valor, 0)
    parcela.status = ParcelaPagar.STATUS_PENDENTE
    parcela.save(update_fields=["valor_pago", "status", "atualizado_em"])
    _atualizar_conta_pagar(conta)

    HistoricoContaPagar.objects.create(
        conta_pagar=conta,
        tipo_evento=HistoricoContaPagar.EVENTO_ESTORNO,
        descricao=(
            f"Baixa da parcela {parcela.numero} estornada. Motivo: {motivo}"
        ),
        dados={
            "baixa_id": baixa.pk,
            "movimentacao_original_id": movimentacao_original.pk,
            "parcela": parcela.numero,
            "valor": str(baixa.valor),
            "valor_movimentado": str(baixa.valor_movimentado),
            "motivo": motivo,
            "saldo_parcela": str(parcela.saldo),
            "saldo_conta": str(conta.saldo),
        },
        usuario=usuario,
    )

    return baixa


@transaction.atomic
def estornar_recebimento(*, recebimento, usuario, motivo):
    """Estorna um recebimento e registra a saída financeira inversa."""
    _validar_usuario(usuario)
    motivo = _validar_motivo(motivo)
    recebimento_id = (
        recebimento.pk
        if isinstance(recebimento, RecebimentoConta)
        else recebimento
    )

    recebimento = (
        RecebimentoConta.objects.select_for_update()
        .select_related("parcela__conta_receber", "conta_financeira")
        .get(pk=recebimento_id)
    )

    if recebimento.estornado:
        raise ValidationError("Este recebimento já foi estornado.")

    parcela = ParcelaReceber.objects.select_for_update().get(
        pk=recebimento.parcela_id
    )
    conta = ContaReceber.objects.select_for_update().get(
        pk=parcela.conta_receber_id
    )

    if conta.status == ContaReceber.STATUS_CANCELADA:
        raise ValidationError(
            "Não é possível estornar um recebimento de uma conta cancelada."
        )

    movimentacao_original = (
        recebimento.movimentacoes.select_for_update()
        .filter(
            tipo=MovimentacaoFinanceira.TIPO_ENTRADA,
            estornada=False,
        )
        .first()
    )

    if movimentacao_original is None:
        raise ValidationError(
            "A movimentação original deste recebimento não foi encontrada."
        )

    agora = timezone.now()

    MovimentacaoFinanceira.objects.create(
        conta_financeira=recebimento.conta_financeira,
        categoria=conta.categoria,
        recebimento_conta=recebimento,
        tipo=MovimentacaoFinanceira.TIPO_ESTORNO_ENTRADA,
        data_movimentacao=timezone.localdate(),
        valor=recebimento.valor_movimentado,
        descricao=(
            f"Estorno do recebimento da conta #{conta.numero} — "
            f"parcela {parcela.numero}"
        ),
        origem="estorno_conta_receber",
        criado_por=usuario,
    )

    recebimento.estornado = True
    recebimento.estornado_por = usuario
    recebimento.estornado_em = agora
    recebimento.motivo_estorno = motivo
    recebimento.save(
        update_fields=[
            "estornado",
            "estornado_por",
            "estornado_em",
            "motivo_estorno",
        ]
    )

    parcela.valor_recebido = max(
        parcela.valor_recebido - recebimento.valor,
        0,
    )
    parcela.status = ParcelaReceber.STATUS_PENDENTE
    parcela.save(
        update_fields=["valor_recebido", "status", "atualizado_em"]
    )
    _atualizar_conta_receber(conta)

    HistoricoContaReceber.objects.create(
        conta_receber=conta,
        tipo_evento=HistoricoContaReceber.EVENTO_ESTORNO,
        descricao=(
            f"Recebimento da parcela {parcela.numero} estornado. "
            f"Motivo: {motivo}"
        ),
        dados={
            "recebimento_id": recebimento.pk,
            "movimentacao_original_id": movimentacao_original.pk,
            "parcela": parcela.numero,
            "valor": str(recebimento.valor),
            "valor_movimentado": str(recebimento.valor_movimentado),
            "motivo": motivo,
            "saldo_parcela": str(parcela.saldo),
            "saldo_conta": str(conta.saldo),
        },
        usuario=usuario,
    )

    return recebimento
