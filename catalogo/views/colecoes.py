from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from catalogo.models import Colecao
from catalogo.forms import ColecaoForm


@login_required
def lista_colecoes(request):
    busca = request.GET.get("busca", "")

    colecoes = Colecao.objects.all().order_by("nome")

    if busca:
        colecoes = colecoes.filter(nome__icontains=busca)

    return render(request, "catalogo/colecoes/lista_colecoes.html", {
        "colecoes": colecoes,
        "busca": busca,
    })


@login_required
def nova_colecao(request):
    if request.method == "POST":
        form = ColecaoForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Coleção cadastrada com sucesso.")
            return redirect("catalogo:lista_colecoes")
    else:
        form = ColecaoForm()

    return render(request, "catalogo/colecoes/form_colecao.html", {
        "form": form,
        "titulo": "Nova Coleção",
    })


@login_required
def editar_colecao(request, pk):
    colecao = get_object_or_404(Colecao, pk=pk)

    if request.method == "POST":
        form = ColecaoForm(request.POST, instance=colecao)

        if form.is_valid():
            form.save()
            messages.success(request, "Coleção atualizada com sucesso.")
            return redirect("catalogo:lista_colecoes")
    else:
        form = ColecaoForm(instance=colecao)

    return render(request, "catalogo/colecoes/form_colecao.html", {
        "form": form,
        "titulo": "Editar Coleção",
        "colecao": colecao,
    })


@login_required
def inativar_colecao(request, pk):
    colecao = get_object_or_404(Colecao, pk=pk)

    if request.method == "POST":
        colecao.ativo = False
        colecao.save()
        messages.success(request, "Coleção inativada com sucesso.")
        return redirect("catalogo:lista_colecoes")

    return render(request, "catalogo/colecoes/confirmar_inativacao_colecao.html", {
        "colecao": colecao,
    })


@login_required
def reativar_colecao(request, pk):
    colecao = get_object_or_404(Colecao, pk=pk)

    if request.method == "POST":
        colecao.ativo = True
        colecao.save()
        messages.success(request, "Coleção reativada com sucesso.")
        return redirect("catalogo:lista_colecoes")

    return render(request, "catalogo/colecoes/confirmar_reativacao_colecao.html", {
        "colecao": colecao,
    })