from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect

from comercial.models import Orcamento
from comercial.services.duplicacao_service import duplicar_orcamento


@login_required
def duplicar_orcamento_view(request, numero):
    if request.method != "POST":
        return redirect(
            "comercial:ficha",
            numero=numero,
        )

    orcamento = get_object_or_404(
        Orcamento,
        numero=numero,
    )

    try:
        novo_orcamento = duplicar_orcamento(
            orcamento=orcamento,
            responsavel=request.user,
        )

    except ValidationError as erro:
        mensagem = (
            erro.messages[0]
            if erro.messages
            else "Não foi possível duplicar o orçamento."
        )

        messages.error(request, mensagem)

        return redirect(
            "comercial:ficha",
            numero=numero,
        )

    messages.success(
        request,
        (
            f"{orcamento.codigo} foi duplicado com sucesso. "
            f"Novo orçamento: {novo_orcamento.codigo}."
        ),
    )

    return redirect(
        "comercial:editar",
        numero=novo_orcamento.numero,
    )