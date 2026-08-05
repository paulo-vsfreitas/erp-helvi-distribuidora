from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from comercial.services.busca_service import (
    buscar_clientes_para_orcamento,
    buscar_produtos_para_orcamento,
)


@login_required
@require_GET
def api_buscar_clientes(request):
    termo = request.GET.get("q", "")

    clientes = buscar_clientes_para_orcamento(
        termo
    )

    dados = [
        {
            "id": cliente.id,
            "nome_fantasia": cliente.nome_fantasia,
            "razao_social": cliente.razao_social,
            "cnpj": cliente.cnpj or "",
            "responsavel": cliente.responsavel or "",
            "telefone": cliente.telefone or "",
            "whatsapp": cliente.whatsapp or "",
            "email": cliente.email or "",
            "cidade": cliente.cidade or "",
            "estado": cliente.estado or "",
            "cep": cliente.cep or "",
            "logradouro": cliente.logradouro or cliente.endereco or "",
            "numero": cliente.numero or "",
            "complemento": cliente.complemento or "",
            "bairro": cliente.bairro or "",
            "limite_credito": str(
                cliente.limite_credito
            ),
            "condicao_pagamento": (
                cliente.condicao_pagamento or ""
            ),
        }
        for cliente in clientes
    ]

    return JsonResponse(
        {
            "resultados": dados,
        }
    )


@login_required
@require_GET
def api_buscar_produtos(request):
    termo = request.GET.get("q", "")

    produtos = buscar_produtos_para_orcamento(
        termo
    )

    dados = [
        {
            "id": produto.id,
            "codigo": produto.codigo or "",
            "codigo_fornecedor": (
                produto.codigo_fornecedor or ""
            ),
            "modelo": produto.modelo or "",
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
            "preco_venda": str(
                produto.preco_venda
            ),
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
        for produto in produtos
    ]

    return JsonResponse(
        {
            "resultados": dados,
        }
    )
