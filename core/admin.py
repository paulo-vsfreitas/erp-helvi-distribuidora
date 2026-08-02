from django.contrib import admin

from configuracoes.models import Empresa


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = (
        "nome_fantasia",
        "razao_social",
        "cnpj",
        "cidade",
        "estado",
        "atualizado_em",
    )

    readonly_fields = (
        "singleton",
        "criado_em",
        "atualizado_em",
    )

    def has_add_permission(self, request):
        if Empresa.objects.exists():
            return False

        return super().has_add_permission(request)