from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404, render

from comercial.models import Orcamento


@login_required
def ficha_orcamento(request, numero):
    orcamento = get_object_or_404(
        Orcamento.objects
        .select_related(
            "cliente",
            "vendedor",
        )
        .prefetch_related(
            "itens__produto",
            "itens__produto__marca",
        ),
        numero=numero,
    )

    resumo_itens = orcamento.itens.aggregate(
        quantidade_pecas=Sum("quantidade"),
    )

    contexto = {
        "orcamento": orcamento,
        "quantidade_itens": orcamento.itens.count(),
        "quantidade_pecas": resumo_itens["quantidade_pecas"] or 0,
    }

    return render(
        request,
        "comercial/ficha_orcamento.html",
        contexto,
    )