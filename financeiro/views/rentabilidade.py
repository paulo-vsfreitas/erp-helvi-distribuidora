from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from financeiro.services.rentabilidade_service import obter_rentabilidade
from usuarios.decorators import perfil_requerido


@login_required
@perfil_requerido("ADM", "GER", "FIN")
def rentabilidade(request):
    return render(
        request,
        "financeiro/rentabilidade.html",
        obter_rentabilidade(request.GET),
    )
