from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.shortcuts import render

from vendas.models import Venda


@login_required
def lista_vendas(request):
    busca = request.GET.get("busca", "").strip()
    status = request.GET.get("status", "").strip()
    pagamento = request.GET.get("pagamento", "").strip()

    status_validos = {valor for valor, _ in Venda.STATUS_CHOICES}
    pagamentos_validos = {valor for valor, _ in Venda.STATUS_PAGAMENTO_CHOICES}
    if status not in status_validos:
        status = ""
    if pagamento not in pagamentos_validos:
        pagamento = ""

    vendas = (
        Venda.objects
        .select_related(
            "cliente",
            "criada_por",
        )
        .order_by("-data_venda", "-numero")
    )

    if busca:
        filtros = (
            Q(cliente__nome_fantasia__icontains=busca)
            | Q(cliente__razao_social__icontains=busca)
        )

        numero_busca = busca.lstrip("#")
        if numero_busca.isdigit():
            filtros |= Q(numero=int(numero_busca))

        vendas = vendas.filter(filtros)

    if status:
        vendas = vendas.filter(status=status)

    if pagamento:
        vendas = vendas.filter(status_pagamento=pagamento)

    paginator = Paginator(vendas, 15)
    page_obj = paginator.get_page(request.GET.get("page"))

    vendas_finalizadas = Venda.objects.filter(status=Venda.STATUS_FINALIZADA)

    return render(
        request,
        "vendas/lista.html",
        {
            "vendas": page_obj,
            "page_obj": page_obj,
            "busca": busca,
            "status": status,
            "pagamento": pagamento,
            "status_choices": Venda.STATUS_CHOICES,
            "pagamento_choices": Venda.STATUS_PAGAMENTO_CHOICES,
            "total_vendas": Venda.objects.count(),
            "vendas_finalizadas": vendas_finalizadas.count(),
            "vendas_em_aberto": Venda.objects.filter(
                status=Venda.STATUS_EM_ABERTO
            ).count(),
            "faturamento": vendas_finalizadas.aggregate(total=Sum("total"))[
                "total"
            ]
            or 0,
        },
    )
