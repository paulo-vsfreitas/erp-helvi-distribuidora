from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from compras.forms import PagamentoCompraForm
from compras.models import Compra
from compras.services.pagamento_service import registrar_pagamento_compra


@login_required
@require_POST
def registrar_pagamento(request, pk):
    compra = get_object_or_404(
        Compra,
        pk=pk,
    )

    form = PagamentoCompraForm(
        request.POST,
        compra=compra,
    )

    if not form.is_valid():
        erros_valor = form.errors.get("valor")
        erros_gerais = form.non_field_errors()

        if erros_valor:
            mensagem_erro = erros_valor[0]
        elif erros_gerais:
            mensagem_erro = erros_gerais[0]
        else:
            mensagem_erro = (
                "Não foi possível registrar o pagamento. "
                "Verifique os dados informados."
            )

        messages.error(
            request,
            mensagem_erro,
        )

        return redirect(
            "compras:ficha",
            pk=compra.pk,
        )

    try:
        registrar_pagamento_compra(
            compra=compra,
            form=form,
            usuario=request.user,
        )

    except ValueError as erro:
        messages.error(
            request,
            str(erro),
        )

        return redirect(
            "compras:ficha",
            pk=compra.pk,
        )

    messages.success(
        request,
        "Pagamento registrado com sucesso.",
    )

    return redirect(
        "compras:ficha",
        pk=compra.pk,
    )