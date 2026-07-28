from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect

from vendas.models import Venda
from vendas.services.finalizacao_service import finalizar_venda


@login_required
def finalizar_venda_view(request, numero):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

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

    except Exception as erro:
        messages.error(
            request,
            f"Não foi possível finalizar a venda: {erro}",
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