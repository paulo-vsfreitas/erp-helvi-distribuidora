from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render

from fornecedores.views.listagem import montar_contexto_listagem
from usuarios.permissoes import Modulo, usuario_tem_permissao


@login_required
def dashboard(request):
    if not usuario_tem_permissao(
        request.user,
        Modulo.FORNECEDORES,
    ):
        raise PermissionDenied

    context = montar_contexto_listagem(request)

    return render(
        request,
        "fornecedores/dashboard.html",
        context,
    )
