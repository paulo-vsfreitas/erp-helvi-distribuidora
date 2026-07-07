from django.urls import path

from compras.views.dashboard import dashboard_compras
from compras.views.lista import lista_compras
from compras.views.cadastro import nova_compra
from compras.views.edicao import editar_compra
from compras.views.estoque import receber_compra_view
from compras.views.ficha import ficha_compra
from compras.views.api.produtos import api_buscar_produtos


app_name = "compras"

urlpatterns = [
    path("", dashboard_compras, name="dashboard"),
    path("lista/", lista_compras, name="lista"),
    path("nova/", nova_compra, name="nova"),
    path("<int:pk>/", ficha_compra, name="ficha"),
    path("<int:pk>/editar/", editar_compra, name="editar"),
    path("<int:pk>/receber/", receber_compra_view, name="receber"),
    path("api/produtos/", api_buscar_produtos, name="api_buscar_produtos"),
]