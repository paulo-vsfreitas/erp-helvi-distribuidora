from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def perfil_requerido(*perfis_permitidos):
    """
    Decorator para restringir acesso às views conforme o perfil do usuário.
    Exemplo:

    @perfil_requerido("ADM")

    ou

    @perfil_requerido("ADM", "GER")
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
                return redirect("core:dashboard")

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator