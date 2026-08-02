from django.db import transaction

from configuracoes.models import Empresa


@transaction.atomic
def obter_ou_criar_empresa():
    """
    Retorna o cadastro institucional da empresa.

    Caso ainda não exista, cria automaticamente um registro
    vazio para permitir a configuração inicial do ERP.
    """

    empresa, _ = Empresa.objects.get_or_create(
        singleton=True,
        defaults={
            "nome_fantasia": "Helvi Distribuidora",
            "razao_social": "Helvi Distribuidora",
        },
    )

    return empresa


def obter_empresa():
    """
    Retorna a empresa configurada.
    """

    return obter_ou_criar_empresa()


@transaction.atomic
def salvar_empresa(form):
    """
    Salva as alterações dos dados institucionais.
    """

    empresa = form.save()

    return empresa


def empresa_possui_logo():
    empresa = obter_empresa()

    return bool(empresa.logo)


def empresa_possui_dados_fiscais():
    empresa = obter_empresa()

    return bool(
        empresa.cnpj
        and empresa.razao_social
    )


def empresa_possui_endereco():
    empresa = obter_empresa()

    return bool(
        empresa.logradouro
        and empresa.cidade
    )