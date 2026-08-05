from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from estoque.models import MovimentacaoEstoque
from estoque.services import (
    listar_movimentacoes_estoque,
    obter_cards_dashboard,
    obter_acoes_dashboard,
    obter_resumo_estoque,
)
from usuarios.permissoes import Acao, usuario_pode_executar


@login_required
def lista_movimentacoes(request):
    busca = request.GET.get("busca", "").strip()
    tipo = request.GET.get("tipo", "").strip()
    origem = request.GET.get("origem", "").strip()

    contexto = {
        "movimentacoes": listar_movimentacoes_estoque(
            busca=busca,
            tipo=tipo,
            origem=origem,
        ),
        "busca": busca,
        "tipo_selecionado": tipo,
        "origem_selecionada": origem,
        "tipos_movimentacao": MovimentacaoEstoque.TIPO_CHOICES,

        "cards": obter_cards_dashboard(),
        "acoes": (
            obter_acoes_dashboard()
            if usuario_pode_executar(request.user, Acao.MOVIMENTAR_ESTOQUE)
            else []
        ),

        **obter_resumo_estoque(),
    }

    return render(
        request,
        "estoque/lista_movimentacoes.html",
        contexto,
    )
