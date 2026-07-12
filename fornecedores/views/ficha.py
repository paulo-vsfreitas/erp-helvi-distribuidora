from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render

from fornecedores.models import Fornecedor
from fornecedores.services.ficha_service import (
    montar_contexto_ficha_fornecedor,
)
from usuarios.permissoes import Modulo, usuario_tem_permissao


@login_required
def ficha_fornecedor(request, pk):
    if not usuario_tem_permissao(
        request.user,
        Modulo.FORNECEDORES,
    ):
        raise PermissionDenied

    fornecedor = get_object_or_404(
        Fornecedor,
        pk=pk,
    )

    context = montar_contexto_ficha_fornecedor(
        fornecedor
    )

    return render(
        request,
        "fornecedores/ficha_fornecedor.html",
        context,
    )