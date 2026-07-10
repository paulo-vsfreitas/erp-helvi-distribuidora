from django.db.models import Q

from produtos.models import Produto


def buscar_produtos_para_compra(termo):
    termo = (termo or "").strip()

    if len(termo) < 2:
        return Produto.objects.none()

    return (
        Produto.objects
        .filter(ativo=True)
        .select_related(
            "marca",
            "genero",
            "colecao",
            "tipo_armacao",
        )
        .filter(
            Q(codigo__icontains=termo)
            | Q(modelo__icontains=termo)
            | Q(marca__nome__icontains=termo)
            | Q(genero__nome__icontains=termo)
            | Q(colecao__nome__icontains=termo)
            | Q(tipo_armacao__nome__icontains=termo)
        )
        .order_by("codigo", "modelo")[:10]
    )