from decimal import Decimal

from django.db import transaction
from django.db.models import Sum

from compras.models import Compra


@transaction.atomic
def registrar_pagamento_compra(compra, form, usuario):
    """
    Registra um pagamento e mantém o resumo financeiro da compra
    sincronizado com o histórico de pagamentos.
    """

    compra = Compra.objects.select_for_update().get(pk=compra.pk)

    if compra.status == Compra.STATUS_CANCELADA:
        raise ValueError(
            "Não é possível registrar pagamento em uma compra cancelada."
        )

    pagamento = form.save(commit=False)
    valor_pagamento = pagamento.valor

    if compra.saldo_a_pagar <= 0:
        raise ValueError(
            "Esta compra já está totalmente paga."
        )

    if valor_pagamento > compra.saldo_a_pagar:
        raise ValueError(
            "O valor informado é maior que o saldo a pagar."
        )

    pagamento.compra = compra
    pagamento.registrado_por = usuario
    pagamento.save()

    total_pago = (
        compra.pagamentos.aggregate(total=Sum("valor"))["total"]
        or Decimal("0.00")
    )

    compra.valor_pago = total_pago
    compra.atualizar_status_pagamento()
    compra.save()

    return pagamento