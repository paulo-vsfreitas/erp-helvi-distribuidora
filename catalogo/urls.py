from django.urls import path

from .views.marcas import (
    lista_marcas,
    nova_marca,
    editar_marca,
    inativar_marca,
)

app_name = "catalogo"

urlpatterns = [
    path("marcas/", lista_marcas, name="lista_marcas"),
    path("marcas/nova/", nova_marca, name="nova_marca"),
    path("marcas/<int:pk>/editar/", editar_marca, name="editar_marca"),
    path("marcas/<int:pk>/inativar/", inativar_marca, name="inativar_marca"),
]