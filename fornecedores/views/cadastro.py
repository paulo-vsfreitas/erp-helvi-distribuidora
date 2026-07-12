from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.urls import reverse

from fornecedores.forms import FornecedorForm
from fornecedores.services.fornecedor_service import criar_fornecedor
from usuarios.permissoes import Modulo, usuario_tem_permissao


@login_required
def cadastrar_fornecedor(request):
    if not usuario_tem_permissao(
        request.user,
        Modulo.FORNECEDORES,
    ):
        raise PermissionDenied

    if request.method == "POST":
        form = FornecedorForm(request.POST)

        if form.is_valid():
            fornecedor = criar_fornecedor(form)

            messages.success(
                request,
                (
                    f"Fornecedor {fornecedor.codigo} cadastrado "
                    "com sucesso."
                ),
            )

            return redirect("fornecedores:dashboard")
    else:
        form = FornecedorForm()

    return render(
        request,
        "fornecedores/form_fornecedor.html",
        {
            "form": form,
            "titulo": "Novo fornecedor",
            "subtitulo": (
                "Cadastre os dados de identificação, contato, "
                "endereço e condições comerciais."
            ),
            "cancelar_url": reverse(
            "fornecedores:dashboard"
        ),
        },
    )