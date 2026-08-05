from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from estoque.models import MovimentacaoEstoque
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
    variacoes = {
        cor.pk: cor
        for cor in VariacaoCor.objects.select_for_update().filter(
            pk__in=[item.variacao_cor_id for item in itens if item.variacao_cor_id]
        )
    }

    erros_estoque = []

    for item in itens:
        produto = produtos.get(item.produto_id)

        if produto is None:
            erros_estoque.append(
                f"O produto do item {item.pk} não foi encontrado."
            )
            continue

        estoque_atual = (
            variacoes[item.variacao_cor_id].estoque
            if item.variacao_cor_id else produto.estoque_atual or 0
        )

        if estoque_atual < item.quantidade:
            erros_estoque.append(
                f"{produto}: estoque disponível "
                f"{estoque_atual}, quantidade vendida "
                f"{item.quantidade}."
            )

    if erros_estoque:
        raise ValidationError(
            [
                "Estoque insuficiente para finalizar a venda:",
                *erros_estoque,
            ]
        )

    if not venda.estoque_baixado:
        for item in itens:
            produto = produtos[item.produto_id]

            # O custo definitivo pertence ao momento da finalização. Depois
            # disso, alterações no cadastro do produto não mudam o histórico.
            if item.custo_unitario != produto.preco_custo:
                item.custo_unitario = produto.preco_custo
                item.save(update_fields=["custo_unitario"])

            if item.variacao_cor_id:
                cor = variacoes[item.variacao_cor_id]
                cor.estoque -= item.quantidade
                cor.save(update_fields=["estoque"])

            saldo_anterior = produto.estoque_atual or 0
            saldo_atual = (
                saldo_anterior - item.quantidade
            )

            MovimentacaoEstoque.objects.create(
                produto=produto,
                variacao_cor_id=item.variacao_cor_id,
                tipo="venda",
                quantidade=item.quantidade,
                saldo_anterior=saldo_anterior,
                saldo_atual=saldo_atual,
                usuario=usuario,
                origem=f"Venda nº {venda.numero}",
                local="Estoque principal",
                observacao=(
                    "Saída automática referente à "
                    f"venda nº {venda.numero}."
                ),
            )

            produto.estoque_atual = saldo_atual

            produto.save(
                update_fields=["estoque_atual"]
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
