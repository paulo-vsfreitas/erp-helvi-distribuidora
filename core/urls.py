from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('recuperar-acesso/', views.recuperacao_acesso, name='recuperacao_acesso'),
    
]