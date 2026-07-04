from django.core.exceptions import ValidationError
from django.db import transaction

from estoque.models import MovimentacaoEstoque


@transaction.atomic
def registrar_saida_estoque(
    produto,
    quantidade,
    usuario=None,
    origem=None,
    local="Estoque Principal",
    observacao=None,
):
    if quantidade <= 0:
        raise ValidationError(
            "A quantidade da saída deve ser maior que zero."
        )

    if quantidade > produto.estoque_atual:
        raise ValidationError(
            f"Estoque insuficiente. Disponível: {produto.estoque_atual}."
        )

    saldo_anterior = produto.estoque_atual
    saldo_atual = saldo_anterior - quantidade

    MovimentacaoEstoque.objects.create(
        produto=produto,
        tipo="saida",
        quantidade=quantidade,
        saldo_anterior=saldo_anterior,
        saldo_atual=saldo_atual,
        usuario=usuario,
        origem=origem,
        local=local or "Estoque Principal",
        observacao=observacao,
    )

    produto.estoque_atual = saldo_atual
    produto.save(update_fields=["estoque_atual"])

    return produto
