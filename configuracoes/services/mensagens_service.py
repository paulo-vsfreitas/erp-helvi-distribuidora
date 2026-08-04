from string import Formatter

from django.core.exceptions import ValidationError


VARIAVEIS_MENSAGEM = (
    "CLIENTE",
    "ORCAMENTO",
    "TOTAL",
    "VALIDADE",
    "VENDEDOR",
    "EMPRESA",
)

CONTEXTO_EXEMPLO_MENSAGEM = {
    "CLIENTE": "Ótica Central",
    "ORCAMENTO": "ORC-000123",
    "TOTAL": "R$ 1.250,00",
    "VALIDADE": "15/08/2026",
    "VENDEDOR": "Maria Silva",
    "EMPRESA": "Helvi",
}


def validar_modelo_mensagem(modelo):
    if not modelo:
        return

    try:
        partes = Formatter().parse(modelo)
        for _, variavel, especificacao, conversao in partes:
            if variavel is None:
                continue
            if variavel not in VARIAVEIS_MENSAGEM:
                raise ValidationError(
                    f"A variável {{{variavel}}} não é permitida."
                )
            if especificacao or conversao:
                raise ValidationError(
                    "As variáveis não aceitam formatação adicional."
                )
    except ValueError as erro:
        raise ValidationError(
            "Revise as chaves do modelo de mensagem."
        ) from erro


def renderizar_modelo_mensagem(modelo, contexto):
    validar_modelo_mensagem(modelo)
    valores = {
        variavel: str(contexto.get(variavel, ""))
        for variavel in VARIAVEIS_MENSAGEM
    }
    return modelo.format_map(valores)
