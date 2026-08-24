from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect, render

from financeiro.forms import ContaPagarForm
from financeiro.models import ContaPagar
from financeiro.services.conta_pagar_service import (
    criar_conta_pagar_manual,
    listar_contas_pagar,
    obter_dados_ficha_conta_pagar,
)
from usuarios.decorators import perfil_requerido
from core.services.operacao_service import obter_operacao_ativa


def _codigo_operacao(request):
    ativa = obter_operacao_ativa(request)
    return ativa.codigo if ativa else "distribuidora"


@login_required
@perfil_requerido("ADM", "GER", "FIN")
def lista_contas_pagar(request):
    contexto = listar_contas_pagar(request)

    return render(
        request,
        "financeiro/lista_contas_pagar.html",
        contexto,
    )


@login_required
@perfil_requerido("ADM", "GER", "FIN")
def nova_conta_pagar(request):
    if request.method == "POST":
        form = ContaPagarForm(request.POST)

        if form.is_valid():
            conta = criar_conta_pagar_manual(
                dados={**form.cleaned_data.copy(), "operacao": _codigo_operacao(request)},
                usuario=request.user,
            )

            messages.success(
                request,
                "Conta a Pagar cadastrada com sucesso.",
            )

            return redirect(
                "financeiro:ficha_conta_pagar",
                pk=conta.pk,
            )
    else:
        form = ContaPagarForm()

    return render(
        request,
        "financeiro/form_conta_pagar.html",
        {
            "form": form,
            "titulo": "Nova Conta a Pagar",
            "subtitulo": (
                "Cadastre uma despesa e defina suas condições "
                "de vencimento."
            ),
        },
    )


@login_required
@perfil_requerido("ADM", "GER", "FIN")
def ficha_conta_pagar(request, pk):
    try:
        contexto = obter_dados_ficha_conta_pagar(pk)
        if contexto["conta"].operacao != _codigo_operacao(request):
            raise ContaPagar.DoesNotExist
    except ContaPagar.DoesNotExist as erro:
        raise Http404(
            "Conta a Pagar não encontrada."
        ) from erro

    return render(
        request,
        "financeiro/ficha_conta_pagar.html",
        contexto,
    )
