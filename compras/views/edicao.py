from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from compras.forms import CompraForm
from compras.models import Compra
from compras.services.compra_service import (
    atualizar_compra_com_itens,
    obter_itens_para_formulario,
)


@login_required
def editar_compra(request, pk):
    compra = get_object_or_404(
        Compra.objects.prefetch_related(
            "itens__produto"
        ),
        pk=pk,
    )

    if (
        compra.entrada_estoque_realizada
        or compra.status == Compra.STATUS_RECEBIDA
    ):
        messages.warning(
            request,
            "Esta compra já foi recebida no estoque "
            "e não pode ser editada.",
        )

        return redirect(
            "compras:ficha",
            pk=compra.pk,
        )

    form = CompraForm(
        request.POST or None,
        instance=compra,
    )

    if request.method == "POST":
        itens_edicao = obter_itens_para_formulario(
            post=request.POST
        )

        if form.is_valid():
            try:
                compra = atualizar_compra_com_itens(
                    compra=compra,
                    form=form,
                    post=request.POST,
                )

                messages.success(
                    request,
                    f"Compra #{compra.numero} "
                    "atualizada com sucesso.",
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
                "Verifique os campos do formulário.",
            )

    else:
        itens_edicao = obter_itens_para_formulario(
            compra=compra
        )

    return render(
        request,
        "compras/editar_compra.html",
        {
            "form": form,
            "compra": compra,
            "itens_edicao": itens_edicao,
        },
    )