from django.core.exceptions import ValidationError
from django.db import transaction

from estoque.models import MovimentacaoEstoque
from estoque.services.saldos import alterar_saldo


@transaction.atomic
def registrar_saida_estoque(
    produto,
    quantidade,
    usuario=None,
    origem=None,
    local="Estoque Principal",
    observacao=None,
    variacao_cor=None,
):
    if quantidade <= 0:
        raise ValidationError(
            "A quantidade da saída deve ser maior que zero."
        )

    resultado = alterar_saldo(
        produto=produto,
        variacao_cor=variacao_cor,
        quantidade=quantidade,
        operacao="saida",
    )

    MovimentacaoEstoque.objects.create(
        produto=resultado["produto"],
        variacao_cor=resultado["variacao_cor"],
        tipo="saida",
        quantidade=quantidade,
        saldo_anterior=resultado["saldo_anterior"],
        saldo_atual=resultado["saldo_atual"],
        usuario=usuario,
        origem=origem,
        local=local or "Estoque Principal",
        observacao=observacao,
    )

    return resultado["produto"]