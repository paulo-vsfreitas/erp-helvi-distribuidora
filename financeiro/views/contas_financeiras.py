from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from financeiro.forms import ContaFinanceiraForm
from financeiro.models import ContaFinanceira
from financeiro.services.conta_financeira_service import (
    inativar_conta_financeira as inativar_conta_service,
    listar_contas_financeiras,
    obter_dados_ficha_conta_financeira,
    reativar_conta_financeira as reativar_conta_service,
    salvar_conta_financeira,
)
from usuarios.decorators import perfil_requerido


@login_required
@perfil_requerido("ADM", "GER", "FIN")
def lista_contas_financeiras(request):
    busca = request.GET.get("busca", "")
    tipo = request.GET.get("tipo", "")
    status = request.GET.get("status", "ativas")

    dados = listar_contas_financeiras(
        busca=busca,
        tipo=tipo,
        status=status,
    )

    indicadores = dados["indicadores"]
    conta_padrao = indicadores["conta_padrao"]

    cards = [
        {
            "titulo": "Total de contas",
            "valor": indicadores["total"],
            "icone": "bi bi-wallet2",
            "cor": "primary",
        },
        {
            "titulo": "Contas ativas",
            "valor": indicadores["ativas"],
            "icone": "bi bi-check-circle",
            "cor": "success",
        },
        {
            "titulo": "Contas inativas",
            "valor": indicadores["inativas"],
            "icone": "bi bi-slash-circle",
            "cor": "secondary",
        },
        {
            "titulo": "Conta padrão",
            "valor": (
                conta_padrao.nome
                if conta_padrao
                else "Não definida"
            ),
            "icone": "bi bi-star",
            "cor": "warning",
        },
    ]

    contexto = {
        "contas": dados["contas"],
        "cards": cards,
        "busca": busca,
        "tipo_selecionado": tipo,
        "status_selecionado": status,
        "tipos": ContaFinanceira.TIPO_CHOICES,
    }

    return render(
        request,
        "financeiro/lista_contas_financeiras.html",
        contexto,
    )


@login_required
@perfil_requerido("ADM", "GER", "FIN")
def nova_conta_financeira(request):
    if request.method == "POST":
        form = ContaFinanceiraForm(request.POST)

        if form.is_valid():
            conta = salvar_conta_financeira(form)

            messages.success(
                request,
                "Conta financeira cadastrada com sucesso.",
            )

            return redirect(
                "financeiro:ficha_conta_financeira",
                pk=conta.pk,
            )

    else:
        form = ContaFinanceiraForm(
            initial={
                "ativo": True,
            }
        )

    return render(
        request,
        "financeiro/form_conta_financeira.html",
        {
            "form": form,
            "titulo": "Nova conta financeira",
            "subtitulo": (
                "Cadastre uma conta bancária, caixa, carteira "
                "digital ou outro local de movimentação financeira."
            ),
        },
    )


@login_required
@perfil_requerido("ADM", "GER", "FIN")
def editar_conta_financeira(request, pk):
    conta = get_object_or_404(
        ContaFinanceira,
        pk=pk,
    )

    if request.method == "POST":
        form = ContaFinanceiraForm(
            request.POST,
            instance=conta,
        )

        if form.is_valid():
            try:
                conta = salvar_conta_financeira(form)

            except ValueError as erro:
                form.add_error(
                    None,
                    str(erro),
                )

            else:
                messages.success(
                    request,
                    "Conta financeira atualizada com sucesso.",
                )

                return redirect(
                    "financeiro:ficha_conta_financeira",
                    pk=conta.pk,
                )

    else:
        form = ContaFinanceiraForm(
            instance=conta,
        )

    return render(
        request,
        "financeiro/form_conta_financeira.html",
        {
            "form": form,
            "conta": conta,
            "titulo": "Editar conta financeira",
            "subtitulo": (
                "Atualize os dados cadastrais da conta selecionada."
            ),
        },
    )


@login_required
@perfil_requerido("ADM", "GER", "FIN")
def ficha_conta_financeira(request, pk):
    conta = get_object_or_404(
        ContaFinanceira,
        pk=pk,
    )

    dados_ficha = obter_dados_ficha_conta_financeira(
        conta
    )

    url_extrato = (
        reverse("financeiro:lista_movimentacoes")
        + f"?conta_financeira={conta.pk}"
    )

    contexto = {
        "conta": conta,
        "url_extrato": url_extrato,
        **dados_ficha,
    }

    return render(
        request,
        "financeiro/ficha_conta_financeira.html",
        contexto,
    )


@login_required
@perfil_requerido("ADM", "GER", "FIN")
def inativar_conta_financeira(request, pk):
    conta = get_object_or_404(
        ContaFinanceira,
        pk=pk,
    )

    if request.method != "POST":
        return redirect(
            "financeiro:ficha_conta_financeira",
            pk=conta.pk,
        )

    try:
        inativar_conta_service(conta)

        messages.success(
            request,
            "Conta financeira inativada com sucesso.",
        )

    except ValueError as erro:
        messages.warning(request, str(erro))

    return redirect(
        "financeiro:ficha_conta_financeira",
        pk=conta.pk,
    )


@login_required
@perfil_requerido("ADM", "GER", "FIN")
def reativar_conta_financeira(request, pk):
    conta = get_object_or_404(
        ContaFinanceira,
        pk=pk,
    )

    if request.method != "POST":
        return redirect(
            "financeiro:ficha_conta_financeira",
            pk=conta.pk,
        )

    try:
        reativar_conta_service(conta)

        messages.success(
            request,
            "Conta financeira reativada com sucesso.",
        )

    except ValueError as erro:
        messages.warning(request, str(erro))

    return redirect(
        "financeiro:ficha_conta_financeira",
        pk=conta.pk,
    )