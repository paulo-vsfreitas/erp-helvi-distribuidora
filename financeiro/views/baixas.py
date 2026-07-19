from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render

from financeiro.forms import BaixaPagarForm
from financeiro.models import ParcelaPagar
from financeiro.services.baixa_service import registrar_baixa


@login_required
def registrar_baixa_view(request, parcela_id):
    """
    Registro de baixa financeira de uma parcela.

    Toda a regra de negócio permanece no service.
    Esta view apenas coordena formulário,
    mensagens e redirecionamentos.
    """

    parcela = get_object_or_404(
        ParcelaPagar.objects.select_related(
            "conta_pagar",
            "conta_pagar__fornecedor",
        ),
        pk=parcela_id,
    )

    if request.method == "POST":

        form = BaixaPagarForm(
            request.POST,
            parcela=parcela,
        )

        if form.is_valid():

            try:

                registrar_baixa(
                    parcela=parcela,
                    conta_financeira=form.cleaned_data["conta_financeira"],
                    data_pagamento=form.cleaned_data["data_pagamento"],
                    valor=form.cleaned_data["valor"],
                    juros=form.cleaned_data["juros"],
                    multa=form.cleaned_data["multa"],
                    desconto=form.cleaned_data["desconto"],
                    forma_pagamento=form.cleaned_data["forma_pagamento"],
                    observacao=form.cleaned_data["observacao"],
                    usuario=request.user,
                )

                messages.success(
                    request,
                    "Baixa financeira registrada com sucesso."
                )

                return redirect(
                    "financeiro:ficha_conta_pagar",
                    parcela.conta_pagar.pk,
                )

            except ValidationError as exc:

                if hasattr(exc, "messages"):
                    for erro in exc.messages:
                        messages.error(request, erro)
                else:
                    messages.error(request, str(exc))

    else:

        form = BaixaPagarForm(
            parcela=parcela,
        )

    return render(
        request,
        "financeiro/registrar_baixa.html",
        {
            "form": form,
            "parcela": parcela,
            "conta": parcela.conta_pagar,
        },
    )