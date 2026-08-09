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
from estoque.services.saldos import alterar_saldo


@transaction.atomic
def cancelar_venda(*, venda, usuario, autorizado_por, motivo):
    """Cancela a venda e reverte estoque e financeiro atomicamente."""

    if not usuario or not usuario.is_authenticated:
        raise ValidationError(
            "Não foi possível identificar o usuário responsável."
        )

    if not autorizado_por or not autorizado_por.is_authenticated or not (
        autorizado_por.is_superuser
        or autorizado_por.perfil == "ADM"
    ):
        raise ValidationError(
            "O cancelamento exige autorização de um administrador ativo."
        )

    if not autorizado_por.is_active:
        raise ValidationError(
            "O administrador informado está inativo."
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
        autorizado_por=autorizado_por,
        motivo=motivo,
    )

    venda.status = Venda.STATUS_CANCELADA
    venda.status_pagamento = Venda.PAGAMENTO_PENDENTE
    venda.valor_recebido = Decimal("0.00")
    venda.valor_troco = Decimal("0.00")
    venda.estoque_baixado = False
    venda.cancelada_por = usuario
    venda.cancelamento_autorizado_por = autorizado_por
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
            "cancelamento_autorizado_por",
            "cancelada_em",
            "motivo_cancelamento",
        ]
    )

    return venda


def _estornar_estoque(
    *,
    venda,
    usuario,
    motivo,
):
    itens = list(
        venda.itens.all()
    )

    produto_ids = [
        item.produto_id
        for item in itens
    ]

    produtos = {
        produto.pk: produto
        for produto in (
            Produto.objects
            .select_for_update()
            .filter(pk__in=produto_ids)
        )
    }

    variacao_ids = [
        item.variacao_cor_id
        for item in itens
        if item.variacao_cor_id
    ]

    variacoes = {
        variacao.pk: variacao
        for variacao in (
            VariacaoCor.objects
            .select_for_update()
            .filter(pk__in=variacao_ids)
        )
    }

    if len(produtos) != len(
        set(produto_ids)
    ):
        raise ValidationError(
            "Não foi possível localizar "
            "todos os produtos da venda."
        )

    for item in itens:
        produto = produtos[
            item.produto_id
        ]

        variacao = (
            variacoes.get(
                item.variacao_cor_id
            )
            if item.variacao_cor_id
            else None
        )

        if (
            item.variacao_cor_id
            and variacao is None
        ):
            raise ValidationError(
                "Não foi possível localizar a "
                "Cor / Variação de um dos itens."
            )

        resultado = alterar_saldo(
            produto=produto,
            variacao_cor=variacao,
            quantidade=item.quantidade,
            operacao="entrada",
        )

        MovimentacaoEstoque.objects.create(
            produto=resultado[
                "produto"
            ],
            variacao_cor=resultado[
                "variacao_cor"
            ],
            tipo="cancelamento_venda",
            quantidade=item.quantidade,
            saldo_anterior=resultado[
                "saldo_anterior"
            ],
            saldo_atual=resultado[
                "saldo_atual"
            ],
            usuario=usuario,
            origem=(
                f"Venda nº {venda.numero}"
            ),
            local="Estoque principal",
            observacao=(
                "Estorno automático pelo "
                "cancelamento da venda "
                f"nº {venda.numero}. "
                f"Motivo: {motivo}"
            ),
        )


def _cancelar_financeiro(*, venda, usuario, autorizado_por, motivo):
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
            "solicitado_por_id": usuario.pk,
            "autorizado_por_id": autorizado_por.pk,
        },
        usuario=usuario,
    )
