from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from compras.services.produto_service import (
    buscar_produtos_para_compra,
)


@login_required
def api_buscar_produtos(request):
    termo = request.GET.get("q", "")

    produtos = buscar_produtos_para_compra(
        termo
    )

    dados = [
        {
            "id": produto.id,
            "codigo": produto.codigo,
            "codigo_fornecedor": (
                produto.codigo_fornecedor or ""
            ),
            "modelo": produto.modelo,
            "marca": (
                produto.marca.nome
                if produto.marca
                else ""
            ),
            "colecao": (
                produto.colecao.nome
                if produto.colecao
                else ""
            ),
            "genero": (
                produto.genero.nome
                if produto.genero
                else ""
            ),
            "tipo_armacao": (
                produto.tipo_armacao.nome
                if produto.tipo_armacao
                else ""
            ),
            "cores_disponiveis": (
                produto.cores_disponiveis or ""
            ),
            "estoque_atual": produto.estoque_atual,
            "preco_custo": str(
                produto.preco_custo
            ),
            "ultimo_custo_compra": (
                str(produto.ultimo_custo_compra)
                if produto.ultimo_custo_compra is not None
                else ""
            ),
            "preco_venda": str(
                produto.preco_venda
            ),
        }
        for produto in produtos
    ]

    return JsonResponse(
        {
            "resultados": dados,
        }
    )