from django.core.exceptions import ValidationError
from django.db import transaction

from estoque.models import MovimentacaoEstoque
from estoque.services.saldos import (
    alterar_saldo,
    obter_saldo,
)
from produtos.models import Produto, VariacaoCor


@transaction.atomic
def ajustar_estoque(
    produto,
    quantidade_correta,
    usuario=None,
    motivo=None,
    local="Estoque Principal",
    observacao=None,
    variacao_cor=None,
):
    if quantidade_correta < 0:
        raise ValidationError(
            "A quantidade correta não pode ser negativa."
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

        if variacao.produto_id != produto.pk:
            raise ValidationError(
                "A variação selecionada não pertence ao produto."
            )

    if (
        produto.variacoes_cor.exists()
        and variacao is None
    ):
        raise ValidationError(
            "Selecione a Cor / Variação deste produto."
        )

    saldo_anterior = obter_saldo(
        produto=produto,
        variacao_cor=variacao,
    )

    diferenca = (
        quantidade_correta
        - saldo_anterior
    )

    if diferenca == 0:
        raise ValidationError(
            "Nenhum ajuste necessário. "
            "A quantidade informada é igual "
            "ao estoque atual."
        )

    operacao = (
        "entrada"
        if diferenca > 0
        else "saida"
    )

    resultado = alterar_saldo(
        produto=produto,
        variacao_cor=variacao,
        quantidade=abs(diferenca),
        operacao=operacao,
    )

    tipo = (
        "ajuste_positivo"
        if diferenca > 0
        else "ajuste_negativo"
    )

    observacao_final = ""

    if motivo:
        observacao_final = (
            f"Motivo: {motivo}"
        )

    if observacao:
        if observacao_final:
            observacao_final += "\n\n"

        observacao_final += (
            f"Observação: {observacao}"
        )

    MovimentacaoEstoque.objects.create(
        produto=resultado["produto"],
        variacao_cor=resultado["variacao_cor"],
        tipo=tipo,
        quantidade=abs(diferenca),
        saldo_anterior=resultado["saldo_anterior"],
        saldo_atual=resultado["saldo_atual"],
        usuario=usuario,
        origem="Ajuste de Estoque",
        local=local or "Estoque Principal",
        observacao=observacao_final,
    )

    return resultado["produto"]