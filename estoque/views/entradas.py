from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from estoque.forms import EntradaEstoqueForm
from estoque.services import registrar_entrada_estoque


@login_required
def nova_entrada(request):
    if request.method == "POST":
        form = EntradaEstoqueForm(request.POST)

        if form.is_valid():
            registrar_entrada_estoque(
                produto=form.cleaned_data["produto"],
                quantidade=form.cleaned_data["quantidade"],
                usuario=request.user,
                origem=form.cleaned_data["origem"],
                local=form.cleaned_data["local"],
                observacao=form.cleaned_data["observacao"],
            )

            messages.success(request, "Entrada de estoque registrada com sucesso.")
            return redirect("estoque:lista_movimentacoes")
    else:
        form = EntradaEstoqueForm()

    return render(
        request,
        "estoque/nova_entrada.html",
        {"form": form},
    )