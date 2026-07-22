from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from comercial.models import Orcamento
from comercial.services.conversao_service import (
    converter_orcamento_em_venda,
)


@require_POST
def converter_orcamento(request, numero):
    orcamento = get_object_or_404(
        Orcamento,
        numero=numero,
    )

    try:
        venda = converter_orcamento_em_venda(orcamento)

        messages.success(
            request,
            f"Orçamento convertido na Venda #{venda.id} com sucesso.",
        )

    except ValueError as erro:
        messages.error(request, str(erro))

    return redirect(
        "comercial:ficha",
        numero=orcamento.numero,
    )