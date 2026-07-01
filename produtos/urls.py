from django.urls import path

from .views.ficha_produto import ficha_produto
from .views.produtos import (
    editar_produto,
    excluir_imagem_produto,
    galeria_produto,
    inativar_produto,
    lista_produtos,
    novo_produto,
    reativar_produto,
)

app_name = "produtos"

urlpatterns = [
    path("", lista_produtos, name="lista_produtos"),
    path("novo/", novo_produto, name="novo_produto"),

    # Ficha do Produto
    path("<int:produto_id>/", ficha_produto, name="ficha_produto"),

    # Cadastro
    path("<int:produto_id>/editar/", editar_produto, name="editar_produto"),

    # Imagens
    path("<int:produto_id>/galeria/", galeria_produto, name="galeria_produto"),
    path(
        "imagem/<int:imagem_id>/excluir/",
        excluir_imagem_produto,
        name="excluir_imagem_produto",
    ),

    # Situação
    path("<int:produto_id>/inativar/", inativar_produto, name="inativar_produto"),
    path("<int:produto_id>/reativar/", reativar_produto, name="reativar_produto"),
]