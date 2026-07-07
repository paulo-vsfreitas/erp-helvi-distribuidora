from django.db import transaction
from django.utils import timezone

from compras.models import Compra
from estoque.models import MovimentacaoEstoque


@transaction.atomic
def receber_compra(compra, usuario):
    if compra.status == Compra.STATUS_CANCELADA:
        raise ValueError("Não é possível receber uma compra cancelada.")

    if compra.entrada_estoque_realizada:
        raise ValueError("Esta compra já foi recebida no estoque.")

    itens = compra.itens.select_related("produto").all()

    if not itens.exists():
        raise ValueError("Não é possível receber uma compra sem produtos.")

    for item in itens:
        produto = item.produto

        saldo_anterior = produto.estoque_atual
        saldo_atual = saldo_anterior + item.quantidade

        produto.estoque_atual = saldo_atual
        produto.preco_custo = item.custo_unitario
        produto.save(update_fields=["estoque_atual", "preco_custo"])

        MovimentacaoEstoque.objects.create(
            produto=produto,
            tipo="compra",
            quantidade=item.quantidade,
            saldo_anterior=saldo_anterior,
            saldo_atual=saldo_atual,
            usuario=usuario,
            origem=f"Compra #{compra.numero}",
            observacao=f"Entrada automática referente à compra #{compra.numero}.",
        )

    compra.status = Compra.STATUS_RECEBIDA
    compra.entrada_estoque_realizada = True
    compra.recebida_em = timezone.now()
    compra.recebida_por = usuario
    compra.save()

    return compra