from core.services.operacao_service import obter_operacao_ativa
from usuarios.permissoes import Modulo, usuario_tem_permissao_na_operacao


def permissoes_usuario(request):
    usuario = getattr(request, "user", None)
    operacao = obter_operacao_ativa(request) or "distribuidora"

    def possui(modulo):
        return usuario_tem_permissao_na_operacao(
            usuario,
            modulo,
            operacao,
        )

    return {
        "permissoes": {
            "dashboard": possui(Modulo.DASHBOARD),
            "vendas": possui(Modulo.VENDAS),
            "clientes": possui(Modulo.CLIENTES),
            "fornecedores": possui(Modulo.FORNECEDORES),
            "produtos": possui(Modulo.PRODUTOS),
            "catalogo": possui(Modulo.CATALOGO),
            "estoque": possui(Modulo.ESTOQUE),
            "financeiro": possui(Modulo.FINANCEIRO),
            "relatorios": possui(Modulo.RELATORIOS),
            "configuracoes": possui(Modulo.CONFIGURACOES),
            "usuarios": possui(Modulo.USUARIOS),
            "compras": possui(Modulo.COMPRAS),
            "eventos": possui(Modulo.EVENTOS),
        }
    }
