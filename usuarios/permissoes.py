class Modulo:
    DASHBOARD = "dashboard"
    VENDAS = "vendas"
    CLIENTES = "clientes"
    PRODUTOS = "produtos"
    CATALOGO = "catalogo"
    ESTOQUE = "estoque"
    FINANCEIRO = "financeiro"
    RELATORIOS = "relatorios"
    CONFIGURACOES = "configuracoes"
    USUARIOS = "usuarios"
    COMPRAS = "compras"


PERFIS = {
    "ADM": {
        "nome": "Administrador",
        "permissoes": {
            Modulo.DASHBOARD,
            Modulo.VENDAS,
            Modulo.CLIENTES,
            Modulo.PRODUTOS,
            Modulo.CATALOGO,
            Modulo.ESTOQUE,
            Modulo.FINANCEIRO,
            Modulo.RELATORIOS,
            Modulo.CONFIGURACOES,
            Modulo.USUARIOS,
            Modulo.COMPRAS,
        },
    },
    "GER": {
        "nome": "Gerente",
        "permissoes": {
            Modulo.DASHBOARD,
            Modulo.VENDAS,
            Modulo.CLIENTES,
            Modulo.PRODUTOS,
            Modulo.CATALOGO,
            Modulo.ESTOQUE,
            Modulo.FINANCEIRO,
            Modulo.RELATORIOS,
            Modulo.COMPRAS,
        },
    },
    "VEN": {
        "nome": "Vendedor",
        "permissoes": {
            Modulo.DASHBOARD,
            Modulo.VENDAS,
            Modulo.CLIENTES,
            Modulo.PRODUTOS,
            Modulo.CATALOGO,
            Modulo.ESTOQUE,
        },
    },
    "FIN": {
        "nome": "Financeiro",
        "permissoes": {
            Modulo.DASHBOARD,
            Modulo.CLIENTES,
            Modulo.FINANCEIRO,
            Modulo.RELATORIOS,
        },
    },
}


def usuario_tem_permissao(usuario, modulo):
    if not usuario or not usuario.is_authenticated:
        return False

    if usuario.is_superuser:
        return True

    perfil = PERFIS.get(usuario.perfil)

    if not perfil:
        return False

    return modulo in perfil["permissoes"]