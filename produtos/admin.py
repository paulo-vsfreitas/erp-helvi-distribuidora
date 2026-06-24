# Register your models here.

from django.contrib import admin
from .models import Produto


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = (
        'codigo',
        'modelo',
        'cor',
        'genero',
        'preco_custo',
        'preco_venda',
        'estoque_atual',
        'ativo',
    )

    search_fields = (
        'codigo',
        'modelo',
        'marca',
        'cor',
    )

    list_filter = (
        'ativo',
        'genero',
        'marca',
    )