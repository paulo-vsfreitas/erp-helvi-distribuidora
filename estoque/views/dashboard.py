from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from estoque.models import MovimentacaoEstoque
from estoque.services.movimentacoes import (
    obter_acoes_dashboard,
    obter_cards_dashboard,
)
from usuarios.permissoes import Acao, usuario_pode_executar


@login_required
def dashboard_estoque(request):
    cards = obter_cards_dashboard()
    acoes = (
        obter_acoes_dashboard()
        if usuario_pode_executar(request.user, Acao.MOVIMENTAR_ESTOQUE)
        else []
    )

    ultimas_movimentacoes = MovimentacaoEstoque.objects.select_related(
        "produto",
        "usuario",
    ).all()[:10]

    return render(
        request,
        "estoque/dashboard.html",
        {
            "cards": cards,
            "acoes": acoes,
            "ultimas_movimentacoes": ultimas_movimentacoes,
        },
    )
