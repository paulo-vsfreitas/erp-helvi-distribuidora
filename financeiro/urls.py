from django.urls import path

from financeiro.views.baixas import registrar_baixa_view
from financeiro.views.categorias import (
    editar_categoria,
    inativar_categoria,
    lista_categorias,
    nova_categoria,
    reativar_categoria,
)
from financeiro.views.contas_financeiras import (
    editar_conta_financeira,
    ficha_conta_financeira,
    inativar_conta_financeira,
    lista_contas_financeiras,
    nova_conta_financeira,
    reativar_conta_financeira,
)
from financeiro.views.contas_pagar import (
    ficha_conta_pagar,
    lista_contas_pagar,
    nova_conta_pagar,
)
from financeiro.views.contas_receber import (
    ficha_conta_receber,
    lista_contas_receber,
    nova_conta_receber,
)
from financeiro.views.dashboard import dashboard_financeiro
from financeiro.views.recebimentos import registrar_recebimento_view

from financeiro.views.movimentacoes import (
    lista_movimentacoes,
)


app_name = "financeiro"


urlpatterns = [
    # Dashboard financeiro
    path(
        "",
        dashboard_financeiro,
        name="dashboard",
    ),

    # Fluxo de caixa
    path(
        "movimentacoes/",
        lista_movimentacoes,
        name="lista_movimentacoes",
    ),

    # Categorias financeiras
    path(
        "categorias/",
        lista_categorias,
        name="lista_categorias",
    ),
    path(
        "categorias/nova/",
        nova_categoria,
        name="nova_categoria",
    ),
    path(
        "categorias/<int:pk>/editar/",
        editar_categoria,
        name="editar_categoria",
    ),
    path(
        "categorias/<int:pk>/inativar/",
        inativar_categoria,
        name="inativar_categoria",
    ),
    path(
        "categorias/<int:pk>/reativar/",
        reativar_categoria,
        name="reativar_categoria",
    ),

    # Contas financeiras
    path(
        "contas/",
        lista_contas_financeiras,
        name="lista_contas_financeiras",
    ),
    path(
        "contas/nova/",
        nova_conta_financeira,
        name="nova_conta_financeira",
    ),
    path(
        "contas/<int:pk>/",
        ficha_conta_financeira,
        name="ficha_conta_financeira",
    ),
    path(
        "contas/<int:pk>/editar/",
        editar_conta_financeira,
        name="editar_conta_financeira",
    ),
    path(
        "contas/<int:pk>/inativar/",
        inativar_conta_financeira,
        name="inativar_conta_financeira",
    ),
    path(
        "contas/<int:pk>/reativar/",
        reativar_conta_financeira,
        name="reativar_conta_financeira",
    ),

    # Contas a pagar
    path(
        "contas-pagar/",
        lista_contas_pagar,
        name="lista_contas_pagar",
    ),
    path(
        "contas-pagar/nova/",
        nova_conta_pagar,
        name="nova_conta_pagar",
    ),
    path(
        "contas-pagar/<int:pk>/",
        ficha_conta_pagar,
        name="ficha_conta_pagar",
    ),

    # Contas a receber
    path(
        "contas-receber/",
        lista_contas_receber,
        name="lista_contas_receber",
    ),
    path(
        "contas-receber/nova/",
        nova_conta_receber,
        name="nova_conta_receber",
    ),
    path(
        "contas-receber/<int:pk>/",
        ficha_conta_receber,
        name="ficha_conta_receber",
    ),
    path(
        "contas-receber/parcela/<int:parcela_id>/receber/",
        registrar_recebimento_view,
        name="registrar_recebimento",
    ),

    # Baixas financeiras
    path(
        "parcelas/<int:parcela_id>/registrar-baixa/",
        registrar_baixa_view,
        name="registrar_baixa",
    ),

]