from django.db.models import F, Q, Sum

from estoque.models import MovimentacaoEstoque
from produtos.models import Produto


def listar_movimentacoes_estoque(busca="", tipo=""):
    movimentacoes = MovimentacaoEstoque.objects.select_related(
        "produto",
        "usuario",
    ).all()

    if busca:
        movimentacoes = movimentacoes.filter(
            Q(produto__codigo__icontains=busca)
            | Q(produto__modelo__icontains=busca)
        )

    if tipo:
        movimentacoes = movimentacoes.filter(tipo=tipo)

    return movimentacoes


def obter_resumo_estoque():
    produtos_ativos = Produto.objects.filter(ativo=True)

    return {
        "produtos_em_estoque": produtos_ativos.filter(estoque_atual__gt=0).count(),
        "produtos_sem_estoque": produtos_ativos.filter(estoque_atual=0).count(),
        "produtos_abaixo_minimo": produtos_ativos.filter(
            estoque_atual__lte=F("estoque_minimo"),
            estoque_minimo__gt=0,
        ).count(),
        "total_pecas": produtos_ativos.aggregate(
            total=Sum("estoque_atual")
        )["total"] or 0,
    }


def obter_cards_dashboard():
    resumo = obter_resumo_estoque()

    return [
        {
            "titulo": "Produtos em Estoque",
            "valor": resumo["produtos_em_estoque"],
            "icone": "bi-box-seam",
            "cor": "success",
        },
        {
            "titulo": "Total de Peças",
            "valor": resumo["total_pecas"],
            "icone": "bi-boxes",
            "cor": "primary",
        },
        {
            "titulo": "Sem Estoque",
            "valor": resumo["produtos_sem_estoque"],
            "icone": "bi-exclamation-circle",
            "cor": "danger",
        },
        {
            "titulo": "Abaixo do Mínimo",
            "valor": resumo["produtos_abaixo_minimo"],
            "icone": "bi-exclamation-triangle",
            "cor": "warning",
        },
    ]

def obter_acoes_dashboard():
    return [
        {
            "titulo": "Nova Entrada",
            "icone": "bi-plus-circle",
            "cor": "success",
            "url": "/estoque/entradas/nova/",
        },
        {
            "titulo": "Nova Saída",
            "icone": "bi-dash-circle",
            "cor": "danger",
            "url": "#",
        },
        {
            "titulo": "Ajuste",
            "icone": "bi-sliders",
            "cor": "warning",
            "url": "#",
        },
        {
            "titulo": "Inventário",
            "icone": "bi-clipboard-check",
            "cor": "secondary",
            "url": "#",
        },
        {
            "titulo": "Transferência",
            "icone": "bi-arrow-left-right",
            "cor": "secondary",
            "url": "#",
        },
    ]

def obter_acoes_dashboard():
    return [
        {
            "titulo": "Nova Entrada",
            "icone": "bi-plus-circle",
            "cor": "success",
            "url": "#",
        },
        {
            "titulo": "Nova Saída",
            "icone": "bi-dash-circle",
            "cor": "danger",
            "url": "#",
        },
        {
            "titulo": "Ajuste",
            "icone": "bi-sliders",
            "cor": "warning",
            "url": "#",
        },
        {
            "titulo": "Inventário",
            "icone": "bi-clipboard-check",
            "cor": "outline-secondary",
            "url": "#",
        },
        {
            "titulo": "Transferência",
            "icone": "bi-arrow-left-right",
            "cor": "outline-secondary",
            "url": "#",
        },
    ]