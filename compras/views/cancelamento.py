from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect

from compras.models import Compra
from compras.services.cancelamento_compra_service import cancelar_compra


@login_required
def cancelar_compra_view(request, pk):

    if request.method != "POST":
        return redirect("compras:ficha", pk=pk)

    compra = get_object_or_404(
        Compra,
        pk=pk,
    )

    motivo = request.POST.get(
        "motivo_cancelamento",
        "",
    )

    try:

        cancelar_compra(
            compra=compra,
            usuario=request.user,
            motivo=motivo,
        )

    except ValidationError as erro:

        messages.error(
            request,
            erro.message,
        )

    except Exception:

        messages.error(
            request,
            "Ocorreu um erro durante o cancelamento da compra.",
        )

    else:

        messages.success(
            request,
            "Compra cancelada com sucesso.",
        )

    return redirect(
        "compras:ficha",
        pk=pk,
    )