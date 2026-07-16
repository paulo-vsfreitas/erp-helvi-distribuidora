from django.db import transaction
from django.db.models import Q

from financeiro.models import CategoriaFinanceira


def listar_categorias_financeiras(
    busca="",
    tipo="",
    status="ativas",
):
    categorias = CategoriaFinanceira.objects.all()

    busca = (busca or "").strip()
    tipo = (tipo or "").strip()
    status = (status or "ativas").strip()

    if busca:
        categorias = categorias.filter(
            Q(nome__icontains=busca)
            | Q(descricao__icontains=busca)
        )

    if tipo in {
        CategoriaFinanceira.TIPO_RECEITA,
        CategoriaFinanceira.TIPO_DESPESA,
    }:
        categorias = categorias.filter(tipo=tipo)

    if status == "ativas":
        categorias = categorias.filter(ativo=True)
    elif status == "inativas":
        categorias = categorias.filter(ativo=False)

    return categorias.order_by("tipo", "nome")


@transaction.atomic
def salvar_categoria_financeira(form):
    return form.save()


@transaction.atomic
def inativar_categoria_financeira(categoria):
    if not categoria.ativo:
        raise ValueError("Esta categoria já está inativa.")

    categoria.ativo = False
    categoria.save(update_fields=["ativo", "data_atualizacao"])

    return categoria


@transaction.atomic
def reativar_categoria_financeira(categoria):
    if categoria.ativo:
        raise ValueError("Esta categoria já está ativa.")

    categoria.ativo = True
    categoria.save(update_fields=["ativo", "data_atualizacao"])

    return categoria