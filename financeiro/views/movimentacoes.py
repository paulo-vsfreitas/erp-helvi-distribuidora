from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from financeiro.services.fluxo_caixa_service import (
    obter_fluxo_caixa,
)
from core.services.operacao_service import obter_operacao_ativa


@login_required
def lista_movimentacoes(request):
    ativa = obter_operacao_ativa(request)
    contexto = obter_fluxo_caixa(
        request.GET, ativa.codigo if ativa else "distribuidora"
    )

    return render(
        request,
        "financeiro/lista_movimentacoes.html",
        contexto,
    )
