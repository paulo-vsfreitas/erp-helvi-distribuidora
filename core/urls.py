from django.urls import path

from . import views


urlpatterns = [
    path(
        "",
        views.dashboard,
        name="dashboard",
    ),
    path(
        "relatorios/",
        views.central_relatorios,
        name="central_relatorios",
    ),
    path(
        "recuperar-acesso/",
        views.recuperacao_acesso,
        name="recuperacao_acesso",
    ),
]