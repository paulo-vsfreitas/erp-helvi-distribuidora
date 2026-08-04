from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from financeiro.models import BaixaPagar, RecebimentoConta
from financeiro.services.estorno_service import (
    estornar_baixa,
    estornar_recebimento,
)
from usuarios.decorators import perfil_requerido


def _mensagens_validacao(request, erro):
    for mensagem in getattr(erro, "messages", [str(erro)]):
        messages.error(request, mensagem)


@login_required
@perfil_requerido("ADM", "GER", "FIN")
@require_http_methods(["GET", "POST"])
def estornar_baixa_view(request, baixa_id):
    baixa = get_object_or_404(
        BaixaPagar.objects.select_related(
            "parcela__conta_pagar",
            "conta_financeira",
        ),
        pk=baixa_id,
    )
    conta = baixa.parcela.conta_pagar

    if request.method == "POST":
        try:
            estornar_baixa(
                baixa=baixa,
                usuario=request.user,
                motivo=request.POST.get("motivo"),
            )
        except ValidationError as erro:
            _mensagens_validacao(request, erro)
        else:
            messages.success(request, "Baixa estornada com sucesso.")
            return redirect("financeiro:ficha_conta_pagar", pk=conta.pk)

    return render(
        request,
        "financeiro/confirmar_estorno.html",
        {
            "tipo": "baixa",
            "titulo": "Estornar baixa",
            "subtitulo": (
                f"Conta #{conta.numero} — Parcela {baixa.parcela.numero}"
            ),
            "objeto": baixa,
            "valor": baixa.valor_movimentado,
            "data_operacao": baixa.data_pagamento,
            "conta_financeira": baixa.conta_financeira,
            "cancelar_url": reverse(
                "financeiro:ficha_conta_pagar",
                kwargs={"pk": conta.pk},
            ),
            "ja_estornado": baixa.estornada,
        },
    )


@login_required
@perfil_requerido("ADM", "GER", "FIN")
@require_http_methods(["GET", "POST"])
def estornar_recebimento_view(request, recebimento_id):
    recebimento = get_object_or_404(
        RecebimentoConta.objects.select_related(
            "parcela__conta_receber",
            "conta_financeira",
        ),
        pk=recebimento_id,
    )
    conta = recebimento.parcela.conta_receber

    if request.method == "POST":
        try:
            estornar_recebimento(
                recebimento=recebimento,
                usuario=request.user,
                motivo=request.POST.get("motivo"),
            )
        except ValidationError as erro:
            _mensagens_validacao(request, erro)
        else:
            messages.success(request, "Recebimento estornado com sucesso.")
            return redirect("financeiro:ficha_conta_receber", pk=conta.pk)

    return render(
        request,
        "financeiro/confirmar_estorno.html",
        {
            "tipo": "recebimento",
            "titulo": "Estornar recebimento",
            "subtitulo": (
                f"Conta #{conta.numero} — Parcela {recebimento.parcela.numero}"
            ),
            "objeto": recebimento,
            "valor": recebimento.valor_movimentado,
            "data_operacao": recebimento.data_recebimento,
            "conta_financeira": recebimento.conta_financeira,
            "cancelar_url": reverse(
                "financeiro:ficha_conta_receber",
                kwargs={"pk": conta.pk},
            ),
            "ja_estornado": recebimento.estornado,
        },
    )
