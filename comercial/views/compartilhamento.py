import logging

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from comercial.forms import CompartilhamentoOrcamentoForm
from comercial.models import Orcamento
from comercial.services.compartilhamento_service import (
    compartilhar_orcamento,
)
from usuarios.decorators import permissao_requerida
from usuarios.permissoes import Modulo


logger = logging.getLogger(__name__)


@permissao_requerida(Modulo.VENDAS)
@require_POST
def compartilhar_orcamento_view(request, numero):
    orcamento = get_object_or_404(
        Orcamento.objects
        .select_related(
            "cliente",
            "vendedor",
        )
        .prefetch_related(
            "itens__produto",
            "itens__produto__marca",
        ),
        numero=numero,
    )

    form = CompartilhamentoOrcamentoForm(request.POST)

    if not form.is_valid():
        mensagem = next(
            iter(form.errors.values())
        )[0]

        messages.error(request, mensagem)

        return redirect(
            "comercial:ficha",
            numero=numero,
        )

    try:
        resultado = compartilhar_orcamento(
            orcamento=orcamento,
            dados=form.cleaned_data,
            usuario=request.user,
        )

    except Exception:
        logger.exception(
            "Falha ao compartilhar o orçamento %s.",
            orcamento.pk,
        )
        messages.error(
            request,
            "Não foi possível compartilhar o orçamento. Tente novamente.",
        )

        return redirect(
            "comercial:ficha",
            numero=numero,
        )

    if resultado.canal == "whatsapp":
        return redirect(resultado.url)

    messages.success(
        request,
        resultado.mensagem,
    )

    return redirect(
        "comercial:ficha",
        numero=numero,
    )
