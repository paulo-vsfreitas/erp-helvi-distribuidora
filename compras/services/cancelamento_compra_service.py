from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from compras.models import Compra
from estoque.models import MovimentacaoEstoque
from financeiro.models import (
    ContaPagar,
    HistoricoContaPagar,
    ParcelaPagar,
)
from produtos.models import Produto


@transaction.atomic
def cancelar_compra(compra, usuario, motivo):
    """
    Cancela uma compra e realiza, de forma atômica:

    - validação das regras de negócio;
    - estorno do estoque, quando a compra já foi recebida;
    - criação das movimentações de cancelamento;
    - cancelamento da Conta a Pagar vinculada;
    - cancelamento das parcelas financeiras;
    - atualização dos dados de auditoria da compra.

    Se qualquer etapa falhar, nenhuma alteração será salva.
    """

    motivo = (motivo or "").strip()

    compra = (
        Compra.objects
        .select_for_update()
        .prefetch_related("itens__produto", "pagamentos")
        .get(pk=compra.pk)
    )

    _validar_cancelamento(
        compra=compra,
        motivo=motivo,
    )

    if compra.entrada_estoque_realizada:
        _estornar_estoque(
            compra=compra,
            usuario=usuario,
            motivo=motivo,
        )

    _cancelar_financeiro(
        compra=compra,
        usuario=usuario,
        motivo=motivo,
    )

    _atualizar_compra(
        compra=compra,
        usuario=usuario,
        motivo=motivo,
    )

    return compra


def _validar_cancelamento(compra, motivo):
    """
    Valida todas as condições antes de qualquer alteração.
    """

    if compra.status == Compra.STATUS_CANCELADA:
        raise ValidationError(
            "Esta compra já foi cancelada."
        )

    if not motivo:
        raise ValidationError(
            "Informe o motivo do cancelamento."
        )

    if len(motivo) < 5:
        raise ValidationError(
            "O motivo do cancelamento deve possuir pelo menos "
            "5 caracteres."
        )

    if compra.valor_pago > Decimal("0.00"):
        raise ValidationError(
            "Não é possível cancelar uma compra que possui "
            "pagamentos registrados."
        )

    if compra.pagamentos.exists():
        raise ValidationError(
            "Não é possível cancelar uma compra que possui "
            "pagamentos registrados."
        )

    conta_pagar = (
        ContaPagar.objects
        .select_for_update()
        .filter(compra=compra)
        .first()
    )

    if conta_pagar:
        if conta_pagar.status == ContaPagar.STATUS_CANCELADA:
            raise ValidationError(
                "A Conta a Pagar vinculada já está cancelada."
            )

        if conta_pagar.valor_pago > Decimal("0.00"):
            raise ValidationError(
                "Não é possível cancelar a compra porque a Conta "
                "a Pagar vinculada possui valor pago."
            )

        possui_baixa_ativa = conta_pagar.parcelas.filter(
            baixas__estornada=False,
        ).exists()

        if possui_baixa_ativa:
            raise ValidationError(
                "Não é possível cancelar a compra porque existem "
                "baixas financeiras ativas na Conta a Pagar."
            )

    if compra.entrada_estoque_realizada:
        _validar_estoque_para_estorno(compra)


def _validar_estoque_para_estorno(compra):
    """
    Garante que o estorno da compra não deixará estoque negativo.
    """

    erros = []

    for item in compra.itens.all():
        produto = item.produto
        estoque_atual = produto.estoque_atual or 0

        if estoque_atual < item.quantidade:
            erros.append(
                f"{produto}: saldo atual de {estoque_atual}, "
                f"mas são necessárias {item.quantidade} unidades."
            )

    if erros:
        raise ValidationError(
            "O cancelamento deixaria o estoque negativo:\n"
            + "\n".join(erros)
        )


def _estornar_estoque(compra, usuario, motivo):
    """
    Retira do estoque as quantidades que entraram pelo recebimento
    da compra e registra as movimentações de cancelamento.
    """

    itens = compra.itens.select_related("produto").all()

    for item in itens:
        produto = (
            Produto.objects
            .select_for_update()
            .get(pk=item.produto_id)
        )

        saldo_anterior = produto.estoque_atual or 0

        if saldo_anterior < item.quantidade:
            raise ValidationError(
                f"O produto {produto} não possui saldo suficiente "
                "para o estorno."
            )

        saldo_atual = saldo_anterior - item.quantidade

        produto.estoque_atual = saldo_atual
        produto.save(
            update_fields=[
                "estoque_atual",
            ]
        )

        MovimentacaoEstoque.objects.create(
            produto=produto,
            tipo="cancelamento_compra",
            quantidade=item.quantidade,
            saldo_anterior=saldo_anterior,
            saldo_atual=saldo_atual,
            usuario=usuario,
            origem=f"Compra #{compra.numero}",
            observacao=(
                f"Estorno de estoque pelo cancelamento da "
                f"compra #{compra.numero}. Motivo: {motivo}"
            ),
        )


def _cancelar_financeiro(compra, usuario, motivo):
    """
    Cancela a Conta a Pagar e suas parcelas quando houver
    integração financeira vinculada à compra.
    """

    conta_pagar = (
        ContaPagar.objects
        .select_for_update()
        .filter(compra=compra)
        .first()
    )

    if not conta_pagar:
        return

    conta_pagar.parcelas.exclude(
        status=ParcelaPagar.STATUS_CANCELADA,
    ).update(
        status=ParcelaPagar.STATUS_CANCELADA,
    )

    conta_pagar.status = ContaPagar.STATUS_CANCELADA
    conta_pagar.cancelado_por = usuario
    conta_pagar.cancelado_em = timezone.now()
    conta_pagar.motivo_cancelamento = motivo

    conta_pagar.save(
        update_fields=[
            "status",
            "cancelado_por",
            "cancelado_em",
            "motivo_cancelamento",
            "atualizado_em",
        ]
    )

    HistoricoContaPagar.objects.create(
        conta_pagar=conta_pagar,
        tipo_evento=HistoricoContaPagar.EVENTO_CANCELAMENTO,
        descricao=(
            f"Conta a Pagar cancelada automaticamente devido ao "
            f"cancelamento da compra #{compra.numero}."
        ),
        dados={
            "compra_id": compra.pk,
            "compra_numero": compra.numero,
            "motivo": motivo,
        },
        usuario=usuario,
    )


def _atualizar_compra(compra, usuario, motivo):
    """
    Atualiza o status e os dados de auditoria da compra.
    """

    compra.status = Compra.STATUS_CANCELADA
    compra.cancelada_em = timezone.now()
    compra.cancelada_por = usuario
    compra.motivo_cancelamento = motivo

    compra.save(
        update_fields=[
            "status",
            "cancelada_em",
            "cancelada_por",
            "motivo_cancelamento",
            "atualizado_em",
        ]
    )