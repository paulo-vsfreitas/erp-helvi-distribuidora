from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render

from financeiro.models import ContaPagar
from financeiro.services.conta_pagar_service import (
    obter_dados_ficha_conta_pagar,
)
from usuarios.decorators import perfil_requerido


@login_required
@perfil_requerido("ADM", "GER", "FIN")
def ficha_conta_pagar(request, pk):
    try:
        contexto = obter_dados_ficha_conta_pagar(pk)
    except ContaPagar.DoesNotExist as erro:
        raise Http404(
            "Conta a Pagar não encontrada."
        ) from erro

    return render(
        request,
        "financeiro/ficha_conta_pagar.html",
        contexto,
    )