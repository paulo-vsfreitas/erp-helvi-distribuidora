from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta

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
from core.services.relatorio_exportacao_service import exportar_csv, exportar_pdf


@login_required
def relatorio_vendas(request):
    parametros_entrada = request.GET.copy()
    periodo_rapido = parametros_entrada.get("periodo")
    hoje = timezone.localdate()
    periodos = {
        "hoje": (hoje, hoje), "7d": (hoje - timedelta(days=6), hoje),
        "30d": (hoje - timedelta(days=29), hoje), "90d": (hoje - timedelta(days=89), hoje),
        "mes": (hoje.replace(day=1), hoje), "ano": (hoje.replace(month=1, day=1), hoje),
    }
    if periodo_rapido in periodos:
        inicio, fim = periodos[periodo_rapido]
        parametros_entrada["data_inicial"] = inicio.isoformat()
        parametros_entrada["data_final"] = fim.isoformat()

    form = RelatorioVendasFiltroForm(
        parametros_entrada or None,
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

    periodo = "Todo o período"
    if filtros.get("data_inicial") or filtros.get("data_final"):
        periodo = f"{filtros.get('data_inicial') or 'início'} a {filtros.get('data_final') or 'hoje'}"

    if request.GET.get("exportar") in {"csv", "pdf"}:
        relatorio_exportacao = {
            "titulo": "Relatório de vendas",
            "subtitulo": "Desempenho comercial, recebimentos e produtos vendidos.",
            "colunas": ["Número", "Data", "Cliente", "Vendedor", "Pagamento", "Status", "Peças", "Total", "Recebido", "Saldo"],
            "kpis": kpis,
            "linhas": [
                {"valores": [
                    f"#{venda.numero:06d}", venda.data_venda.strftime("%d/%m/%Y %H:%M"),
                    str(venda.cliente or "Consumidor Final"),
                    str(venda.finalizada_por or venda.criada_por or "—"),
                    venda.get_forma_pagamento_display() or "—",
                    venda.get_status_pagamento_display(), venda.total_pecas,
                    f"R$ {venda.total:.2f}", f"R$ {venda.valor_recebido:.2f}", f"R$ {venda.saldo_receber:.2f}",
                ]}
                for venda in vendas
            ],
        }
        if request.GET["exportar"] == "csv":
            return exportar_csv(relatorio_exportacao, "vendas")
        return exportar_pdf(relatorio_exportacao, "vendas", periodo)

    por_pagina = request.GET.get("por_pagina", "25")
    if por_pagina not in {"25", "50", "100"}:
        por_pagina = "25"

    paginator = Paginator(
        vendas,
        int(por_pagina),
    )

    pagina = paginator.get_page(
        request.GET.get("pagina"),
    )

    parametros = request.GET.copy()
    parametros.pop("pagina", None)

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
            "querystring": parametros.urlencode(),
            "periodo_texto": periodo,
            "periodo_rapido": periodo_rapido,
            "por_pagina": por_pagina,
            "filtros_ativos": sum(
                bool(filtros.get(campo))
                for campo in (
                    "data_inicial", "data_final", "cliente", "vendedor",
                    "forma_pagamento", "status", "status_pagamento",
                    "consumidor_final",
                )
            ),
        },
    )
