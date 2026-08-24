from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect, render

from financeiro.forms import ContaReceberForm
from financeiro.models import ContaReceber
from financeiro.services.conta_receber_service import (
    criar_conta_receber_manual,
    listar_contas_receber,
    obter_dados_ficha_conta_receber,
)
from usuarios.decorators import perfil_requerido
from core.services.operacao_service import obter_operacao_ativa


def _codigo_operacao(request):
    ativa = obter_operacao_ativa(request)
    return ativa.codigo if ativa else "distribuidora"


@login_required
@perfil_requerido("ADM", "GER", "FIN")
def lista_contas_receber(request):
    contexto = listar_contas_receber(request)

    return render(
        request,
        "financeiro/lista_contas_receber.html",
        contexto,
    )


@login_required
@perfil_requerido("ADM", "GER", "FIN")
def nova_conta_receber(request):
    if request.method == "POST":
        form = ContaReceberForm(request.POST)

        if form.is_valid():
            conta = criar_conta_receber_manual(
                dados={**form.cleaned_data.copy(), "operacao": _codigo_operacao(request)},
                usuario=request.user,
            )

            messages.success(
                request,
                "Conta a Receber cadastrada com sucesso.",
            )

            return redirect(
                "financeiro:ficha_conta_receber",
                pk=conta.pk,
            )
    else:
        form = ContaReceberForm()

    return render(
        request,
        "financeiro/form_conta_receber.html",
        {
            "form": form,
            "titulo": "Nova Conta a Receber",
            "subtitulo": (
                "Cadastre uma receita e defina suas condições "
                "de vencimento."
            ),
        },
    )


@login_required
@perfil_requerido("ADM", "GER", "FIN")
def ficha_conta_receber(request, pk):
    try:
        contexto = obter_dados_ficha_conta_receber(pk)
        if contexto["conta"].operacao != _codigo_operacao(request):
            raise ContaReceber.DoesNotExist
    except ContaReceber.DoesNotExist as erro:
        raise Http404(
            "Conta a Receber não encontrada."
        ) from erro

    return render(
        request,
        "financeiro/ficha_conta_receber.html",
        contexto,
    )
