from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

from core.services.operacao_service import (
    USE_HELVI,
    obter_operacao_ativa,
)

from usuarios.permissoes import (
    Acao,
    Modulo,
    usuario_pode_executar,
    operacao_tem_modulo,
    usuario_tem_permissao,
)


class PermissaoModuloMiddleware:
    """Aplica a matriz de módulos a todas as rotas internas do ERP."""

    MODULOS_POR_NAMESPACE = {
        "catalogo": Modulo.CATALOGO,
        "clientes": Modulo.CLIENTES,
        "comercial": Modulo.VENDAS,
        "compras": Modulo.COMPRAS,
        "configuracoes": Modulo.CONFIGURACOES,
        "estoque": Modulo.ESTOQUE,
        "financeiro": Modulo.FINANCEIRO,
        "fornecedores": Modulo.FORNECEDORES,
        "produtos": Modulo.PRODUTOS,
        "usuarios": Modulo.USUARIOS,
        "vendas": Modulo.VENDAS,
        "eventos": Modulo.EVENTOS,
    }

    MODULOS_POR_URL = {
        "central_relatorios": Modulo.RELATORIOS,
        "relatorio_analitico": Modulo.RELATORIOS,
    }

    ROTAS_EXCLUSIVAS_DISTRIBUIDORA = {
        ("financeiro", "rentabilidade"),
    }

    ACOES_POR_ROTA = {
        ("catalogo", "nova_marca"): (Acao.GERENCIAR_CATALOGO, None),
        ("catalogo", "editar_marca"): (Acao.GERENCIAR_CATALOGO, None),
        ("catalogo", "inativar_marca"): (Acao.GERENCIAR_CATALOGO, None),
        ("catalogo", "reativar_marca"): (Acao.GERENCIAR_CATALOGO, None),
        ("catalogo", "nova_colecao"): (Acao.GERENCIAR_CATALOGO, None),
        ("catalogo", "editar_colecao"): (Acao.GERENCIAR_CATALOGO, None),
        ("catalogo", "inativar_colecao"): (Acao.GERENCIAR_CATALOGO, None),
        ("catalogo", "reativar_colecao"): (Acao.GERENCIAR_CATALOGO, None),
        ("catalogo", "novo_genero"): (Acao.GERENCIAR_CATALOGO, None),
        ("catalogo", "editar_genero"): (Acao.GERENCIAR_CATALOGO, None),
        ("catalogo", "inativar_genero"): (Acao.GERENCIAR_CATALOGO, None),
        ("catalogo", "reativar_genero"): (Acao.GERENCIAR_CATALOGO, None),
        ("catalogo", "novo_tipo_armacao"): (Acao.GERENCIAR_CATALOGO, None),
        ("catalogo", "editar_tipo_armacao"): (Acao.GERENCIAR_CATALOGO, None),
        ("catalogo", "inativar_tipo_armacao"): (Acao.GERENCIAR_CATALOGO, None),
        ("catalogo", "reativar_tipo_armacao"): (Acao.GERENCIAR_CATALOGO, None),
        ("produtos", "novo_produto"): (Acao.GERENCIAR_PRODUTOS, None),
        ("produtos", "importar_produtos"): (Acao.GERENCIAR_PRODUTOS, None),
        ("produtos", "modelo_importacao_produtos"): (Acao.GERENCIAR_PRODUTOS, None),
        ("produtos", "importar_catalogo"): (Acao.GERENCIAR_PRODUTOS, None),
        ("produtos", "conferir_catalogo"): (Acao.GERENCIAR_PRODUTOS, None),
        ("produtos", "confirmar_catalogo"): (Acao.GERENCIAR_PRODUTOS, None),
        ("produtos", "reanalisar_catalogo"): (Acao.GERENCIAR_PRODUTOS, None),
        ("produtos", "editar_produto"): (Acao.GERENCIAR_PRODUTOS, None),
        ("produtos", "galeria_produto"): (Acao.GERENCIAR_PRODUTOS, None),
        ("produtos", "excluir_imagem_produto"): (Acao.GERENCIAR_PRODUTOS, None),
        ("produtos", "inativar_produto"): (Acao.GERENCIAR_PRODUTOS, None),
        ("produtos", "reativar_produto"): (Acao.GERENCIAR_PRODUTOS, None),
        ("estoque", "nova_entrada"): (Acao.MOVIMENTAR_ESTOQUE, None),
        ("estoque", "nova_saida"): (Acao.MOVIMENTAR_ESTOQUE, None),
        ("estoque", "ajuste_estoque"): (Acao.MOVIMENTAR_ESTOQUE, None),
        ("estoque", "novo_inventario"): (Acao.GERENCIAR_INVENTARIO, None),
        ("estoque", "conferir_inventario"): (Acao.GERENCIAR_INVENTARIO, {"POST"}),
        ("estoque", "finalizar_inventario"): (Acao.GERENCIAR_INVENTARIO, None),
        ("vendas", "alterar_vendedor"): (Acao.ALTERAR_VENDEDOR, None),
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        resolver_match = request.resolver_match

        if resolver_match is None:
            return None

        if (
            request.user.is_authenticated
            and request.user.primeiro_acesso
            and resolver_match.url_name != "primeiro_acesso"
        ):
            return redirect("usuarios:primeiro_acesso")

        if resolver_match.url_name == "primeiro_acesso":
            return None

        regra_acao = self.ACOES_POR_ROTA.get(
            (resolver_match.namespace, resolver_match.url_name)
        )

        if regra_acao is not None:
            acao, metodos = regra_acao
            deve_validar = metodos is None or request.method in metodos

            if deve_validar and not usuario_pode_executar(request.user, acao):
                raise PermissionDenied(
                    "Seu perfil não possui permissão para executar esta ação."
                )

        modulo = self.MODULOS_POR_NAMESPACE.get(
            resolver_match.namespace
        )

        if modulo is None:
            modulo = self.MODULOS_POR_URL.get(
                resolver_match.url_name
            )

        if modulo is None:
            return None

        if not request.user.is_authenticated:
            return redirect_to_login(
                request.get_full_path(),
                settings.LOGIN_URL,
            )

        # Sessões anteriores à seleção de operação pertencem ao legado da
        # Distribuidora. O login normal continua direcionando para a escolha.
        operacao = obter_operacao_ativa(request) or "distribuidora"

        if not operacao_tem_modulo(operacao, modulo):
            messages.error(
                request,
                "Este módulo não pertence à operação selecionada.",
            )
            if operacao == USE_HELVI:
                return redirect("dashboard_use_helvi")
            return redirect("dashboard")

        if (
            operacao == USE_HELVI
            and (resolver_match.namespace, resolver_match.url_name)
            in self.ROTAS_EXCLUSIVAS_DISTRIBUIDORA
        ):
            messages.error(
                request,
                "Esta página financeira usa dados comerciais da Distribuidora.",
            )
            return redirect("eventos:financeiro")

        # O Financeiro pode consultar uma venda específica e corrigir seu
        # vendedor mediante senha, sem receber acesso ao restante do módulo.
        if (
            request.user.perfil == "FIN"
            and resolver_match.namespace == "vendas"
            and resolver_match.url_name in {
                "ficha",
                "alterar_vendedor",
                "cancelar",
                "pdf",
            }
        ):
            return None

        if usuario_tem_permissao(
            request.user,
            modulo,
        ):
            return None

        messages.error(
            request,
            "Você não possui permissão para acessar esta página.",
        )
        return redirect("dashboard")
