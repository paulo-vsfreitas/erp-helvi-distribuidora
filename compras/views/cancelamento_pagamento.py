from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from compras.models import PagamentoCompra
from compras.services.cancelamento_pagamento_service import (
    cancelar_pagamento_compra,
)


@login_required
@require_POST
def cancelar_pagamento(request, pk):
    pagamento = get_object_or_404(
        PagamentoCompra,
        pk=pk,
    )

    compra = pagamento.compra

    try:
        cancelar_pagamento_compra(pagamento)

    except ValueError as erro:
        messages.error(
            request,
            str(erro),
        )

        return redirect(
            "compras:ficha",
            pk=compra.pk,
        )

    messages.success(
        request,
        "Pagamento cancelado com sucesso.",
    )

    return redirect(
        "compras:ficha",
        pk=compra.pk,
    )