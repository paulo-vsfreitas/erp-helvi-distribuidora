from django.db import transaction

from compras.models import PagamentoCompra


@transaction.atomic
def cancelar_pagamento_compra(pagamento):
    compra = pagamento.compra

    compra.valor_pago -= pagamento.valor

    if compra.valor_pago < 0:
        compra.valor_pago = 0

    compra.atualizar_status_pagamento()
    compra.save()

    pagamento.delete()

    return compra