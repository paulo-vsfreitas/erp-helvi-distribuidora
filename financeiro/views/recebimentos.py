from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render

from financeiro.forms import RecebimentoContaForm
from financeiro.models import ParcelaReceber
from financeiro.services import registrar_recebimento


@login_required
def registrar_recebimento_view(request, parcela_id):
    parcela = get_object_or_404(
        ParcelaReceber.objects.select_related(
            "conta_receber",
            "conta_receber__cliente",
        ),
        pk=parcela_id,
    )

    if request.method == "POST":
        form = RecebimentoContaForm(
            request.POST,
            parcela=parcela,
        )

        if form.is_valid():
            try:
                registrar_recebimento(
                    parcela=parcela,
                    conta_financeira=form.cleaned_data["conta_financeira"],
                    data_recebimento=form.cleaned_data["data_recebimento"],
                    valor=form.cleaned_data["valor"],
                    juros=form.cleaned_data["juros"],
                    multa=form.cleaned_data["multa"],
                    desconto=form.cleaned_data["desconto"],
                    forma_recebimento=form.cleaned_data["forma_recebimento"],
                    observacao=form.cleaned_data["observacao"],
                    usuario=request.user,
                )

                messages.success(
                    request,
                    "Recebimento registrado com sucesso.",
                )

                return redirect(
                    "financeiro:ficha_conta_receber",
                    pk=parcela.conta_receber.pk,
                )

            except ValidationError as e:
                if hasattr(e, "messages"):
                    for erro in e.messages:
                        messages.error(request, erro)
                else:
                    messages.error(request, str(e))

    else:
        form = RecebimentoContaForm(
            parcela=parcela,
        )

    context = {
        "form": form,
        "parcela": parcela,
        "conta": parcela.conta_receber,
        "ficha_titulo": "Registrar Recebimento",
        "ficha_subtitulo": (
            f"Conta #{parcela.conta_receber.numero}"
        ),
    }

    return render(
        request,
        "financeiro/registrar_recebimento.html",
        context,
    )

