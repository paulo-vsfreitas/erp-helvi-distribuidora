from django.urls import path

from vendas.views import (
    cancelar_venda_view,
    editar_venda,
    ficha_venda,
    finalizar_venda_view,
    lista_vendas,
    pdf_resumo_venda,
    nova_venda,
    relatorio_vendas,
    alterar_vendedor_view,
)
from vendas.views.api import buscar_produtos


app_name = "vendas"


urlpatterns = [
    path(
        "",
        lista_vendas,
        name="lista",
    ),
    path(
        "nova/",
        nova_venda,
        name="nova",
    ),
    path(
        "relatorios/",
        relatorio_vendas,
        name="relatorio",
    ),
    path(
        "api/produtos/",
        buscar_produtos,
        name="api_produtos",
    ),
    path(
        "<int:numero>/editar/",
        editar_venda,
        name="editar",
    ),
    path(
        "<int:numero>/vendedor/",
        alterar_vendedor_view,
        name="alterar_vendedor",
    ),
    path(
        "<int:numero>/pdf/",
        pdf_resumo_venda,
        name="pdf",
    ),
    path(
        "<int:numero>/finalizar/",
        finalizar_venda_view,
        name="finalizar",
    ),
    path(
        "<int:numero>/cancelar/",
        cancelar_venda_view,
        name="cancelar",
    ),
    path(
        "<int:numero>/",
        ficha_venda,
        name="ficha",
    ),
]
