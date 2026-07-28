from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render

from financeiro.models import ContaFinanceira
from vendas.forms import VendaForm
from vendas.services.processamento_venda_service import (
    processar_nova_venda,
)


@login_required
def nova_venda(request):
    if request.method == "POST":
        form = VendaForm(request.POST)

        if form.is_valid():
            try:
                resultado = processar_nova_venda(
                    form=form,
                    post=request.POST,
                    usuario=request.user,
                )
            except ValidationError as erro:
                mensagens = getattr(
                    erro,
                    "messages",
                    [str(erro)],
                )

                for mensagem in mensagens:
                    messages.error(
                        request,
                        mensagem,
                    )
            else:
                venda = resultado["venda"]

                if resultado["finalizada"]:
                    mensagem = (
                        f"Venda nº {venda.numero} finalizada "
                        "com sucesso."
                    )

                    if resultado["troco"] > 0:
                        mensagem += (
                            f" Troco: R$ "
                            f"{resultado['troco']:.2f}."
                        )

                    messages.success(
                        request,
                        mensagem,
                    )

                    return redirect(
                        "vendas:ficha",
                        venda.pk,
                    )

                messages.success(
                    request,
                    (
                        f"Venda nº {venda.numero} salva "
                        "em aberto com sucesso."
                    ),
                )

                return redirect(
                    "vendas:lista",
                )
    else:
        form = VendaForm()

    contas_financeiras = (
        ContaFinanceira.objects
        .filter(ativo=True)
        .order_by(
            "-conta_padrao",
            "nome",
        )
    )

    return render(
        request,
        "vendas/nova.html",
        {
            "form": form,
        },
    )