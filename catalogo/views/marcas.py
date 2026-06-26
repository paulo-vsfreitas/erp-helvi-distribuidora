from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from catalogo.models import Marca
from catalogo.forms import MarcaForm


@login_required
def lista_marcas(request):
    busca = request.GET.get("busca", "")

    marcas = Marca.objects.all().order_by("nome")

    if busca:
        marcas = marcas.filter(nome__icontains=busca)

    return render(request, "catalogo/marcas/lista_marcas.html", {
        "marcas": marcas,
        "busca": busca,
    })


@login_required
def nova_marca(request):
    if request.method == "POST":
        form = MarcaForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("lista_marcas")
    else:
        form = MarcaForm()

    return render(request, "catalogo/marcas/form_marca.html", {
        "form": form,
        "titulo": "Nova Marca",
    })


@login_required
def editar_marca(request, pk):
    marca = get_object_or_404(Marca, pk=pk)

    if request.method == "POST":
        form = MarcaForm(request.POST, instance=marca)

        if form.is_valid():
            form.save()
            return redirect("lista_marcas")
    else:
        form = MarcaForm(instance=marca)

    return render(request, "catalogo/marcas/form_marca.html", {
        "form": form,
        "titulo": "Editar Marca",
    })


@login_required
def excluir_marca(request, pk):
    marca = get_object_or_404(Marca, pk=pk)

    if request.method == "POST":
        marca.delete()
        return redirect("lista_marcas")

    return render(request, "catalogo/marcas/confirmar_exclusao_marca.html", {
        "marca": marca,
    })