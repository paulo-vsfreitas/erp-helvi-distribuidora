from django.urls import path

from vendas.views import (
    ficha_venda,
    finalizar_venda_view,
    lista_vendas,
    nova_venda,
    relatorio_vendas,
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
        "<int:numero>/finalizar/",
        finalizar_venda_view,
        name="finalizar",
    ),
    path(
        "<int:numero>/",
        ficha_venda,
        name="ficha",
    ),
]