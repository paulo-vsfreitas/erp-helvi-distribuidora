class Modulo:
    DASHBOARD = "dashboard"
    VENDAS = "vendas"
    CLIENTES = "clientes"
    FORNECEDORES = "fornecedores"
    PRODUTOS = "produtos"
    CATALOGO = "catalogo"
    ESTOQUE = "estoque"
    FINANCEIRO = "financeiro"
    RELATORIOS = "relatorios"
    CONFIGURACOES = "configuracoes"
    USUARIOS = "usuarios"
    COMPRAS = "compras"
    EVENTOS = "eventos"


class Acao:
    """Permissões para operações sensíveis dentro de um módulo."""

    GERENCIAR_CATALOGO = "catalogo.gerenciar"
    GERENCIAR_PRODUTOS = "produtos.gerenciar"
    MOVIMENTAR_ESTOQUE = "estoque.movimentar"
    GERENCIAR_INVENTARIO = "estoque.gerenciar_inventario"
    ALTERAR_VENDEDOR = "vendas.alterar_vendedor"


MODULOS_POR_OPERACAO = {
    "distribuidora": {
        Modulo.DASHBOARD,
        Modulo.VENDAS,
        Modulo.CLIENTES,
        Modulo.FORNECEDORES,
        Modulo.PRODUTOS,
        Modulo.CATALOGO,
        Modulo.ESTOQUE,
        Modulo.FINANCEIRO,
        Modulo.RELATORIOS,
        Modulo.CONFIGURACOES,
        Modulo.USUARIOS,
        Modulo.COMPRAS,
    },
    "use-helvi": {
        Modulo.DASHBOARD,
        Modulo.FINANCEIRO,
        Modulo.EVENTOS,
    },
}


PERFIS = {
    "ADM": {
        "nome": "Administrador",
        "permissoes": {
            Modulo.DASHBOARD,
            Modulo.VENDAS,
            Modulo.CLIENTES,
            Modulo.FORNECEDORES,
            Modulo.PRODUTOS,
            Modulo.CATALOGO,
            Modulo.ESTOQUE,
            Modulo.FINANCEIRO,
            Modulo.RELATORIOS,
            Modulo.CONFIGURACOES,
            Modulo.USUARIOS,
            Modulo.COMPRAS,
            Modulo.EVENTOS,
        },
    },
    "GER": {
        "nome": "Gerente",
        "permissoes": {
            Modulo.DASHBOARD,
            Modulo.VENDAS,
            Modulo.CLIENTES,
            Modulo.FORNECEDORES,
            Modulo.PRODUTOS,
            Modulo.CATALOGO,
            Modulo.ESTOQUE,
            Modulo.FINANCEIRO,
            Modulo.RELATORIOS,
            Modulo.COMPRAS,
            Modulo.EVENTOS,
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


ACOES_POR_PERFIL = {
    "ADM": {
        Acao.GERENCIAR_CATALOGO,
        Acao.GERENCIAR_PRODUTOS,
        Acao.MOVIMENTAR_ESTOQUE,
        Acao.GERENCIAR_INVENTARIO,
        Acao.ALTERAR_VENDEDOR,
    },
    "GER": {
        Acao.GERENCIAR_CATALOGO,
        Acao.GERENCIAR_PRODUTOS,
        Acao.MOVIMENTAR_ESTOQUE,
        Acao.GERENCIAR_INVENTARIO,
        Acao.ALTERAR_VENDEDOR,
    },
    "VEN": set(),
    "FIN": {
        Acao.ALTERAR_VENDEDOR,
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


def operacao_tem_modulo(operacao, modulo):
    """Confirma se o domínio pertence à operação ativa."""
    codigo = getattr(operacao, "codigo", operacao)
    return modulo in MODULOS_POR_OPERACAO.get(codigo, set())


def usuario_tem_permissao_na_operacao(usuario, modulo, operacao):
    return usuario_tem_permissao(usuario, modulo) and operacao_tem_modulo(
        operacao,
        modulo,
    )


def usuario_pode_executar(usuario, acao):
    if not usuario or not usuario.is_authenticated:
        return False

    if usuario.is_superuser:
        return True

    return acao in ACOES_POR_PERFIL.get(usuario.perfil, set())
