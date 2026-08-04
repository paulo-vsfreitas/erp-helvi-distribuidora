from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render

from fornecedores.models import Fornecedor
from usuarios.permissoes import Modulo, usuario_tem_permissao


def montar_contexto_listagem(request):
    busca = request.GET.get("busca", "").strip()
    status = request.GET.get("status", "").strip()
    estado = request.GET.get("estado", "").strip().upper()

    if status not in {"ativos", "inativos"}:
        status = ""

    estados_validos = {sigla for sigla, _ in Fornecedor.ESTADOS_CHOICES}
    if estado not in estados_validos:
        estado = ""

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

    if estado:
        fornecedores = fornecedores.filter(estado=estado)

    paginator = Paginator(fornecedores, 15)
    page_obj = paginator.get_page(request.GET.get("page"))

    return {
        "page_obj": page_obj,
        "busca": busca,
        "status_atual": status,
        "estado_atual": estado,
        "estados_choices": Fornecedor.ESTADOS_CHOICES,
        "total_fornecedores": Fornecedor.objects.count(),
        "fornecedores_ativos": Fornecedor.objects.filter(ativo=True).count(),
        "fornecedores_inativos": Fornecedor.objects.filter(ativo=False).count(),
        "pessoas_juridicas": Fornecedor.objects.filter(
            tipo_pessoa=Fornecedor.TIPO_PESSOA_JURIDICA
        ).count(),
    }


@login_required
def listar_fornecedores(request):
    if not usuario_tem_permissao(
        request.user,
        Modulo.FORNECEDORES,
    ):
        raise PermissionDenied

    return render(
        request,
        "fornecedores/lista_fornecedores.html",
        montar_contexto_listagem(request),
    )
