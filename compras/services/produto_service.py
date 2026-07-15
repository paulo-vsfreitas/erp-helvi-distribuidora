from django.db.models import OuterRef, Q, Subquery

from compras.models import ItemCompra
from produtos.models import Produto


def buscar_produtos_para_compra(termo):
    termo = (termo or "").strip()

    ultimo_custo = (
        ItemCompra.objects
        .filter(
            produto_id=OuterRef("pk"),
        )
        .order_by(
            "-compra__data_compra",
            "-compra__id",
            "-id",
        )
        .values("custo_unitario")[:1]
    )

    produtos = (
        Produto.objects
        .filter(ativo=True)
        .select_related(
            "marca",
            "genero",
            "colecao",
            "tipo_armacao",
        )
        .annotate(
            ultimo_custo_compra=Subquery(
                ultimo_custo
            )
        )
    )

    if termo:
        produtos = produtos.filter(
            Q(codigo__icontains=termo)
            | Q(codigo_fornecedor__icontains=termo)
            | Q(modelo__icontains=termo)
            | Q(marca__nome__icontains=termo)
            | Q(genero__nome__icontains=termo)
            | Q(colecao__nome__icontains=termo)
            | Q(tipo_armacao__nome__icontains=termo)
            | Q(cores_disponiveis__icontains=termo)
            | Q(observacoes__icontains=termo)
        )

    return produtos.order_by(
        "codigo",
        "modelo",
    )[:30]