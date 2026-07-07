from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from compras.forms import CompraForm
from compras.models import Compra


@login_required
def editar_compra(request, pk):
    compra = get_object_or_404(Compra, pk=pk)

    if compra.entrada_estoque_realizada:
        messages.warning(
            request,
            "Esta compra já foi recebida no estoque e não pode ser editada.",
        )
        return redirect("compras:ficha", pk=compra.pk)

    form = CompraForm(request.POST or None, instance=compra)

    if request.method == "POST":
        if form.is_valid():
            compra = form.save()
            messages.success(request, f"Compra #{compra.numero} atualizada com sucesso.")
            return redirect("compras:ficha", pk=compra.pk)

        messages.error(request, "Não foi possível salvar. Verifique os campos do formulário.")

    return render(
        request,
        "compras/editar_compra.html",
        {
            "form": form,
            "compra": compra,
        },
    )