from estoque.models import MovimentacaoEstoque


def buscar_movimentacoes_entrada_compra(compra):
    """
    Retorna as movimentações de estoque geradas no recebimento da compra.

    O vínculo atual é identificado pela origem textual registrada durante
    o recebimento. Esse critério deverá ser substituído futuramente por uma
    relação direta com Compra, caso o model de estoque seja evoluído.
    """

    produtos_ids = compra.itens.values_list(
        "produto_id",
        flat=True,
    )

    return (
        MovimentacaoEstoque.objects
        .filter(
            tipo="compra",
            origem=f"Compra #{compra.numero}",
            produto_id__in=produtos_ids,
        )
        .select_related(
            "produto",
            "usuario",
        )
        .order_by(
            "data_movimentacao",
            "pk",
        )
    )