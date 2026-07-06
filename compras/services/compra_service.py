from decimal import Decimal

from django.db import transaction

from compras.models import Compra, ItemCompra
from produtos.models import Produto


def decimal_post(valor):
    if not valor:
        return Decimal("0.00")

    return Decimal(str(valor).replace(",", "."))


@transaction.atomic
def criar_compra_com_itens(form, usuario, post):
    produtos_ids = post.getlist("produto_id[]")
    quantidades = post.getlist("quantidade[]")
    custos = post.getlist("custo_unitario[]")
    descontos = post.getlist("desconto_item[]")

    if not produtos_ids:
        raise ValueError("Adicione pelo menos um produto à compra.")

    compra = form.save(commit=False)
    compra.criado_por = usuario
    compra.status = Compra.STATUS_AGUARDANDO_ENTREGA

    subtotal = Decimal("0.00")
    desconto_total = Decimal("0.00")

    compra.subtotal = Decimal("0.00")
    compra.desconto = Decimal("0.00")
    compra.save()

    for index, produto_id in enumerate(produtos_ids):
        produto = Produto.objects.get(id=produto_id)

        quantidade = int(quantidades[index])
        custo_unitario = decimal_post(custos[index])
        desconto = decimal_post(descontos[index])

        if quantidade <= 0:
            raise ValueError("A quantidade deve ser maior que zero.")

        if custo_unitario < 0:
            raise ValueError("O custo não pode ser negativo.")

        valor_bruto = quantidade * custo_unitario

        if desconto > valor_bruto:
            raise ValueError("O desconto não pode ser maior que o valor do item.")

        item = ItemCompra.objects.create(
            compra=compra,
            produto=produto,
            quantidade=quantidade,
            custo_unitario=custo_unitario,
            desconto=desconto,
        )

        subtotal += valor_bruto
        desconto_total += desconto

        produto.preco_custo = custo_unitario
        produto.save(update_fields=["preco_custo"])

    compra.subtotal = subtotal
    compra.desconto = desconto_total
    compra.save()

    return compra