from django.contrib import admin
from .models import MovimentacaoEstoque


@admin.register(MovimentacaoEstoque)
class MovimentacaoEstoqueAdmin(admin.ModelAdmin):
    list_display = (
        'produto',
        'tipo',
        'motivo',
        'quantidade',
        'data_movimentacao',
    )

    search_fields = (
        'produto__codigo',
        'produto__modelo',
    )

    list_filter = (
        'tipo',
        'motivo',
        'data_movimentacao',
    )