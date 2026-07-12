from django.urls import path

from fornecedores.views import (
    cadastrar_fornecedor,
    dashboard,
    editar_fornecedor,
    ficha_fornecedor,
    listar_fornecedores,
)

app_name = "fornecedores"

urlpatterns = [
    path(
        "",
        dashboard,
        name="dashboard",
    ),
    path(
        "listar/",
        listar_fornecedores,
        name="lista",
    ),
    path(
        "novo/",
        cadastrar_fornecedor,
        name="cadastrar",
    ),
    path(
        "<int:pk>/",
        ficha_fornecedor,
        name="ficha",
    ),
    path(
        "<int:pk>/editar/",
        editar_fornecedor,
        name="editar",
    ),
]