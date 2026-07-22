from django.urls import path

from comercial.views import (
    api_buscar_clientes,
    api_buscar_produtos,
    cadastrar_orcamento,
    dashboard,
    ficha_orcamento,
    editar_orcamento,
    alterar_status,
    converter_orcamento,
    
    
)
from comercial.views.cliente import vincular_cliente


app_name = "comercial"


urlpatterns = [
    path(
        "",
        dashboard,
        name="dashboard",
    ),
    path(
        "novo/",
        cadastrar_orcamento,
        name="novo",
    ),
    path(
        "orcamentos/<int:numero>/",
        ficha_orcamento,
        name="ficha",
    ),
    path(
        "api/clientes/",
        api_buscar_clientes,
        name="api_clientes",
    ),
    path(
        "api/produtos/",
        api_buscar_produtos,
        name="api_produtos",
    ),
    path(
        "orcamentos/<int:numero>/editar/",
        editar_orcamento,
        name="editar",
    ),
    path(
    "orcamentos/<int:numero>/status/<str:status>/",
    alterar_status,
    name="alterar_status",
    ),

    path(
    "orcamentos/<int:numero>/converter/",
    converter_orcamento,
    name="converter_orcamento",
    ),

    path(
    "orcamentos/<int:numero>/vincular-cliente/",
    vincular_cliente,
    name="vincular_cliente",
    ),
]