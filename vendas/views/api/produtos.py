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
                "codigo": produto.codigo or "",
                "modelo": produto.modelo or "",
                "marca": marca,
                "preco": str(produto.preco_venda),
                "estoque": produto.estoque_atual,
                "variacoes": [
                    {
                        "id": cor.pk,
                        "nome": cor.nome or cor.codigo,
                        "codigo": cor.codigo,
                        "estoque": cor.estoque,
                    }
                    for cor in produto.variacoes_cor.all()
                ],
            }
        )

    return JsonResponse(
        {
            "resultados": resultados,
        }
    )
