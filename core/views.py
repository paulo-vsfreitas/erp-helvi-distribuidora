from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from core.services.central_relatorios_service import (
    montar_central_relatorios,
)
from core.services.dashboard_service import (
    obter_contexto_dashboard,
)


@login_required
def dashboard(request):
    contexto = obter_contexto_dashboard()

    return render(
        request,
        "core/dashboard.html",
        contexto,
    )


@login_required
def central_relatorios(request):
    contexto = montar_central_relatorios()

    return render(
        request,
        "core/relatorios.html",
        contexto,
    )
