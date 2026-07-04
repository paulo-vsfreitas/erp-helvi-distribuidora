from django.core.exceptions import ValidationError
from django.db import transaction

from estoque.models import MovimentacaoEstoque


@transaction.atomic
def ajustar_estoque(
    produto,
    quantidade_correta,
    usuario=None,
    motivo=None,
    local="Estoque Principal",
    observacao=None,
):
    if quantidade_correta < 0:
        raise ValidationError(
            "A quantidade correta não pode ser negativa."
        )

    saldo_anterior = produto.estoque_atual
    saldo_atual = quantidade_correta
    diferenca = saldo_atual - saldo_anterior

    if diferenca == 0:
        raise ValidationError(
            "Nenhum ajuste necessário. A quantidade informada é igual ao estoque atual."
        )

    tipo = "ajuste_positivo" if diferenca > 0 else "ajuste_negativo"

    observacao_final = observacao or ""

    if motivo:
        observacao_final = f"Motivo: {motivo}"

        if observacao:
            observacao_final += f"\n\nObservação: {observacao}"

    MovimentacaoEstoque.objects.create(
        produto=produto,
        tipo=tipo,
        quantidade=abs(diferenca),
        saldo_anterior=saldo_anterior,
        saldo_atual=saldo_atual,
        usuario=usuario,
        origem="Ajuste de Estoque",
        local=local or "Estoque Principal",
        observacao=observacao_final,
    )

    produto.estoque_atual = saldo_atual
    produto.save(update_fields=["estoque_atual"])

    return produto
