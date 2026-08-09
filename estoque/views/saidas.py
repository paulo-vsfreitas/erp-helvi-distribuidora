from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render

from estoque.forms import SaidaEstoqueForm
from estoque.services import registrar_saida_estoque


@login_required
def nova_saida(request):
    if request.method == "POST":
        form = SaidaEstoqueForm(request.POST)

        if form.is_valid():
            try:
                registrar_saida_estoque(
                    produto=form.cleaned_data["produto"],
                    variacao_cor=form.cleaned_data[
                        "variacao_cor"
                    ],
                    quantidade=form.cleaned_data[
                        "quantidade"
                    ],
                    usuario=request.user,
                    origem=form.cleaned_data["origem"],
                    local=form.cleaned_data["local"],
                    observacao=form.cleaned_data[
                        "observacao"
                    ],
                )

            except ValidationError as erro:
                form.add_error(
                    None,
                    erro.messages[0],
                )

            else:
                messages.success(
                    request,
                    "Saída de estoque registrada com sucesso.",
                )

                return redirect(
                    "estoque:lista_movimentacoes"
                )

    else:
        form = SaidaEstoqueForm()

    return render(
        request,
        "estoque/nova_saida.html",
        {
            "form": form,
        },
    )