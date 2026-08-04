from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.conf import settings
from django.shortcuts import redirect

from usuarios.permissoes import Modulo, usuario_tem_permissao


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
    }

    MODULOS_POR_URL = {
        "central_relatorios": Modulo.RELATORIOS,
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
