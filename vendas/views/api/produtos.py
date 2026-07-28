from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from compras.services.produto_service import buscar_produtos_para_compra


@login_required
def buscar_produtos(request):
    termo = request.GET.get("q", "").strip()

    produtos = buscar_produtos_para_compra(termo)

    resultados = []

    for produto in produtos:
        marca = produto.marca.nome if produto.marca else ""

        resultados.append(
            {
                "id": produto.pk,
                "codigo": produto.codigo,
                "modelo": produto.modelo,
                "marca": marca,
                "preco": str(produto.preco_venda),
                "estoque": produto.estoque_atual,
            }
        )

    return JsonResponse(
        {
            "resultados": resultados,
        }
    )