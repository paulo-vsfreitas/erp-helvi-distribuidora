from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from comercial.forms import VincularClienteForm
from comercial.models import Orcamento
from comercial.services.cliente_service import (
    vincular_cliente_ao_orcamento,
)


def vincular_cliente(request, numero):
    orcamento = get_object_or_404(
        Orcamento,
        numero=numero,
    )

    if request.method == "POST":
        form = VincularClienteForm(
            request.POST,
            instance=orcamento,
        )

        if form.is_valid():
            try:
                vincular_cliente_ao_orcamento(
                    orcamento=orcamento,
                    cliente=form.cleaned_data["cliente"],
                )

                messages.success(
                    request,
                    "Cliente vinculado ao orçamento com sucesso.",
                )

                return redirect(
                    "comercial:ficha",
                    numero=orcamento.numero,
                )

            except ValueError as erro:
                messages.error(request, str(erro))

    else:
        form = VincularClienteForm(instance=orcamento)

    return render(
        request,
        "comercial/orcamentos/vincular_cliente.html",
        {
            "orcamento": orcamento,
            "form": form,
        },
    )