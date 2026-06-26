from django.urls import path
from .views.marcas import lista_marcas, nova_marca, editar_marca, excluir_marca

urlpatterns = [
    path("marcas/", lista_marcas, name="lista_marcas"),
    path("marcas/nova/", nova_marca, name="nova_marca"),
    path("marcas/<int:pk>/editar/", editar_marca, name="editar_marca"),
    path("marcas/<int:pk>/excluir/", excluir_marca, name="excluir_marca"),
]