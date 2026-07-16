from financeiro.services.conta_pagar_service import (
    criar_conta_pagar_compra,
)


def gerar_financeiro_compra(compra, usuario):
    """
    Ponto público de integração entre Compras e Financeiro.

    O módulo Compras solicita a geração financeira,
    mas todas as regras permanecem no módulo Financeiro.
    """

    return criar_conta_pagar_compra(
        compra=compra,
        usuario=usuario,
    )