from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from financeiro.services.fluxo_caixa_service import (
    obter_fluxo_caixa,
)


@login_required
def lista_movimentacoes(request):
    contexto = obter_fluxo_caixa(request.GET)

    return render(
        request,
        "financeiro/lista_movimentacoes.html",
        contexto,
    )