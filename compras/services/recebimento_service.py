from django.db import transaction
from django.utils import timezone

from compras.models import Compra
from estoque.models import MovimentacaoEstoque
from produtos.models import Produto


@transaction.atomic
def receber_compra(compra, usuario):
    """
    Recebe uma compra, lança seus produtos no estoque e registra
    as respectivas movimentações.

    Toda a operação é executada dentro de uma única transação:
    se qualquer etapa falhar, nenhuma alteração será confirmada.
    """

    # Recarrega e bloqueia a compra até o término da transação.
    compra = Compra.objects.select_for_update().get(pk=compra.pk)

    if compra.status == Compra.STATUS_CANCELADA:
        raise ValueError(
            "Não é possível receber uma compra cancelada."
        )

    if (
        compra.status == Compra.STATUS_RECEBIDA
        or compra.entrada_estoque_realizada
    ):
        raise ValueError(
            "Esta compra já foi recebida no estoque."
        )

    itens = list(
        compra.itens.select_related("produto").all()
    )

    if not itens:
        raise ValueError(
            "Não é possível receber uma compra sem produtos."
        )

    produtos_ids = {
        item.produto_id
        for item in itens
    }

    # Bloqueia todos os produtos envolvidos na operação.
    produtos = {
        produto.pk: produto
        for produto in Produto.objects.select_for_update().filter(
            pk__in=produtos_ids
        )
    }

    if len(produtos) != len(produtos_ids):
        raise ValueError(
            "Um ou mais produtos da compra não foram encontrados."
        )

    for item in itens:
        produto = produtos[item.produto_id]

        saldo_anterior = produto.estoque_atual
        saldo_atual = saldo_anterior + item.quantidade

        produto.estoque_atual = saldo_atual
        produto.preco_custo = item.custo_unitario

        produto.save(
            update_fields=[
                "estoque_atual",
                "preco_custo",
            ]
        )

        MovimentacaoEstoque.objects.create(
            produto=produto,
            tipo="compra",
            quantidade=item.quantidade,
            saldo_anterior=saldo_anterior,
            saldo_atual=saldo_atual,
            usuario=usuario,
            origem=f"Compra #{compra.numero}",
            observacao=(
                "Entrada automática referente à "
                f"compra #{compra.numero}."
            ),
        )

    compra.status = Compra.STATUS_RECEBIDA
    compra.entrada_estoque_realizada = True
    compra.recebida_em = timezone.now()
    compra.recebida_por = usuario
    compra.save()

    return compra