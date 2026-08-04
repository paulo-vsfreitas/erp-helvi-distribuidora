import logging

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from usuarios.decorators import permissao_requerida
from usuarios.permissoes import Modulo
from vendas.models import Venda
from vendas.services.cancelamento_service import cancelar_venda


logger = logging.getLogger(__name__)


@permissao_requerida(Modulo.VENDAS)
@require_POST
def cancelar_venda_view(request, numero):
    venda = get_object_or_404(Venda, numero=numero)

    try:
        cancelar_venda(
            venda=venda,
            usuario=request.user,
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
