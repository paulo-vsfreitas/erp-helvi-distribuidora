from django.contrib import admin
from .models import Venda, ItemVenda


class ItemVendaInline(admin.TabularInline):
    model = ItemVenda
    extra = 1


@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'cliente',
        'data_venda',
        'status',
        'forma_pagamento',
        
    )

    list_filter = (
        'status',
        'forma_pagamento',
        'data_venda',
    )

    search_fields = (
        'cliente__nome_fantasia',
        'cliente__razao_social',
    )

    inlines = [ItemVendaInline]

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.baixar_estoque()


@admin.register(ItemVenda)
class ItemVendaAdmin(admin.ModelAdmin):
    list_display = (
        'venda',
        'produto',
        'quantidade',
        'preco_unitario',
    )