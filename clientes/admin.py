from django.contrib import admin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = (
        'nome_fantasia',
        'razao_social',
        'cidade',
        'estado',
        'whatsapp',
        'ativo',
    )

    search_fields = (
        'nome_fantasia',
        'razao_social',
        'cnpj',
        'responsavel',
    )

    list_filter = (
        'ativo',
        'estado',
        'cidade',
    )