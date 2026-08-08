from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render

from estoque.forms import EntradaEstoqueForm
from estoque.services import registrar_entrada_estoque
from django.http import JsonResponse

from produtos.models import VariacaoCor


@login_required
def nova_entrada(request):
    if request.method == "POST":
        form = EntradaEstoqueForm(request.POST)

        if form.is_valid():
            try:
                registrar_entrada_estoque(
                    produto=form.cleaned_data["produto"],
                    variacao_cor=form.cleaned_data["variacao_cor"],
                    quantidade=form.cleaned_data["quantidade"],
                    usuario=request.user,
                    origem=form.cleaned_data["origem"],
                    local=form.cleaned_data["local"],
                    observacao=form.cleaned_data["observacao"],
                )

            except ValidationError as erro:
                form.add_error(
                    None,
                    erro.messages[0],
                )
            else:
                messages.success(
                    request,
                    "Entrada de estoque registrada com sucesso.",
                )

                return redirect(
                    "estoque:lista_movimentacoes"
                )

    else:
        form = EntradaEstoqueForm()

    return render(
        request,
        "estoque/nova_entrada.html",
        {
            "form": form,
        },
    )

@login_required
def variacoes_produto(request):
    produto_id = request.GET.get("produto_id")

    if not produto_id:
        return JsonResponse(
            {
                "variacoes": [],
            }
        )

    variacoes = (
        VariacaoCor.objects
        .filter(
            produto_id=produto_id,
        )
        .order_by(
            "codigo",
            "nome",
        )
    )

    dados = [
        {
            "id": variacao.pk,
            "nome": variacao.nome or "",
            "codigo": variacao.codigo or "",
            "estoque": variacao.estoque or 0,
        }
        for variacao in variacoes
    ]

    return JsonResponse(
        {
            "variacoes": dados,
        }
    )