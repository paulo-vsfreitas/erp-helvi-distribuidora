from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from compras.forms import CompraForm
from compras.services.compra_service import criar_compra_com_itens


@login_required
def nova_compra(request):
    form = CompraForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            try:
                compra = criar_compra_com_itens(
                    form=form,
                    usuario=request.user,
                    post=request.POST,
                )

                messages.success(request, f"Compra #{compra.numero} cadastrada com sucesso.")
                return redirect("compras:ficha", pk=compra.pk)

            except ValueError as erro:
                messages.error(request, str(erro))
        else:
            messages.error(request, "Não foi possível salvar. Verifique os dados da compra.")

    return render(
        request,
        "compras/nova_compra.html",
        {
            "form": form,
        },
    )