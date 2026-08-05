from django.contrib import admin

from usuarios.models import ControleTentativaLogin, EventoLogin


@admin.register(EventoLogin)
class EventoLoginAdmin(admin.ModelAdmin):
    list_display = (
        "criado_em",
        "username",
        "endereco_ip",
        "resultado",
        "usuario",
    )
    list_filter = ("resultado", "criado_em")
    search_fields = ("username", "endereco_ip")
    readonly_fields = (
        "username",
        "endereco_ip",
        "resultado",
        "usuario",
        "user_agent",
        "criado_em",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ControleTentativaLogin)
class ControleTentativaLoginAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "endereco_ip",
        "falhas",
        "bloqueado_ate",
        "ultima_tentativa",
    )
    search_fields = ("username", "endereco_ip")
    readonly_fields = (
        "username",
        "endereco_ip",
        "falhas",
        "bloqueado_ate",
        "ultima_tentativa",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
