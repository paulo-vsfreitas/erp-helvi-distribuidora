from django.db import models
from django.db.models import Q

from produtos.models import Produto


RELACIONAMENTOS_PESQUISAVEIS = [
    "marca",
    "genero",
    "colecao",
    "tipo_armacao",
]


def buscar_produtos_para_venda(termo=""):
    termo = (termo or "").strip()

    campos_produto = {
        campo.name: campo
        for campo in Produto._meta.get_fields()
    }

    relacionamentos_validos = [
        nome
        for nome in RELACIONAMENTOS_PESQUISAVEIS
        if nome in campos_produto
    ]

    consulta = (
        Produto.objects
        .filter(ativo=True)
        .select_related(*relacionamentos_validos)
    )

    if termo:
        filtros = Q()

        # Pesquisa automaticamente em todos os campos de texto do produto.
        # Isso inclui código, modelo, código do fornecedor, observações etc.,
        # caso esses campos existam no model.
        for campo in Produto._meta.fields:
            if isinstance(
                campo,
                (
                    models.CharField,
                    models.TextField,
                ),
            ):
                filtros |= Q(
                    **{
                        f"{campo.name}__icontains": termo,
                    }
                )

        # Pesquisa também nos cadastros relacionados.
        for relacionamento in relacionamentos_validos:
            campo_relacionamento = campos_produto[relacionamento]
            modelo_relacionado = campo_relacionamento.related_model

            for campo in modelo_relacionado._meta.fields:
                if isinstance(
                    campo,
                    (
                        models.CharField,
                        models.TextField,
                    ),
                ):
                    filtros |= Q(
                        **{
                            (
                                f"{relacionamento}__"
                                f"{campo.name}__icontains"
                            ): termo
                        }
                    )

        consulta = consulta.filter(filtros)

    campos_ordenacao = []

    if "codigo" in campos_produto:
        campos_ordenacao.append("codigo")

    if "modelo" in campos_produto:
        campos_ordenacao.append("modelo")

    campos_ordenacao.append("pk")

    return consulta.order_by(*campos_ordenacao)[:12]