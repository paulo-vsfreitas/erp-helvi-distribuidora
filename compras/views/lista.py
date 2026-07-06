from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.shortcuts import render

from compras.models import Compra


@login_required
def lista_compras(request):
    busca = request.GET.get("busca", "").strip()
    status = request.GET.get("status", "").strip()
    pagamento = request.GET.get("pagamento", "").strip()

    compras = Compra.objects.all().order_by("-data_compra", "-numero")

    if busca:
        compras = compras.filter(
            Q(numero__icontains=busca)
            | Q(fornecedor_nome__icontains=busca)
            | Q(fornecedor_documento__icontains=busca)
        )

    if status:
        compras = compras.filter(status=status)

    if pagamento:
        compras = compras.filter(status_pagamento=pagamento)

    paginator = Paginator(compras, 15)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "compras": page_obj,
        "page_obj": page_obj,
        "busca": busca,
        "status": status,
        "pagamento": pagamento,
        "status_choices": Compra.STATUS_CHOICES,
        "status_pagamento_choices": Compra.STATUS_PAGAMENTO_CHOICES,

        # Cards
        "total_compras": Compra.objects.count(),
        "valor_total": Compra.objects.aggregate(
            total=Sum("total")
        )["total"] or 0,

        "recebidas": Compra.objects.filter(
            status=Compra.STATUS_RECEBIDA
        ).count(),

        "pendentes": Compra.objects.exclude(
            status=Compra.STATUS_RECEBIDA
        ).count(),
    }

    return render(
        request,
        "compras/lista_compras.html",
        context,
    )