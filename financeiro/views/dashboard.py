from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from financeiro.services.dashboard_service import (
    obter_dados_dashboard_financeiro,
)
from usuarios.decorators import perfil_requerido


@login_required
@perfil_requerido("ADM", "GER", "FIN")
def dashboard_financeiro(request):
    contexto = obter_dados_dashboard_financeiro()

    return render(
        request,
        "financeiro/dashboard.html",
        contexto,
    )