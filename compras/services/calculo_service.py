from decimal import Decimal


def calcular_total_item(quantidade, custo_unitario, desconto=Decimal("0.00")):
    quantidade = quantidade or 0
    custo_unitario = custo_unitario or Decimal("0.00")
    desconto = desconto or Decimal("0.00")

    return (quantidade * custo_unitario) - desconto


def calcular_totais_compra(itens, desconto=Decimal("0.00"), frete=Decimal("0.00")):
    subtotal = Decimal("0.00")

    for item in itens:
        subtotal += item.total

    desconto = desconto or Decimal("0.00")
    frete = frete or Decimal("0.00")

    total = (subtotal - desconto) + frete

    return {
        "subtotal": subtotal,
        "desconto": desconto,
        "frete": frete,
        "total": total,
    }