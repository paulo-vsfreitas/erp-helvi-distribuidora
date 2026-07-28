from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from vendas.models import Venda


@login_required
def ficha_venda(request, numero):
    venda = get_object_or_404(
        Venda.objects
        .select_related(
            "cliente",
            "criada_por",
            "finalizada_por",
            "cancelada_por",
        )
        .prefetch_related(
            "itens__produto",
            "itens__produto__marca",
            "itens__produto__colecao",
        ),
        numero=numero,
    )

    return render(
        request,
        "vendas/ficha.html",
        {
            "venda": venda,
        },
    )