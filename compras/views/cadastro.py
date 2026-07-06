from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from compras.forms import CompraForm
from compras.services.compra_service import criar_compra_com_itens


@login_required
def nova_compra(request):
    form = CompraForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        try:
            compra = criar_compra_com_itens(
                form=form,
                usuario=request.user,
                post=request.POST,
            )

            messages.success(request, f"Compra #{compra.numero} cadastrada com sucesso.")
            return redirect("compras:lista")

        except ValueError as erro:
            messages.error(request, erro)

    return render(
        request,
        "compras/nova_compra.html",
        {
            "form": form,
        },
    )