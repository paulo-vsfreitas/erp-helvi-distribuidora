from django.contrib.auth.models import Group


PERFIS_PADRAO = [
    "Administrador",
    "Gerente",
    "Vendedor",
    "Financeiro",
]


def criar_perfis_padrao():
    """
    Cria os grupos/perfis padrão do ERP Helvi.
    """
    for perfil in PERFIS_PADRAO:
        Group.objects.get_or_create(name=perfil)