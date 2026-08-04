from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from comercial.models import Orcamento
from comercial.services import (
    aprovar_orcamento,
    cancelar_orcamento,
    enviar_orcamento,
    rejeitar_orcamento,
)
from usuarios.decorators import permissao_requerida
from usuarios.permissoes import Modulo


SERVICOS_STATUS = {
    Orcamento.Status.ENVIADO: enviar_orcamento,
    Orcamento.Status.APROVADO: aprovar_orcamento,
    Orcamento.Status.REJEITADO: rejeitar_orcamento,
    Orcamento.Status.CANCELADO: cancelar_orcamento,
}


@permissao_requerida(Modulo.VENDAS)
@require_POST
def alterar_status(request, numero, status):
    orcamento = get_object_or_404(
        Orcamento,
        numero=numero,
    )

    try:
        servico = SERVICOS_STATUS.get(status)

        if servico is None:
            raise ValidationError("Status solicitado inválido.")

        servico(orcamento)

    except ValidationError as erro:
        for mensagem in erro.messages:
            messages.error(request, mensagem)

    else:
        messages.success(
            request,
            "Status atualizado com sucesso.",
        )

    return redirect(
        "comercial:ficha",
        numero=numero,
    )
