from django.urls import path

from estoque.views import (
    ajuste_estoque, 
    lista_movimentacoes, 
    nova_entrada, nova_saida, 
    novo_inventario, 
    conferir_inventario, 
    finalizar_inventario_view, 
    lista_inventarios,
    dashboard_estoque,
    
    )

app_name = "estoque"

urlpatterns = [
    path("movimentacoes/", lista_movimentacoes, name="lista_movimentacoes"),
    path("entradas/nova/", nova_entrada, name="nova_entrada"),
    path("saidas/nova/", nova_saida, name="nova_saida"),
    path("ajustes/novo/", ajuste_estoque, name="ajuste_estoque"),
    path("inventarios/novo/", novo_inventario, name="novo_inventario"),
    path("inventarios/<int:pk>/conferir/", conferir_inventario, name="conferir_inventario"),
    path("inventarios/<int:pk>/finalizar/", finalizar_inventario_view, name="finalizar_inventario"),
    path("inventarios/", lista_inventarios, name="lista_inventarios"),
    path("", dashboard_estoque, name="dashboard_estoque"),
]
