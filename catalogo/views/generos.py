from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from catalogo.forms import GeneroForm
from catalogo.models import Genero


@login_required
def lista_generos(request):
    busca = request.GET.get("busca", "")

    generos = Genero.objects.all().order_by("nome")

    if busca:
        generos = generos.filter(nome__icontains=busca)

    return render(
        request,
        "catalogo/generos/lista_generos.html",
        {
            "generos": generos,
            "busca": busca,
        },
    )


@login_required
def novo_genero(request):
    if request.method == "POST":
        form = GeneroForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Gênero cadastrado com sucesso.")
            return redirect("catalogo:lista_generos")
    else:
        form = GeneroForm()

    return render(
        request,
        "catalogo/generos/form_genero.html",
        {
            "form": form,
            "titulo": "Novo Gênero",
        },
    )


@login_required
def editar_genero(request, pk):
    genero = get_object_or_404(Genero, pk=pk)

    if request.method == "POST":
        form = GeneroForm(request.POST, instance=genero)

        if form.is_valid():
            form.save()
            messages.success(request, "Gênero atualizado com sucesso.")
            return redirect("catalogo:lista_generos")
    else:
        form = GeneroForm(instance=genero)

    return render(
        request,
        "catalogo/generos/form_genero.html",
        {
            "form": form,
            "titulo": "Editar Gênero",
            "genero": genero,
        },
    )


@login_required
def inativar_genero(request, pk):
    genero = get_object_or_404(Genero, pk=pk)

    if request.method == "POST":
        genero.ativo = False
        genero.save()
        messages.success(request, "Gênero inativado com sucesso.")
        return redirect("catalogo:lista_generos")

    return render(
        request,
        "catalogo/generos/confirmar_inativacao_genero.html",
        {
            "genero": genero,
        },
    )


@login_required
def reativar_genero(request, pk):
    genero = get_object_or_404(Genero, pk=pk)

    if request.method == "POST":
        genero.ativo = True
        genero.save()
        messages.success(request, "Gênero reativado com sucesso.")
        return redirect("catalogo:lista_generos")

    return render(
        request,
        "catalogo/generos/confirmar_reativacao_genero.html",
        {
            "genero": genero,
        },
    )