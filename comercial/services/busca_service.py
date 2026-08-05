from django.db.models import Q

from clientes.models import Cliente
from produtos.models import Produto


LIMITE_RESULTADOS = 10
TAMANHO_MINIMO_TERMO = 2


def buscar_clientes_para_orcamento(termo):
    termo = (termo or "").strip()

    clientes = (
        Cliente.objects
        .filter(ativo=True)
        .order_by(
            "nome_fantasia",
            "razao_social",
        )
    )

    # Ao clicar no campo sem digitar, retorna os primeiros
    # clientes ativos cadastrados.
    if not termo:
        return clientes[:LIMITE_RESULTADOS]

    if len(termo) < TAMANHO_MINIMO_TERMO:
        return Cliente.objects.none()

    return (
        clientes
        .filter(
            Q(nome_fantasia__icontains=termo)
            | Q(razao_social__icontains=termo)
            | Q(cnpj__icontains=termo)
            | Q(responsavel__icontains=termo)
            | Q(telefone__icontains=termo)
            | Q(whatsapp__icontains=termo)
        )[:LIMITE_RESULTADOS]
    )


def buscar_produtos_para_orcamento(termo):
    termo = (termo or "").strip()

    produtos = (
        Produto.objects
        .filter(ativo=True)
        .select_related(
            "marca",
            "colecao",
            "genero",
            "tipo_armacao",
        )
        .prefetch_related("variacoes_cor")
        .order_by(
            "codigo",
            "modelo",
        )
    )

    if not termo:
        return produtos[:LIMITE_RESULTADOS]

    if len(termo) < TAMANHO_MINIMO_TERMO:
        return Produto.objects.none()

    return (
        produtos
        .filter(
            Q(codigo__icontains=termo)
            | Q(codigo_fornecedor__icontains=termo)
            | Q(modelo__icontains=termo)
            | Q(marca__nome__icontains=termo)
            | Q(colecao__nome__icontains=termo)
            | Q(genero__nome__icontains=termo)
            | Q(tipo_armacao__nome__icontains=termo)
            | Q(cores_disponiveis__icontains=termo)
        )[:LIMITE_RESULTADOS]
    )
