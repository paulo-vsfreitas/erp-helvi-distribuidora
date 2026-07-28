from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render

from vendas.forms.relatorio_vendas import (
    RelatorioVendasFiltroForm,
)
from vendas.services.relatorio_vendas_service import (
    calcular_indicadores_relatorio,
    montar_kpis_relatorio_vendas,
    obter_produtos_mais_vendidos,
    obter_resumo_formas_pagamento,
    obter_resumo_status_pagamento,
    obter_vendas_filtradas,
    
)


@login_required
def relatorio_vendas(request):
    form = RelatorioVendasFiltroForm(
        request.GET or None,
    )

    filtros = {}

    if form.is_valid():
        filtros = form.cleaned_data

    vendas = obter_vendas_filtradas(
        filtros,
    )

    indicadores = calcular_indicadores_relatorio(
        vendas,
    )

    formas_pagamento = obter_resumo_formas_pagamento(
        vendas,
    )

    status_pagamento = obter_resumo_status_pagamento(
        vendas,
    )

    produtos_mais_vendidos = obter_produtos_mais_vendidos(
        vendas,
    )

    kpis = montar_kpis_relatorio_vendas(
    indicadores,
    )

    paginator = Paginator(
        vendas,
        20,
    )

    pagina = paginator.get_page(
        request.GET.get("pagina"),
    )

    return render(
        request,
        "vendas/relatorios/vendas.html",
        {
            "form": form,
            "pagina": pagina,
            "indicadores": indicadores,
            "kpis": kpis,
            "formas_pagamento": formas_pagamento,
            "status_pagamento": status_pagamento,
            "produtos_mais_vendidos": produtos_mais_vendidos,
        },
    )