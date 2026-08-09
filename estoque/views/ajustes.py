from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render

from estoque.forms import AjusteEstoqueForm
from estoque.services import ajustar_estoque


@login_required
def ajuste_estoque(request):
    if request.method == "POST":
        form = AjusteEstoqueForm(
            request.POST
        )

        if form.is_valid():
            try:
                ajustar_estoque(
                    produto=form.cleaned_data[
                        "produto"
                    ],
                    variacao_cor=form.cleaned_data[
                        "variacao_cor"
                    ],
                    quantidade_correta=(
                        form.cleaned_data[
                            "quantidade_correta"
                        ]
                    ),
                    usuario=request.user,
                    motivo=form.cleaned_data[
                        "motivo"
                    ],
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
                    (
                        "Ajuste de estoque "
                        "registrado com sucesso."
                    ),
                )

                return redirect(
                    "estoque:lista_movimentacoes"
                )

    else:
        form = AjusteEstoqueForm()

    return render(
        request,
        "estoque/ajuste_estoque.html",
        {
            "form": form,
        },
    )