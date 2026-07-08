from django.db import transaction

from compras.models import PagamentoCompra


@transaction.atomic
def registrar_pagamento_compra(compra, form, usuario):
    pagamento = form.save(commit=False)
    pagamento.compra = compra
    pagamento.registrado_por = usuario
    pagamento.save()

    compra.valor_pago += pagamento.valor
    compra.atualizar_status_pagamento()
    compra.save()

    return pagamento