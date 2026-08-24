from django.urls import path

from . import views

app_name = "eventos"

urlpatterns = [
    path("", views.agenda, name="agenda"),
    path("novo/", views.novo, name="novo"),
    path("despesas/", views.despesas_gerais, name="despesas_gerais"),
    path("financeiro/", views.financeiro_use, name="financeiro"),
    path("financeiro/relatorios/", views.relatorio_financeiro, name="relatorio_financeiro"),
    path("tipos-produto/", views.tipos_produto, name="tipos_produto"),
    path("tipos-produto/<int:pk>/editar/", views.editar_tipo_produto, name="editar_tipo_produto"),
    path("tipos-produto/<int:pk>/alternar/", views.alternar_tipo_produto, name="alternar_tipo_produto"),
    path("equipes/", views.equipes, name="equipes"),
    path("equipes/pessoas/<int:pk>/editar/", views.editar_pessoa, name="editar_pessoa"),
    path("equipes/<int:pk>/editar/", views.editar_equipe, name="editar_equipe"),
    path("equipes/<str:tipo>/<int:pk>/alternar/", views.alternar_cadastro_equipe, name="alternar_cadastro_equipe"),
    path("categorias-despesa/", views.categorias_despesa, name="categorias_despesa"),
    path("categorias-despesa/<int:pk>/editar/", views.editar_categoria_despesa, name="editar_categoria_despesa"),
    path("categorias-despesa/<int:pk>/alternar/", views.alternar_categoria_despesa, name="alternar_categoria_despesa"),
    path("<int:pk>/", views.ficha, name="ficha"),
    path("<int:pk>/editar/", views.editar, name="editar"),
    path("<int:pk>/cancelar/", views.cancelar, name="cancelar"),
    path("<int:pk>/despesas/nova/", views.lancar_despesa, name="lancar_despesa"),
    path("<int:pk>/vendas/nova/", views.lancar_venda, name="lancar_venda"),
]
