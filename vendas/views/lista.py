from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render

from vendas.models import Venda


@login_required
def lista_vendas(request):
    busca = request.GET.get("busca", "").strip()

    vendas = (
        Venda.objects
        .select_related(
            "cliente",
            "criada_por",
        )
        .order_by("-numero")
    )

    if busca:
        filtros = (
            Q(cliente__nome_fantasia__icontains=busca)
            | Q(cliente__razao_social__icontains=busca)
        )

        if busca.isdigit():
            filtros |= Q(numero=int(busca))

        vendas = vendas.filter(filtros)

    return render(
        request,
        "vendas/lista.html",
        {
            "vendas": vendas,
            "busca": busca,
        },
    )