from django.urls import path

from estoque.views import (
    ajuste_estoque,
    lista_movimentacoes,
    nova_entrada,
    nova_saida,
)

app_name = "estoque"

urlpatterns = [
    path("movimentacoes/", lista_movimentacoes, name="lista_movimentacoes"),
    path("entradas/nova/", nova_entrada, name="nova_entrada"),
    path("saidas/nova/", nova_saida, name="nova_saida"),
    path("ajustes/novo/", ajuste_estoque, name="ajuste_estoque"),
]