import re
from urllib.parse import quote


def normalizar_telefone_whatsapp(telefone):
    """
    Retorna o telefone somente com números.

    Para números brasileiros sem código do país,
    acrescenta automaticamente o prefixo 55.
    """
    numeros = re.sub(r"\D", "", telefone or "")

    if not numeros:
        raise ValueError("O telefone do destinatário não foi informado.")

    if len(numeros) in (10, 11):
        numeros = f"55{numeros}"

    if len(numeros) < 12:
        raise ValueError(
            "O telefone informado não é válido para o WhatsApp."
        )

    return numeros


def gerar_url_whatsapp(*, telefone, mensagem):
    telefone_normalizado = normalizar_telefone_whatsapp(telefone)
    mensagem_codificada = quote((mensagem or "").strip())

    return (
        f"https://wa.me/{telefone_normalizado}"
        f"?text={mensagem_codificada}"
    )