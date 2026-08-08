from django.core.exceptions import ValidationError
from django.db import transaction

from produtos.models import Produto, VariacaoCor


def obter_saldo(*, produto, variacao_cor=None):
    if variacao_cor is not None:
        return variacao_cor.estoque or 0

    return produto.estoque_atual or 0


@transaction.atomic
def sincronizar_estoque_produto(produto):
    produto = (
        Produto.objects
        .select_for_update()
        .get(pk=produto.pk)
    )

    variacoes = produto.variacoes_cor.all()

    if not variacoes.exists():
        return produto.estoque_atual or 0

    total = sum(
        variacao.estoque or 0
        for variacao in variacoes
    )

    if produto.estoque_atual != total:
        produto.estoque_atual = total
        produto.save(
            update_fields=["estoque_atual"]
        )

    return total


def validar_variacao_produto(*, produto, variacao_cor):
    if variacao_cor is None:
        return

    if variacao_cor.produto_id != produto.pk:
        raise ValidationError(
            "A variação selecionada não pertence ao produto."
        )


@transaction.atomic
def alterar_saldo(
    *,
    produto,
    quantidade,
    operacao,
    variacao_cor=None,
):
    if quantidade <= 0:
        raise ValidationError(
            "A quantidade deve ser maior que zero."
        )

    produto = (
        Produto.objects
        .select_for_update()
        .get(pk=produto.pk)
    )

    variacao = None

    if variacao_cor is not None:
        variacao = (
            VariacaoCor.objects
            .select_for_update()
            .get(pk=variacao_cor.pk)
        )

        validar_variacao_produto(
            produto=produto,
            variacao_cor=variacao,
        )

    if produto.variacoes_cor.exists() and variacao is None:
        raise ValidationError(
            "Selecione a Cor / Variação deste produto."
        )

    saldo_anterior = obter_saldo(
        produto=produto,
        variacao_cor=variacao,
    )

    if operacao == "entrada":
        saldo_atual = saldo_anterior + quantidade

    elif operacao == "saida":
        if quantidade > saldo_anterior:
            raise ValidationError(
                f"Estoque insuficiente. Disponível: {saldo_anterior}."
            )

        saldo_atual = saldo_anterior - quantidade

    else:
        raise ValidationError(
            "Operação de estoque inválida."
        )

    if variacao is not None:
        variacao.estoque = saldo_atual
        variacao.save(
            update_fields=["estoque"]
        )

        sincronizar_estoque_produto(produto)

    else:
        produto.estoque_atual = saldo_atual
        produto.save(
            update_fields=["estoque_atual"]
        )

    produto.refresh_from_db()

    return {
        "produto": produto,
        "variacao_cor": variacao,
        "saldo_anterior": saldo_anterior,
        "saldo_atual": saldo_atual,
        "estoque_total": produto.estoque_atual,
    }