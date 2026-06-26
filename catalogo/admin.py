from django.contrib import admin
from .models import Marca, Colecao, Genero, TipoArmacao


@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ativo', 'data_cadastro')
    search_fields = ('nome',)
    list_filter = ('ativo',)


@admin.register(Colecao)
class ColecaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ativo', 'data_cadastro')
    search_fields = ('nome',)
    list_filter = ('ativo',)


@admin.register(Genero)
class GeneroAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ativo', 'data_cadastro')
    search_fields = ('nome',)
    list_filter = ('ativo',)


@admin.register(TipoArmacao)
class TipoArmacaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ativo', 'data_cadastro')
    search_fields = ('nome',)
    list_filter = ('ativo',)