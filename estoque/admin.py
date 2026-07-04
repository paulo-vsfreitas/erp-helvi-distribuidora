from django.contrib import admin

from .models import MovimentacaoEstoque


@admin.register(MovimentacaoEstoque)
class MovimentacaoEstoqueAdmin(admin.ModelAdmin):
    list_display = (
        "produto",
        "tipo",
        "quantidade",
        "saldo_anterior",
        "saldo_atual",
        "usuario",
        "local",
        "data_movimentacao",
    )

    list_filter = (
        "tipo",
        "local",
        "data_movimentacao",
    )

    search_fields = (
        "produto__codigo",
        "produto__modelo",
        "origem",
        "observacao",
    )

    readonly_fields = (
        "data_movimentacao",
    )
