from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from estoque.models import MovimentacaoEstoque
from estoque.services import (
    listar_movimentacoes_estoque,
    obter_cards_dashboard,
    obter_acoes_dashboard,
    obter_resumo_estoque,
)


@login_required
def lista_movimentacoes(request):
    busca = request.GET.get("busca", "").strip()
    tipo = request.GET.get("tipo", "").strip()

    contexto = {
        "movimentacoes": listar_movimentacoes_estoque(
            busca=busca,
            tipo=tipo,
        ),
        "busca": busca,
        "tipo_selecionado": tipo,
        "tipos_movimentacao": MovimentacaoEstoque.TIPO_CHOICES,

        # Dashboard
        "cards": obter_cards_dashboard(),
        "acoes": obter_acoes_dashboard(),

        **obter_resumo_estoque(),
    }

    return render(
        request,
        "estoque/lista_movimentacoes.html",
        contexto,
    )