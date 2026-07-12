from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from compras.forms import CompraForm
from compras.services.compra_service import criar_compra_com_itens
from fornecedores.models import Fornecedor


@login_required
def nova_compra(request):
    fornecedor_inicial = None

    fornecedor_id = request.GET.get("fornecedor")

    if fornecedor_id:
        fornecedor_inicial = (
            Fornecedor.objects
            .filter(
                pk=fornecedor_id,
                ativo=True,
            )
            .first()
        )

    if request.method == "POST":
        form = CompraForm(request.POST)
    else:
        form = CompraForm(
            initial={
                "fornecedor": fornecedor_inicial,
            }
        )

    if request.method == "POST":
        if form.is_valid():
            try:
                compra = criar_compra_com_itens(
                    form=form,
                    usuario=request.user,
                    post=request.POST,
                )

                messages.success(
                    request,
                    f"Compra #{compra.numero} cadastrada com sucesso.",
                )

                return redirect(
                    "compras:ficha",
                    pk=compra.pk,
                )

            except ValueError as erro:
                messages.error(
                    request,
                    str(erro),
                )

        else:
            messages.error(
                request,
                "Não foi possível salvar. "
                "Verifique os dados da compra.",
            )

    return render(
        request,
        "compras/nova_compra.html",
        {
            "form": form,
            "fornecedor_inicial": fornecedor_inicial,
        },
    )