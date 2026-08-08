from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import redirect, render
from django.utils import timezone
from datetime import timedelta

from core.services.central_relatorios_service import (
    montar_central_relatorios,
)
from core.services.dashboard_service import (
    obter_contexto_dashboard,
)
from core.relatorio_forms import RelatorioAnaliticoFiltroForm
from core.services.relatorios_analiticos_service import (
    RELATORIOS,
    obter_relatorio_analitico,
    obter_status_relatorio,
)
from core.services.relatorio_exportacao_service import (
    PDF_OFICIAL,
    exportar_csv,
    exportar_pdf,
)
from core.services.operacao_service import (
    HELVI_DISTRIBUIDORA,
    USE_HELVI,
    definir_operacao_ativa,
    limpar_operacao_ativa,
    obter_operacao_ativa,
)


@login_required
def dashboard(request):
    operacao = obter_operacao_ativa(request)
    if operacao == USE_HELVI:
        return redirect("dashboard_use_helvi")

    contexto = obter_contexto_dashboard()

    return render(
        request,
        "core/dashboard.html",
        contexto,
    )


@login_required
def selecionar_operacao(request):
    if request.method == "POST":
        operacao = definir_operacao_ativa(
            request,
            request.POST.get("operacao"),
        )
        if operacao == HELVI_DISTRIBUIDORA:
            return redirect("dashboard")
        if operacao == USE_HELVI:
            return redirect("dashboard_use_helvi")

        return render(
            request,
            "core/selecionar_operacao.html",
            {"operacao_invalida": True},
            status=400,
        )

    return render(request, "core/selecionar_operacao.html")


@login_required
def trocar_operacao(request):
    limpar_operacao_ativa(request)
    return redirect("selecionar_operacao")


@login_required
def dashboard_use_helvi(request):
    operacao = obter_operacao_ativa(request)
    if operacao is None:
        return redirect("selecionar_operacao")
    if operacao == HELVI_DISTRIBUIDORA:
        return redirect("dashboard")
    return render(request, "core/dashboard_use_helvi.html")


@login_required
def central_relatorios(request):
    contexto = montar_central_relatorios()

    return render(
        request,
        "core/relatorios.html",
        contexto,
    )


@login_required
def relatorio_analitico(request, slug):
    if slug not in RELATORIOS:
        raise Http404("Relatório não encontrado.")

    parametros_entrada = request.GET.copy()
    periodo_rapido = parametros_entrada.get("periodo")
    hoje = timezone.localdate()
    periodos = {
        "hoje": (hoje, hoje),
        "7d": (hoje - timedelta(days=6), hoje),
        "30d": (hoje - timedelta(days=29), hoje),
        "90d": (hoje - timedelta(days=89), hoje),
        "mes": (hoje.replace(day=1), hoje),
        "ano": (hoje.replace(month=1, day=1), hoje),
    }
    if periodo_rapido in periodos:
        inicio, fim = periodos[periodo_rapido]
        parametros_entrada["data_inicial"] = inicio.isoformat()
        parametros_entrada["data_final"] = fim.isoformat()

    form = RelatorioAnaliticoFiltroForm(
        parametros_entrada or None,
        status_choices=obter_status_relatorio(slug),
    )
    filtros = form.cleaned_data if form.is_valid() else {}
    relatorio = obter_relatorio_analitico(slug, filtros)
    periodo_texto = "Todo o período"
    if filtros.get("data_inicial") or filtros.get("data_final"):
        periodo_texto = f"{filtros.get('data_inicial') or 'início'} a {filtros.get('data_final') or 'hoje'}"

    formato = request.GET.get("exportar")
    if formato == "csv":
        return exportar_csv(relatorio, slug)
    if formato == "pdf":
        try:
            return exportar_pdf(relatorio, slug, periodo_texto)
        except ValueError as erro:
            raise Http404(str(erro)) from erro

    por_pagina = int(filtros.get("por_pagina") or 25)
    pagina = Paginator(relatorio.pop("linhas"), por_pagina).get_page(
        request.GET.get("pagina")
    )
    parametros = request.GET.copy()
    parametros.pop("pagina", None)

    return render(
        request,
        "core/relatorio_analitico.html",
        {
            **relatorio,
            "form": form,
            "pagina": pagina,
            "slug": slug,
            "querystring": parametros.urlencode(),
            "periodo_rapido": periodo_rapido,
            "periodo_texto": periodo_texto,
            "possui_pdf": slug in PDF_OFICIAL,
            "filtros_ativos": sum(bool(filtros.get(campo)) for campo in ("data_inicial", "data_final", "busca", "status")),
        },
    )
