from django.urls import path

from .views.ficha_produto import ficha_produto
from .views.catalogo_importacao import (
    confirmar_catalogo,
    conferir_catalogo,
    importar_catalogo,
    reanalisar_catalogo,
    visualizar_arquivo_catalogo,
    visualizar_recorte_catalogo,
)
from .views.importacao import (
    baixar_modelo_importacao_produtos,
    importar_produtos,
)
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

    # Importação
    path(
        "importar/",
        importar_produtos,
        name="importar_produtos",
    ),
    path(
        "importar/modelo/",
        baixar_modelo_importacao_produtos,
        name="modelo_importacao_produtos",
    ),
    path("importar/catalogo/", importar_catalogo, name="importar_catalogo"),
    path("importar/catalogo/<int:lote_id>/", conferir_catalogo, name="conferir_catalogo"),
    path("importar/catalogo/<int:lote_id>/confirmar/", confirmar_catalogo, name="confirmar_catalogo"),
    path("importar/catalogo/<int:lote_id>/reanalisar/", reanalisar_catalogo, name="reanalisar_catalogo"),
    path(
        "importar/catalogo/<int:lote_id>/arquivo/<int:arquivo_id>/",
        visualizar_arquivo_catalogo,
        name="visualizar_arquivo_catalogo",
    ),
    path(
        "importar/catalogo/<int:lote_id>/arquivo/<int:arquivo_id>/recorte/<str:tipo>/<int:indice>/",
        visualizar_recorte_catalogo,
        name="visualizar_recorte_catalogo",
    ),

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