from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from estoque.models import MovimentacaoEstoque
from financeiro.models import (
    ContaReceber,
    HistoricoContaReceber,
    MovimentacaoFinanceira,
    ParcelaReceber,
    RecebimentoConta,
)
from produtos.models import Produto, VariacaoCor
from vendas.models import Venda


@transaction.atomic
def cancelar_venda(*, venda, usuario, motivo):
    """Cancela a venda e reverte estoque e financeiro atomicamente."""

    if not usuario or not usuario.is_authenticated:
        raise ValidationError(
            "Não foi possível identificar o usuário responsável."
        )

    motivo = (motivo or "").strip()

    if len(motivo) < 5:
        raise ValidationError(
            "O motivo do cancelamento deve possuir pelo menos 5 caracteres."
        )

    venda_id = venda.pk if isinstance(venda, Venda) else venda
    venda = (
        Venda.objects
        .select_for_update()
        .prefetch_related("itens")
        .get(pk=venda_id)
    )

    if venda.status == Venda.STATUS_CANCELADA:
        raise ValidationError("Esta venda já foi cancelada.")

    if venda.estoque_baixado:
        _estornar_estoque(
            venda=venda,
            usuario=usuario,
            motivo=motivo,
        )

    _cancelar_financeiro(
        venda=venda,
        usuario=usuario,
        motivo=motivo,
    )

    venda.status = Venda.STATUS_CANCELADA
    venda.status_pagamento = Venda.PAGAMENTO_PENDENTE
    venda.valor_recebido = Decimal("0.00")
    venda.valor_troco = Decimal("0.00")
    venda.estoque_baixado = False
    venda.cancelada_por = usuario
    venda.cancelada_em = timezone.now()
    venda.motivo_cancelamento = motivo
    venda.save(
        update_fields=[
            "status",
            "status_pagamento",
            "valor_recebido",
            "valor_troco",
            "estoque_baixado",
            "cancelada_por",
            "cancelada_em",
            "motivo_cancelamento",
        ]
    )

    return venda


def _estornar_estoque(*, venda, usuario, motivo):
    itens = list(venda.itens.all())
    produto_ids = [item.produto_id for item in itens]
    produtos = {
        produto.pk: produto
        for produto in (
            Produto.objects
            .select_for_update()
            .filter(pk__in=produto_ids)
        )
    }
    variacoes = {
        cor.pk: cor
        for cor in VariacaoCor.objects.select_for_update().filter(
            pk__in=[item.variacao_cor_id for item in itens if item.variacao_cor_id]
        )
    }

    if len(produtos) != len(set(produto_ids)):
        raise ValidationError(
            "Não foi possível localizar todos os produtos da venda."
        )

    for item in itens:
        produto = produtos[item.produto_id]
        if item.variacao_cor_id:
            cor = variacoes[item.variacao_cor_id]
            cor.estoque += item.quantidade
            cor.save(update_fields=["estoque"])
        saldo_anterior = produto.estoque_atual or 0
        saldo_atual = saldo_anterior + item.quantidade

        produto.estoque_atual = saldo_atual
        produto.save(update_fields=["estoque_atual"])

        MovimentacaoEstoque.objects.create(
            produto=produto,
            variacao_cor_id=item.variacao_cor_id,
            tipo="cancelamento_venda",
            quantidade=item.quantidade,
            saldo_anterior=saldo_anterior,
            saldo_atual=saldo_atual,
            usuario=usuario,
            origem=f"Venda nº {venda.numero}",
            local="Estoque principal",
            observacao=(
                f"Estorno automático pelo cancelamento da venda "
                f"nº {venda.numero}. Motivo: {motivo}"
            ),
        )


def _cancelar_financeiro(*, venda, usuario, motivo):
    conta = (
        ContaReceber.objects
        .select_for_update()
        .filter(
            origem=ContaReceber.ORIGEM_VENDA,
            origem_id=venda.pk,
        )
        .first()
    )

    if conta is None:
        if venda.financeiro_gerado or venda.valor_recebido > 0:
            raise ValidationError(
                "A integração financeira da venda não foi encontrada. "
                "Concilie a venda antes de cancelá-la."
            )
        return

    recebimentos = list(
        RecebimentoConta.objects
        .select_for_update()
        .filter(
            parcela__conta_receber=conta,
            estornado=False,
        )
    )
    agora = timezone.now()

    for recebimento in recebimentos:
        MovimentacaoFinanceira.objects.filter(
            recebimento_conta=recebimento,
            estornada=False,
        ).update(estornada=True)

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

    conta.parcelas.select_for_update().exclude(
        status=ParcelaReceber.STATUS_CANCELADA,
    ).update(
        valor_recebido=Decimal("0.00"),
        status=ParcelaReceber.STATUS_CANCELADA,
    )

    conta.valor_recebido = Decimal("0.00")
    conta.status = ContaReceber.STATUS_CANCELADA
    conta.cancelado_por = usuario
    conta.cancelado_em = agora
    conta.motivo_cancelamento = motivo
    conta.save(
        update_fields=[
            "valor_recebido",
            "status",
            "cancelado_por",
            "cancelado_em",
            "motivo_cancelamento",
            "atualizado_em",
        ]
    )

    HistoricoContaReceber.objects.create(
        conta_receber=conta,
        tipo_evento=HistoricoContaReceber.EVENTO_CANCELAMENTO,
        descricao=(
            f"Conta cancelada automaticamente devido ao cancelamento "
            f"da venda nº {venda.numero}."
        ),
        dados={
            "venda_id": venda.pk,
            "venda_numero": venda.numero,
            "motivo": motivo,
            "recebimentos_estornados": len(recebimentos),
        },
        usuario=usuario,
    )
