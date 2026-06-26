from django.contrib import admin
from .models import Produto


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = (
        'codigo',
        'modelo',
        'marca',
        'genero',
        'tipo_armacao',
        'preco_custo',
        'preco_venda',
        'estoque_atual',
        'ativo',
    )

    search_fields = (
        'codigo',
        'modelo',
        'marca__nome',
        'tipo_armacao__nome',
    )

    list_filter = (
        'ativo',
        'marca',
        'genero',
        'tipo_armacao',
    )