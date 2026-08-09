from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from estoque.models import MovimentacaoEstoque
from estoque.services.saldos import alterar_saldo
from produtos.models import Produto, VariacaoCor
from vendas.models import Venda
from vendas.services.processamento_pagamento_service import (
    processar_pagamento_venda,
)


@transaction.atomic
def finalizar_venda(
    *,
    venda_id,
    usuario,
):
    venda = (
        Venda.objects
        .select_for_update()
        .prefetch_related("itens")
        .get(pk=venda_id)
    )

    if venda.status == Venda.STATUS_CANCELADA:
        raise ValidationError(
            "Não é possível finalizar uma venda cancelada."
        )

    if venda.status == Venda.STATUS_FINALIZADA:
        raise ValidationError(
            "Esta venda já foi finalizada."
        )

    itens = list(venda.itens.all())

    if not itens:
        raise ValidationError(
            "A venda não possui produtos."
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

    if len(produtos) != len(set(produto_ids)):
        raise ValidationError(
            "Não foi possível localizar todos os produtos da venda."
        )

    for item in itens:
        produto = produtos[item.produto_id]

        if item.variacao_cor_id:
            variacao = variacoes.get(
                item.variacao_cor_id
            )

            if variacao is None:
                raise ValidationError(
                    "Não foi possível localizar a "
                    "Cor / Variação de um dos itens."
                )

            if variacao.produto_id != produto.pk:
                raise ValidationError(
                    "A Cor / Variação selecionada "
                    "não pertence ao produto."
                )

        elif produto.variacoes_cor.exists():
            raise ValidationError(
                f"Selecione a Cor / Variação "
                f"do produto {produto}."
            )

    if not venda.estoque_baixado:
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
                item.custo_unitario
                != produto.preco_custo
            ):
                item.custo_unitario = (
                    produto.preco_custo
                )

                item.save(
                    update_fields=[
                        "custo_unitario"
                    ]
                )

            try:
                resultado = alterar_saldo(
                    produto=produto,
                    variacao_cor=variacao,
                    quantidade=item.quantidade,
                    operacao="saida",
                )

            except ValidationError as erro:
                identificacao = str(produto)

                if variacao:
                    identificacao += (
                        f" / {variacao}"
                    )

                detalhe = (
                    erro.messages[0]
                    if erro.messages
                    else str(erro)
                )

                raise ValidationError(
                    f"{identificacao}: {detalhe}"
                )

            MovimentacaoEstoque.objects.create(
                produto=resultado[
                    "produto"
                ],
                variacao_cor=resultado[
                    "variacao_cor"
                ],
                tipo="venda",
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
                    "Saída automática referente "
                    f"à venda nº {venda.numero}."
                ),
            )

        venda.estoque_baixado = True

    processar_pagamento_venda(
        venda=venda,
        usuario=usuario,
        conta_financeira=venda.conta_financeira,
    )

    venda.status = Venda.STATUS_FINALIZADA
    venda.finalizada_por = usuario
    venda.finalizada_em = timezone.now()

    venda.save(
        update_fields=[
            "status",
            "estoque_baixado",
            "financeiro_gerado",
            "finalizada_por",
            "finalizada_em",
        ]
    )

    return venda