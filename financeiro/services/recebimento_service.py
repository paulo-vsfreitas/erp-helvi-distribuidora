from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum

from financeiro.models import (
    ContaFinanceira,
    ContaReceber,
    HistoricoContaReceber,
    MovimentacaoFinanceira,
    ParcelaReceber,
    RecebimentoConta,
)


def _normalizar_decimal(valor, padrao="0.00"):
    if valor in (None, ""):
        return Decimal(padrao)

    if isinstance(valor, Decimal):
        return valor

    return Decimal(str(valor))


def _validar_recebimento(
    *,
    parcela,
    conta_financeira,
    valor,
    juros,
    multa,
    desconto,
):
    conta = parcela.conta_receber

    if conta.status == ContaReceber.STATUS_CANCELADA:
        raise ValidationError(
            "Não é possível registrar recebimento em uma conta cancelada."
        )

    if parcela.status == ParcelaReceber.STATUS_CANCELADA:
        raise ValidationError(
            "Não é possível registrar recebimento em uma parcela cancelada."
        )

    if parcela.status == ParcelaReceber.STATUS_RECEBIDA:
        raise ValidationError(
            "Esta parcela já foi totalmente recebida."
        )

    if parcela.saldo <= 0:
        raise ValidationError(
            "Esta parcela não possui saldo disponível."
        )

    if not conta_financeira.ativo:
        raise ValidationError(
            "A conta financeira selecionada está inativa."
        )

    if valor <= 0:
        raise ValidationError(
            "O valor recebido deve ser maior que zero."
        )

    if juros < 0:
        raise ValidationError(
            "Os juros não podem ser negativos."
        )

    if multa < 0:
        raise ValidationError(
            "A multa não pode ser negativa."
        )

    if desconto < 0:
        raise ValidationError(
            "O desconto não pode ser negativo."
        )

    if valor > parcela.saldo:
        raise ValidationError(
            (
                "O valor informado é maior que o saldo da parcela "
                f"(R$ {parcela.saldo:.2f})."
            )
        )

    valor_movimentado = valor + juros + multa - desconto

    if valor_movimentado <= 0:
        raise ValidationError(
            "O valor movimentado deve ser maior que zero."
        )


def _atualizar_valores_da_conta(conta):
    total_recebido = (
        conta.parcelas.aggregate(
            total=Sum("valor_recebido")
        )["total"]
        or Decimal("0.00")
    )

    conta.valor_recebido = total_recebido
    conta.atualizar_status()

    conta.save(
        update_fields=[
            "valor_recebido",
            "status",
            "atualizado_em",
        ]
    )


@transaction.atomic
def registrar_recebimento(
    *,
    parcela,
    conta_financeira,
    data_recebimento,
    valor,
    juros=Decimal("0.00"),
    multa=Decimal("0.00"),
    desconto=Decimal("0.00"),
    forma_recebimento,
    observacao="",
    usuario,
):
    parcela = (
        ParcelaReceber.objects
        .select_for_update()
        .select_related(
            "conta_receber",
        )
        .get(pk=parcela.pk)
    )

    conta = parcela.conta_receber

    conta_financeira = ContaFinanceira.objects.select_for_update().get(
        pk=conta_financeira.pk
    )

    valor = _normalizar_decimal(valor)
    juros = _normalizar_decimal(juros)
    multa = _normalizar_decimal(multa)
    desconto = _normalizar_decimal(desconto)

    _validar_recebimento(
        parcela=parcela,
        conta_financeira=conta_financeira,
        valor=valor,
        juros=juros,
        multa=multa,
        desconto=desconto,
    )

    recebimento = RecebimentoConta.objects.create(
        parcela=parcela,
        conta_financeira=conta_financeira,
        data_recebimento=data_recebimento,
        valor=valor,
        juros=juros,
        multa=multa,
        desconto=desconto,
        forma_recebimento=forma_recebimento,
        observacao=observacao,
        registrado_por=usuario,
    )

    MovimentacaoFinanceira.objects.create(
        conta_financeira=conta_financeira,
        categoria=conta.categoria,
        recebimento_conta=recebimento,
        tipo=MovimentacaoFinanceira.TIPO_ENTRADA,
        data_movimentacao=data_recebimento,
        valor=recebimento.valor_movimentado,
        descricao=(
            f"Recebimento da Conta #{conta.numero} "
            f"- Parcela {parcela.numero}"
        ),
        origem="conta_receber",
        criado_por=usuario,
    )

    parcela.valor_recebido += valor
    parcela.atualizar_status()

    parcela.save(
        update_fields=[
            "valor_recebido",
            "status",
            "atualizado_em",
        ]
    )

    _atualizar_valores_da_conta(conta)

    if conta.status == ContaReceber.STATUS_RECEBIDA:
        descricao = (
            "Conta totalmente recebida. "
            f"Parcela {parcela.numero} quitada."
        )

    elif parcela.status == ParcelaReceber.STATUS_RECEBIDA:
        descricao = (
            f"Parcela {parcela.numero} quitada."
        )

    else:
        descricao = (
            "Recebimento parcial registrado "
            f"na parcela {parcela.numero}."
        )

    HistoricoContaReceber.objects.create(
        conta_receber=conta,
        tipo_evento=HistoricoContaReceber.EVENTO_RECEBIMENTO,
        descricao=descricao,
        dados={
            "parcela": parcela.numero,
            "recebimento_id": recebimento.id,
            "valor": str(valor),
            "juros": str(juros),
            "multa": str(multa),
            "desconto": str(desconto),
            "valor_movimentado": str(
                recebimento.valor_movimentado
            ),
            "saldo_parcela": str(parcela.saldo),
            "saldo_conta": str(conta.saldo),
            "conta_financeira": conta_financeira.nome,
            "forma_recebimento": (
                recebimento.get_forma_recebimento_display()
            ),
            "data_recebimento": data_recebimento.isoformat(),
        },
        usuario=usuario,
    )

    return recebimentoq213