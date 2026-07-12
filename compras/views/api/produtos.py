from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from compras.services.produto_service import buscar_produtos_para_compra


@login_required
def api_buscar_produtos(request):
    termo = request.GET.get("q", "")

    produtos = buscar_produtos_para_compra(termo)

    dados = [
    {
        "id": produto.id,
        "codigo": produto.codigo,
        "modelo": produto.modelo,
        "preco_custo": str(produto.preco_custo),
        "preco_venda": str(produto.preco_venda),
    }
    for produto in produtos
]

    return JsonResponse({"resultados": dados})