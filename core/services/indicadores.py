from decimal import Decimal


def formatar_moeda(valor):
    valor = valor or Decimal("0.00")

    return (
        f"R$ {valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def criar_indicador(
    titulo,
    valor,
    icone,
    subtitulo="",
    url=None,
):
    return {
        "titulo": titulo,
        "valor": valor,
        "icone": icone,
        "subtitulo": subtitulo,
        "url": url,
    }