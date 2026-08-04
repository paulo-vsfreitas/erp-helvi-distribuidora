import logging

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from usuarios.decorators import permissao_requerida
from usuarios.permissoes import Modulo
from vendas.models import Venda
from vendas.services.finalizacao_service import finalizar_venda


logger = logging.getLogger(__name__)


@permissao_requerida(Modulo.VENDAS)
@require_POST
def finalizar_venda_view(request, numero):
    try:
        venda = Venda.objects.get(numero=numero)

        finalizar_venda(
            venda_id=venda.pk,
            usuario=request.user,
        )

    except Venda.DoesNotExist:
        messages.error(
            request,
            "Venda não encontrada.",
        )

        return redirect("vendas:lista")

    except ValidationError as erro:
        mensagens = getattr(
            erro,
            "messages",
            [str(erro)],
        )

        for mensagem in mensagens:
            messages.error(
                request,
                mensagem,
            )

    except Exception:
        logger.exception(
            "Falha inesperada ao finalizar a venda nº %s.",
            numero,
        )
        messages.error(
            request,
            "Não foi possível finalizar a venda. Tente novamente.",
        )

    else:
        messages.success(
            request,
            (
                f"Venda nº {venda.numero} finalizada. "
                "O estoque foi baixado e o financeiro gerado."
            ),
        )

    return redirect(
        "vendas:ficha",
        numero=numero,
    )
