from decimal import Decimal, InvalidOperation

from django.db import transaction

from compras.models import Compra, ItemCompra
from produtos.models import Produto


def decimal_post(valor, campo="valor"):
    """
    Converte valores recebidos pelo formulário para Decimal.

    Aceita formatos como:
    - 150
    - 150.00
    - 150,00
    - 1.250,00
    """
    if valor in (None, ""):
        return Decimal("0.00")

    valor_normalizado = str(valor).strip()

    # Formato brasileiro: 1.250,00
    if "," in valor_normalizado:
        valor_normalizado = (
            valor_normalizado
            .replace(".", "")
            .replace(",", ".")
        )

    try:
        return Decimal(valor_normalizado)
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f"Informe um {campo} válido.")


@transaction.atomic
def criar_compra_com_itens(form, usuario, post):
    produtos_ids = post.getlist("produto_id[]")
    quantidades = post.getlist("quantidade[]")
    custos = post.getlist("custo_unitario[]")
    descontos = post.getlist("desconto_item[]")

    if not produtos_ids:
        raise ValueError("Adicione pelo menos um produto à compra.")

    quantidade_itens = len(produtos_ids)

    if not (
        len(quantidades) == quantidade_itens
        and len(custos) == quantidade_itens
        and len(descontos) == quantidade_itens
    ):
        raise ValueError(
            "Os dados dos produtos estão incompletos. "
            "Revise os itens da compra."
        )

    compra = form.save(commit=False)
    compra.criado_por = usuario
    compra.status = Compra.STATUS_AGUARDANDO_ENTREGA

    subtotal = Decimal("0.00")
    desconto_total = Decimal("0.00")

    # A compra precisa existir antes da criação dos itens.
    compra.subtotal = Decimal("0.00")
    compra.desconto = Decimal("0.00")
    compra.save()

    for index, produto_id in enumerate(produtos_ids):
        try:
            produto = Produto.objects.select_for_update().get(
                pk=produto_id
            )
        except Produto.DoesNotExist:
            raise ValueError(
                "Um dos produtos selecionados não foi encontrado."
            )

        try:
            quantidade = int(quantidades[index])
        except (TypeError, ValueError):
            raise ValueError("Informe uma quantidade válida.")

        custo_unitario = decimal_post(
            custos[index],
            campo="custo unitário",
        )

        desconto = decimal_post(
            descontos[index],
            campo="desconto",
        )

        if quantidade <= 0:
            raise ValueError(
                "A quantidade deve ser maior que zero."
            )

        if custo_unitario <= 0:
            raise ValueError(
                "O custo unitário deve ser maior que zero."
            )

        if desconto < 0:
            raise ValueError(
                "O desconto não pode ser negativo."
            )

        valor_bruto = Decimal(quantidade) * custo_unitario

        if desconto > valor_bruto:
            raise ValueError(
                "O desconto não pode ser maior que o valor do item."
            )

        ItemCompra.objects.create(
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