from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from comercial.models import Orcamento
from comercial.services.conversao_service import (
    converter_orcamento_em_venda,
)
from usuarios.decorators import permissao_requerida
from usuarios.permissoes import Modulo


@permissao_requerida(Modulo.VENDAS)
@require_POST
def converter_orcamento(request, numero):
    orcamento = get_object_or_404(
        Orcamento,
        numero=numero,
    )

    try:
        venda = converter_orcamento_em_venda(
            orcamento,
            usuario=request.user,
        )

        messages.success(
            request,
            f"Orçamento convertido na Venda #{venda.numero} com sucesso.",
        )

    except ValidationError as erro:
        for mensagem in erro.messages:
            messages.error(request, mensagem)

    return redirect(
        "comercial:ficha",
        numero=orcamento.numero,
    )
