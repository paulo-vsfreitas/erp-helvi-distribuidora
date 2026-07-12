import re


def somente_numeros(valor):
    """
    Remove qualquer caractere que não seja número.

    Exemplos:
    12.345.678/0001-90 -> 12345678000190
    123.456.789-09     -> 12345678909
    """
    return re.sub(r"\D", "", valor or "")


def validar_cpf(cpf):
    """
    Valida um CPF pelos dígitos verificadores.
    """
    cpf = somente_numeros(cpf)

    if len(cpf) != 11:
        return False

    if cpf == cpf[0] * 11:
        return False

    soma = sum(
        int(cpf[indice]) * (10 - indice)
        for indice in range(9)
    )

    primeiro_digito = (soma * 10) % 11

    if primeiro_digito == 10:
        primeiro_digito = 0

    if primeiro_digito != int(cpf[9]):
        return False

    soma = sum(
        int(cpf[indice]) * (11 - indice)
        for indice in range(10)
    )

    segundo_digito = (soma * 10) % 11

    if segundo_digito == 10:
        segundo_digito = 0

    return segundo_digito == int(cpf[10])


def validar_cnpj(cnpj):
    """
    Valida um CNPJ pelos dígitos verificadores.
    """
    cnpj = somente_numeros(cnpj)

    if len(cnpj) != 14:
        return False

    if cnpj == cnpj[0] * 14:
        return False

    pesos_primeiro_digito = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    soma = sum(
        int(numero) * peso
        for numero, peso in zip(
            cnpj[:12],
            pesos_primeiro_digito,
        )
    )

    resto = soma % 11
    primeiro_digito = 0 if resto < 2 else 11 - resto

    if primeiro_digito != int(cnpj[12]):
        return False

    pesos_segundo_digito = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    soma = sum(
        int(numero) * peso
        for numero, peso in zip(
            cnpj[:13],
            pesos_segundo_digito,
        )
    )

    resto = soma % 11
    segundo_digito = 0 if resto < 2 else 11 - resto

    return segundo_digito == int(cnpj[13])


def validar_cpf_cnpj(documento, tipo_pessoa=None):
    """
    Valida CPF ou CNPJ.

    Quando o tipo de pessoa é informado, também confirma se o tamanho
    do documento corresponde ao tipo selecionado.
    """
    documento = somente_numeros(documento)

    if tipo_pessoa == "PF":
        return validar_cpf(documento)

    if tipo_pessoa == "PJ":
        return validar_cnpj(documento)

    if len(documento) == 11:
        return validar_cpf(documento)

    if len(documento) == 14:
        return validar_cnpj(documento)

    return False


def formatar_cpf_cnpj(documento):
    """
    Retorna o documento com a máscara correspondente.
    """
    documento = somente_numeros(documento)

    if len(documento) == 11:
        return (
            f"{documento[:3]}."
            f"{documento[3:6]}."
            f"{documento[6:9]}-"
            f"{documento[9:]}"
        )

    if len(documento) == 14:
        return (
            f"{documento[:2]}."
            f"{documento[2:5]}."
            f"{documento[5:8]}/"
            f"{documento[8:12]}-"
            f"{documento[12:]}"
        )

    return documento

def formatar_telefone(telefone):
    """
    Formata telefone fixo ou celular com DDD.
    """
    numeros = somente_numeros(telefone)

    if len(numeros) == 11:
        return (
            f"({numeros[:2]}) "
            f"{numeros[2:7]}-"
            f"{numeros[7:]}"
        )

    if len(numeros) == 10:
        return (
            f"({numeros[:2]}) "
            f"{numeros[2:6]}-"
            f"{numeros[6:]}"
        )

    return telefone