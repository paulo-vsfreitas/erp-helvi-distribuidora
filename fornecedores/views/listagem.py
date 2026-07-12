from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render

from fornecedores.models import Fornecedor
from usuarios.permissoes import Modulo, usuario_tem_permissao


@login_required
def listar_fornecedores(request):
    if not usuario_tem_permissao(
        request.user,
        Modulo.FORNECEDORES,
    ):
        raise PermissionDenied

    busca = request.GET.get("busca", "").strip()
    status = request.GET.get("status", "").strip()

    fornecedores = Fornecedor.objects.all().order_by(
        "razao_social"
    )

    if busca:
        fornecedores = fornecedores.filter(
            Q(codigo__icontains=busca)
            | Q(razao_social__icontains=busca)
            | Q(nome_fantasia__icontains=busca)
            | Q(cpf_cnpj__icontains=busca)
            | Q(contato_principal__icontains=busca)
            | Q(cidade__icontains=busca)
        )

    if status == "ativos":
        fornecedores = fornecedores.filter(ativo=True)

    elif status == "inativos":
        fornecedores = fornecedores.filter(ativo=False)

    paginator = Paginator(fornecedores, 15)

    page_obj = paginator.get_page(
        request.GET.get("page")
    )

    return render(
        request,
        "fornecedores/lista_fornecedores.html",
        {
            "page_obj": page_obj,
            "busca": busca,
            "status_atual": status,
        },
    )