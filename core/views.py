from django.contrib.auth.decorators import login_required
from django.shortcuts import render

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


def recuperacao_acesso(request):
    return render(
        request,
        "core/recuperacao_acesso.html",
    )