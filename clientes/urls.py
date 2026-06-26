from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_clientes, name='lista_clientes'),
    path('novo/', views.novo_cliente, name='novo_cliente'),
    path('editar/<int:cliente_id>/', views.editar_cliente, name='editar_cliente'),
]