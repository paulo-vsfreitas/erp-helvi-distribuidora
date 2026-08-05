from django.db import transaction
from django.db.models import Sum


@transaction.atomic
def sincronizar_estoque_total(produto):
    if not produto.variacoes_cor.exists():
        return produto.estoque_atual
    total = produto.variacoes_cor.aggregate(total=Sum("estoque"))["total"] or 0
    if produto.estoque_atual != total:
        produto.estoque_atual = total
        produto.save(update_fields=["estoque_atual"])
    return total


@transaction.atomic
def salvar_produto_com_cores(form, formset):
    produto = form.save()
    formset.instance = produto
    formset.save()
    sincronizar_estoque_total(produto)
    return produto
