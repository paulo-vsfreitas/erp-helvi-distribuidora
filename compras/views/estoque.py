from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

from compras.models import Compra
from compras.services.recebimento_service import receber_compra


@login_required
def receber_compra_view(request, pk):
    compra = get_object_or_404(Compra, pk=pk)

    if request.method != "POST":
        return redirect("compras:ficha", pk=compra.pk)

    try:
        receber_compra(compra=compra, usuario=request.user)
        messages.success(request, f"Compra #{compra.numero} recebida e estoque atualizado com sucesso.")

    except ValueError as erro:
        messages.error(request, erro)

    return redirect("compras:ficha", pk=compra.pk)