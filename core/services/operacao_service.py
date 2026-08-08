from dataclasses import dataclass


CHAVE_SESSAO_OPERACAO = "operacao_ativa"


@dataclass(frozen=True)
class Operacao:
    codigo: str
    nome: str


HELVI_DISTRIBUIDORA = Operacao(
    codigo="distribuidora",
    nome="Helvi Distribuidora",
)
USE_HELVI = Operacao(
    codigo="use-helvi",
    nome="Use Helvi",
)

OPERACOES = {
    operacao.codigo: operacao
    for operacao in (HELVI_DISTRIBUIDORA, USE_HELVI)
}


def obter_operacao_ativa(request):
    return OPERACOES.get(
        request.session.get(CHAVE_SESSAO_OPERACAO)
    )


def definir_operacao_ativa(request, codigo):
    operacao = OPERACOES.get(codigo)
    if operacao is not None:
        request.session[CHAVE_SESSAO_OPERACAO] = operacao.codigo
    return operacao


def limpar_operacao_ativa(request):
    request.session.pop(CHAVE_SESSAO_OPERACAO, None)
