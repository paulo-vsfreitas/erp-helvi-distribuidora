from django.core.exceptions import ValidationError
from django.db import transaction

from estoque.models import MovimentacaoEstoque


@transaction.atomic
def registrar_entrada_estoque(
    produto,
    quantidade,
    usuario=None,
    origem=None,
    local="Estoque Principal",
    observacao=None,
):
    if quantidade <= 0:
        raise ValidationError("A quantidade da entrada deve ser maior que zero.")

    saldo_anterior = produto.estoque_atual
    saldo_atual = saldo_anterior + quantidade

    MovimentacaoEstoque.objects.create(
        produto=produto,
        tipo="entrada",
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