from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

from comercial.models import Orcamento
from comercial.services import alterar_status_orcamento


@login_required
def alterar_status(request, numero, status):
    if request.method != "POST":
        return redirect("comercial:ficha", numero=numero)

    orcamento = get_object_or_404(
        Orcamento,
        numero=numero,
    )

    try:
        alterar_status_orcamento(
            orcamento,
            status,
        )

    except ValueError as erro:
        messages.error(request, str(erro))

    else:
        messages.success(
            request,
            "Status atualizado com sucesso.",
        )

    return redirect(
        "comercial:ficha",
        numero=numero,
    )