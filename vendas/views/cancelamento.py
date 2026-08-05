import logging

from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from usuarios.models import Usuario
from vendas.models import Venda
from vendas.services.cancelamento_service import cancelar_venda


logger = logging.getLogger(__name__)


@login_required
@require_POST
def cancelar_venda_view(request, numero):
    venda = get_object_or_404(Venda, numero=numero)

    administrador = authenticate(
        request=request,
        username=(request.POST.get("administrador_usuario") or "").strip(),
        password=request.POST.get("administrador_senha") or "",
    )

    if not administrador or not administrador.is_active or not (
        administrador.is_superuser
        or administrador.perfil == Usuario.Perfil.ADMINISTRADOR
    ):
        messages.error(
            request,
            "Usuário ou senha de administrador inválidos.",
        )
        return redirect("vendas:ficha", numero=numero)

    try:
        cancelar_venda(
            venda=venda,
            usuario=request.user,
            autorizado_por=administrador,
            motivo=request.POST.get("motivo"),
        )
    except ValidationError as erro:
        for mensagem in erro.messages:
            messages.error(request, mensagem)
    except Exception:
        logger.exception(
            "Falha inesperada ao cancelar a venda %s.",
            venda.pk,
        )
        messages.error(
            request,
            "Não foi possível cancelar a venda. Tente novamente.",
        )
    else:
        messages.success(
            request,
            "Venda cancelada e integrações estornadas com sucesso.",
        )

    return redirect("vendas:ficha", numero=numero)
