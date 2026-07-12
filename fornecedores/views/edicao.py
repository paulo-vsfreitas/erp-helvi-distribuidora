from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from fornecedores.forms import FornecedorForm
from fornecedores.models import Fornecedor
from fornecedores.services.fornecedor_service import atualizar_fornecedor
from usuarios.permissoes import Modulo, usuario_tem_permissao


@login_required
def editar_fornecedor(request, pk):
    if not usuario_tem_permissao(
        request.user,
        Modulo.FORNECEDORES,
    ):
        raise PermissionDenied

    fornecedor = get_object_or_404(
        Fornecedor,
        pk=pk,
    )

    if request.method == "POST":
        form = FornecedorForm(
            request.POST,
            instance=fornecedor,
        )

        if form.is_valid():
            fornecedor = atualizar_fornecedor(form)

            messages.success(
                request,
                (
                    f"Fornecedor {fornecedor.codigo} atualizado "
                    "com sucesso."
                ),
            )

            return redirect(
                "fornecedores:ficha",
                pk=fornecedor.pk,
            )
    else:
        form = FornecedorForm(
            instance=fornecedor,
        )

    return render(
        request,
        "fornecedores/form_fornecedor.html",
        {
            "form": form,
            "fornecedor": fornecedor,
            "titulo": "Editar fornecedor",
            "subtitulo": (
                f"Atualize os dados cadastrais do fornecedor "
                f"{fornecedor.codigo}."
            ),
            "cancelar_url": reverse(
                "fornecedores:ficha",
                kwargs={"pk": fornecedor.pk},
            ),
            },
    )