from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from financeiro.forms import CategoriaFinanceiraForm
from financeiro.models import CategoriaFinanceira
from financeiro.services.categoria_service import (
    inativar_categoria_financeira,
    listar_categorias_financeiras,
    reativar_categoria_financeira,
    salvar_categoria_financeira,
)
from usuarios.decorators import perfil_requerido


@login_required
@perfil_requerido("ADM", "GER", "FIN")
def lista_categorias(request):
    busca = request.GET.get("busca", "")
    tipo = request.GET.get("tipo", "")
    status = request.GET.get("status", "ativas")

    categorias = listar_categorias_financeiras(
        busca=busca,
        tipo=tipo,
        status=status,
    )

    contexto = {
        "categorias": categorias,
        "busca": busca,
        "tipo_selecionado": tipo,
        "status_selecionado": status,
        "tipos": CategoriaFinanceira.TIPO_CHOICES,
    }

    return render(
        request,
        "financeiro/lista_categorias.html",
        contexto,
    )


@login_required
@perfil_requerido("ADM", "GER", "FIN")
def nova_categoria(request):
    if request.method == "POST":
        form = CategoriaFinanceiraForm(request.POST)

        if form.is_valid():
            salvar_categoria_financeira(form)

            messages.success(
                request,
                "Categoria financeira cadastrada com sucesso.",
            )

            return redirect("financeiro:lista_categorias")
    else:
        form = CategoriaFinanceiraForm()

    return render(
        request,
        "financeiro/form_categoria.html",
        {
            "form": form,
            "titulo": "Nova categoria financeira",
            "subtitulo": (
                "Cadastre uma categoria para classificar "
                "receitas e despesas."
            ),
        },
    )


@login_required
@perfil_requerido("ADM", "GER", "FIN")
def editar_categoria(request, pk):
    categoria = get_object_or_404(
        CategoriaFinanceira,
        pk=pk,
    )

    if request.method == "POST":
        form = CategoriaFinanceiraForm(
            request.POST,
            instance=categoria,
        )

        if form.is_valid():
            salvar_categoria_financeira(form)

            messages.success(
                request,
                "Categoria financeira atualizada com sucesso.",
            )

            return redirect("financeiro:lista_categorias")
    else:
        form = CategoriaFinanceiraForm(instance=categoria)

    return render(
        request,
        "financeiro/form_categoria.html",
        {
            "form": form,
            "categoria": categoria,
            "titulo": "Editar categoria financeira",
            "subtitulo": (
                "Atualize os dados da categoria selecionada."
            ),
        },
    )


@login_required
@perfil_requerido("ADM", "GER", "FIN")
def inativar_categoria(request, pk):
    categoria = get_object_or_404(
        CategoriaFinanceira,
        pk=pk,
    )

    if request.method != "POST":
        return redirect("financeiro:lista_categorias")

    try:
        inativar_categoria_financeira(categoria)
        messages.success(
            request,
            "Categoria financeira inativada com sucesso.",
        )
    except ValueError as erro:
        messages.warning(request, str(erro))

    return redirect("financeiro:lista_categorias")


@login_required
@perfil_requerido("ADM", "GER", "FIN")
def reativar_categoria(request, pk):
    categoria = get_object_or_404(
        CategoriaFinanceira,
        pk=pk,
    )

    if request.method != "POST":
        return redirect("financeiro:lista_categorias")

    try:
        reativar_categoria_financeira(categoria)
        messages.success(
            request,
            "Categoria financeira reativada com sucesso.",
        )
    except ValueError as erro:
        messages.warning(request, str(erro))

    return redirect("financeiro:lista_categorias")