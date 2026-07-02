from django.urls import path

from estoque.views import lista_movimentacoes, nova_entrada

app_name = "estoque"

urlpatterns = [
    path("movimentacoes/", lista_movimentacoes, name="lista_movimentacoes"),
    path("entradas/nova/", nova_entrada, name="nova_entrada"),
]