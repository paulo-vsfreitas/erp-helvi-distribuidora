from django.db import transaction
from django.db.models import Q

from financeiro.models import (
    CategoriaFinanceira,
    MovimentacaoFinanceira,
)


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
        categorias = categorias.filter(
            tipo=tipo
        )

    if status == "ativas":
        categorias = categorias.filter(
            ativo=True
        )

    elif status == "inativas":
        categorias = categorias.filter(
            ativo=False
        )

    return categorias.order_by(
        "tipo",
        "nome",
    )


def categoria_possui_movimentacoes(categoria):
    if not categoria or not categoria.pk:
        return False

    return MovimentacaoFinanceira.objects.filter(
        categoria_id=categoria.pk,
    ).exists()


@transaction.atomic
def salvar_categoria_financeira(form):
    categoria = form.save(commit=False)

    if categoria.pk:
        categoria_original = (
            CategoriaFinanceira.objects
            .select_for_update()
            .get(pk=categoria.pk)
        )

        tipo_foi_alterado = (
            categoria_original.tipo
            != categoria.tipo
        )

        if (
            tipo_foi_alterado
            and categoria_possui_movimentacoes(
                categoria_original
            )
        ):
            raise ValueError(
                "O tipo desta categoria não pode ser alterado, "
                "pois ela já foi utilizada em movimentações "
                "financeiras. O nome e a descrição ainda podem "
                "ser atualizados."
            )

    categoria.save()

    return categoria


@transaction.atomic
def inativar_categoria_financeira(categoria):
    categoria = (
        CategoriaFinanceira.objects
        .select_for_update()
        .get(pk=categoria.pk)
    )

    if not categoria.ativo:
        raise ValueError(
            "Esta categoria já está inativa."
        )

    categoria.ativo = False

    categoria.save(
        update_fields=[
            "ativo",
            "data_atualizacao",
        ]
    )

    return categoria


@transaction.atomic
def reativar_categoria_financeira(categoria):
    categoria = (
        CategoriaFinanceira.objects
        .select_for_update()
        .get(pk=categoria.pk)
    )

    if categoria.ativo:
        raise ValueError(
            "Esta categoria já está ativa."
        )

    categoria.ativo = True

    categoria.save(
        update_fields=[
            "ativo",
            "data_atualizacao",
        ]
    )

    return categoria