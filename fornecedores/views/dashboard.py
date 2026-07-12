from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render

from fornecedores.models import Fornecedor
from usuarios.permissoes import Modulo, usuario_tem_permissao


@login_required
def dashboard(request):
    if not usuario_tem_permissao(
        request.user,
        Modulo.FORNECEDORES,
    ):
        raise PermissionDenied

    context = {
        "total_fornecedores": Fornecedor.objects.count(),
        "fornecedores_ativos": Fornecedor.objects.filter(
            ativo=True
        ).count(),
        "fornecedores_inativos": Fornecedor.objects.filter(
            ativo=False
        ).count(),
        "ultimos_fornecedores": Fornecedor.objects.order_by(
            "-criado_em"
        )[:10],
    }

    return render(
        request,
        "fornecedores/dashboard.html",
        context,
    )