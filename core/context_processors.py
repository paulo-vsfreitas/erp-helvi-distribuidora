from django.conf import settings


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
