from decimal import Decimal

from django.db import transaction
from django.db.models import Sum

from compras.models import Compra, PagamentoCompra


@transaction.atomic
def cancelar_pagamento_compra(pagamento):
    """
    Cancela um pagamento e recalcula o resumo financeiro da compra
    com base nos pagamentos que permanecerem registrados.
    """

    pagamento = (
        PagamentoCompra.objects
        .select_for_update()
        .select_related("compra")
        .get(pk=pagamento.pk)
    )

    compra = Compra.objects.select_for_update().get(
        pk=pagamento.compra_id
    )

    pagamento.delete()

    total_pago = (
        compra.pagamentos.aggregate(total=Sum("valor"))["total"]
        or Decimal("0.00")
    )

    compra.valor_pago = total_pago
    compra.atualizar_status_pagamento()
    compra.save()

    return compra