from django.urls import path


from .views import (
    editar_usuario,
    inativar_usuario,
    lista_usuarios,
    novo_usuario,
    reativar_usuario,
)

app_name = "usuarios"

urlpatterns = [
    path(
        "",
        lista_usuarios,
        name="lista_usuarios",
    ),
    path(
        "novo/",
        novo_usuario,
        name="novo_usuario",
    ),
    path(
        "<int:pk>/editar/",
        editar_usuario,
        name="editar_usuario",
    ),
    path(
        "<int:pk>/inativar/",
        inativar_usuario,
        name="inativar_usuario",
    ),
    path(
    "<int:pk>/reativar/",
    reativar_usuario,
    name="reativar_usuario",
),
]