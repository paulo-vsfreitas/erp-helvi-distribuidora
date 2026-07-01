from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from usuarios.permissoes import usuario_tem_permissao


def perfil_requerido(*perfis_permitidos):
    """
    Restringe acesso por perfil específico.
    """

    def decorator(view_func):

        @login_required
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            if request.user.perfil not in perfis_permitidos:
                messages.error(
                    request,
                    "Você não possui permissão para acessar esta página.",
                )
                return redirect("dashboard")

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def permissao_requerida(modulo):
    """
    Restringe acesso com base nas permissões do perfil do usuário.
    """

    def decorator(view_func):

        @login_required
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            if not usuario_tem_permissao(request.user, modulo):
                messages.error(
                    request,
                    "Você não possui permissão para acessar esta página.",
                )
                return redirect("dashboard")

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator