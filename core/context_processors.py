from django.conf import settings

from core.services.operacao_service import obter_operacao_ativa


def ambiente_aplicacao(request):
    ambiente = settings.APP_ENV
    rotulos = {
        "development": "AMBIENTE DE DESENVOLVIMENTO",
        "staging": "AMBIENTE DE HOMOLOGAÇÃO",
    }
    return {
        "app_ambiente": ambiente,
        "app_ambiente_rotulo": rotulos.get(ambiente, ""),
        "app_exibir_ambiente": ambiente != "production",
    }


def operacao_ativa(request):
    return {
        "operacao_ativa": obter_operacao_ativa(request),
    }
