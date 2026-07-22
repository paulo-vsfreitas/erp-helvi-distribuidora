from django.utils import timezone

from comercial.models import Orcamento


def alterar_status_orcamento(orcamento, novo_status):

    permitidos = {
        Orcamento.Status.RASCUNHO: [
            Orcamento.Status.ENVIADO,
            Orcamento.Status.CANCELADO,
        ],
        Orcamento.Status.ENVIADO: [
            Orcamento.Status.APROVADO,
            Orcamento.Status.REJEITADO,
        ],
    }

    if novo_status not in permitidos.get(orcamento.status, []):
        raise ValueError("Transição de status inválida.")

    agora = timezone.now()

    match novo_status:

        case Orcamento.Status.ENVIADO:
            orcamento.status = novo_status
            orcamento.enviado_em = agora

        case Orcamento.Status.APROVADO:
            orcamento.status = novo_status
            orcamento.aprovado_em = agora

        case Orcamento.Status.REJEITADO:
            orcamento.status = novo_status
            orcamento.rejeitado_em = agora

        case Orcamento.Status.CANCELADO:
            orcamento.status = novo_status
            orcamento.cancelado_em = agora

        case _:
            raise ValueError("Status inválido.")

    orcamento.save()

    return orcamento