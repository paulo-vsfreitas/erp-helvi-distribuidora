from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from estoque.forms.inventarios import InventarioForm
from estoque.models import Inventario
from estoque.services.inventarios import (
    criar_inventario,
    salvar_conferencia_inventario,
    finalizar_inventario,
)


@login_required
def novo_inventario(request):
    if request.method == "POST":
        form = InventarioForm(request.POST)

        if form.is_valid():
            inventario = criar_inventario(
                usuario=request.user,
                observacao=form.cleaned_data["observacao"],
            )

            messages.success(request, "Inventário criado com sucesso.")
            return redirect("estoque:conferir_inventario", pk=inventario.pk)
    else:
        form = InventarioForm()

    return render(
        request,
        "estoque/inventarios/novo.html",
        {
            "form": form,
        },
    )


@login_required
def conferir_inventario(request, pk):
    inventario = get_object_or_404(
        Inventario.objects.prefetch_related("itens__produto"),
        pk=pk,
    )

    if request.method == "POST":
        salvar_conferencia_inventario(
            inventario=inventario,
            dados=request.POST,
        )

        messages.success(request, "Conferência salva com sucesso.")
        return redirect("estoque:conferir_inventario", pk=inventario.pk)

    return render(
        request,
        "estoque/inventarios/conferir.html",
        {
            "inventario": inventario,
        },
    )


@login_required
def finalizar_inventario_view(request, pk):
    inventario = get_object_or_404(Inventario, pk=pk)

    if request.method == "POST":
        finalizar_inventario(
            inventario=inventario,
            usuario=request.user,
        )

        messages.success(
            request,
            "Inventário finalizado e estoque ajustado com sucesso.",
        )

    return redirect("estoque:conferir_inventario", pk=inventario.pk)