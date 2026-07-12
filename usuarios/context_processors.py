from usuarios.permissoes import Modulo, usuario_tem_permissao


def permissoes_usuario(request):
    usuario = getattr(request, "user", None)

    return {
        "permissoes": {
            "dashboard": usuario_tem_permissao(
                usuario,
                Modulo.DASHBOARD,
            ),
            "vendas": usuario_tem_permissao(
                usuario,
                Modulo.VENDAS,
            ),
            "clientes": usuario_tem_permissao(
                usuario,
                Modulo.CLIENTES,
            ),
            "fornecedores": usuario_tem_permissao(
                usuario,
                Modulo.FORNECEDORES,
            ),
            "produtos": usuario_tem_permissao(
                usuario,
                Modulo.PRODUTOS,
            ),
            "catalogo": usuario_tem_permissao(
                usuario,
                Modulo.CATALOGO,
            ),
            "estoque": usuario_tem_permissao(
                usuario,
                Modulo.ESTOQUE,
            ),
            "financeiro": usuario_tem_permissao(
                usuario,
                Modulo.FINANCEIRO,
            ),
            "relatorios": usuario_tem_permissao(
                usuario,
                Modulo.RELATORIOS,
            ),
            "configuracoes": usuario_tem_permissao(
                usuario,
                Modulo.CONFIGURACOES,
            ),
            "usuarios": usuario_tem_permissao(
                usuario,
                Modulo.USUARIOS,
            ),
            "compras": usuario_tem_permissao(
                usuario,
                Modulo.COMPRAS,
            ),
        }
    }