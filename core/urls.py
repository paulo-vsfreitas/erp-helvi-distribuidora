from django.urls import path

from . import views


urlpatterns = [
    path(
        "operacoes/",
        views.selecionar_operacao,
        name="selecionar_operacao",
    ),
    path(
        "operacoes/trocar/",
        views.trocar_operacao,
        name="trocar_operacao",
    ),
    path(
        "use-helvi/",
        views.dashboard_use_helvi,
        name="dashboard_use_helvi",
    ),
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
        "relatorios/<slug:slug>/",
        views.relatorio_analitico,
        name="relatorio_analitico",
    ),
]
