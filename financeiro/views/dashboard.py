from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from financeiro.services.dashboard_service import (
    obter_dados_dashboard_financeiro,
)
from usuarios.decorators import perfil_requerido
from core.services.operacao_service import obter_operacao_ativa


@login_required
@perfil_requerido("ADM", "GER", "FIN")
def dashboard_financeiro(request):
    operacao = obter_operacao_ativa(request)
    contexto = obter_dados_dashboard_financeiro(
        operacao.codigo if operacao else "distribuidora"
    )

    return render(
        request,
        "financeiro/dashboard.html",
        contexto,
    )
