from django.urls import path

from .views.marcas import (
    lista_marcas,
    nova_marca,
    editar_marca,
    inativar_marca,
    reativar_marca,
)

from .views.colecoes import (
    lista_colecoes,
    nova_colecao,
    editar_colecao,
    inativar_colecao,
    reativar_colecao,
)

from .views.generos import (
    lista_generos,
    novo_genero,
    editar_genero,
    inativar_genero,
    reativar_genero,
)

app_name = "catalogo"

urlpatterns = [
    path("marcas/", lista_marcas, name="lista_marcas"),
    path("marcas/nova/", nova_marca, name="nova_marca"),
    path("marcas/<int:pk>/editar/", editar_marca, name="editar_marca"),
    path("marcas/<int:pk>/inativar/", inativar_marca, name="inativar_marca"),
    path("marcas/<int:pk>/reativar/", reativar_marca, name="reativar_marca",),

    path("colecoes/", lista_colecoes, name="lista_colecoes",),
    path("colecoes/nova/", nova_colecao, name="nova_colecao",),        
    path("colecoes/<int:pk>/editar/", editar_colecao, name="editar_colecao",),
    path("colecoes/<int:pk>/inativar/", inativar_colecao, name="inativar_colecao",),
    path("colecoes/<int:pk>/reativar/", reativar_colecao, name="reativar_colecao",),

    path("generos/", lista_generos, name="lista_generos"),
    path("generos/novo/", novo_genero, name="novo_genero"),
    path("generos/<int:pk>/editar/", editar_genero, name="editar_genero"),
    path("generos/<int:pk>/inativar/", inativar_genero, name="inativar_genero"),
    path("generos/<int:pk>/reativar/", reativar_genero, name="reativar_genero"),
    
]