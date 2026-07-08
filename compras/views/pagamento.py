from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

from compras.forms import PagamentoCompraForm
from compras.models import Compra
from compras.services.pagamento_service import registrar_pagamento_compra


@login_required
def registrar_pagamento(request, pk):
    compra = get_object_or_404(Compra, pk=pk)

    if request.method != "POST":
        return redirect("compras:ficha", pk=compra.pk)

    form = PagamentoCompraForm(request.POST, compra=compra)

    if form.is_valid():
        registrar_pagamento_compra(compra=compra, form=form, usuario=request.user)
        messages.success(request, "Pagamento registrado com sucesso.")
    else:
        messages.error(request, "Não foi possível registrar o pagamento. Verifique o valor informado.")

    return redirect("compras:ficha", pk=compra.pk)