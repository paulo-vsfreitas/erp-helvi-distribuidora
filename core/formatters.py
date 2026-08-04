from decimal import Decimal


def formatar_moeda_br(valor, *, simbolo=True):
    valor = Decimal(valor or 0)
    texto = f"{valor:,.2f}"
    texto = (
        texto
        .replace(",", "__MILHAR__")
        .replace(".", ",")
        .replace("__MILHAR__", ".")
    )
    return f"R$ {texto}" if simbolo else texto
