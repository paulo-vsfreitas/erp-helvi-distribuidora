from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import transaction

from produtos.models import Produto
from vendas.models import ItemVenda, Venda
from vendas.services.numero_service import gerar_proximo_numero_venda


def converter_decimal(valor, padrao=Decimal("0.00")):
    if valor in (None, ""):
        return padrao

    texto = str(valor).strip().replace("R$", "").replace(" ", "")

    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")

    try:
        return Decimal(texto)
    except (InvalidOperation, TypeError, ValueError):
        raise ValidationError(f"Valor monetário inválido: {valor}")


def converter_inteiro(valor):
    try:
        return int(valor)
    except (TypeError, ValueError):
        raise ValidationError("Quantidade inválida.")


def extrair_itens(post):
    produtos = post.getlist("produto_id[]")
    quantidades = post.getlist("quantidade[]")
    precos = post.getlist("preco_unitario[]")
    descontos = post.getlist("desconto_item[]")

    itens = []
    produtos_adicionados = set()

    for indice, produto_id in enumerate(produtos):
        produto_id = str(produto_id or "").strip()

        if not produto_id:
            continue

        if produto_id in produtos_adicionados:
            raise ValidationError(
                "Um produto foi adicionado mais de uma vez. "
                "Altere somente a quantidade do item já existente."
            )

        produtos_adicionados.add(produto_id)

        quantidade = converter_inteiro(
            quantidades[indice] if indice < len(quantidades) else 0
        )

        preco_unitario = converter_decimal(
            precos[indice] if indice < len(precos) else 0
        )

        desconto = converter_decimal(
            descontos[indice] if indice < len(descontos) else 0
        )

        if quantidade <= 0:
            raise ValidationError(
                "A quantidade dos produtos deve ser maior que zero."
            )

        if preco_unitario <= 0:
            raise ValidationError(
                "O preço unitário deve ser maior que zero."
            )

        valor_bruto = preco_unitario * quantidade

        if desconto < 0:
            raise ValidationError(
                "O desconto do item não pode ser negativo."
            )

        if desconto > valor_bruto:
            raise ValidationError(
                "O desconto do item não pode ser maior que o valor do item."
            )

        itens.append(
            {
                "produto_id": int(produto_id),
                "quantidade": quantidade,
                "preco_unitario": preco_unitario,
                "desconto": desconto,
                "total": valor_bruto - desconto,
            }
        )

    if not itens:
        raise ValidationError(
            "Adicione pelo menos um produto à venda."
        )

    return itens


@transaction.atomic
def criar_venda(*, form, post, usuario):
    itens = extrair_itens(post)

    venda = form.save(commit=False)

    tipo_cliente = post.get(
        "tipo_cliente",
        "cadastrado",
    )

    if tipo_cliente == "consumidor_final":
        venda.cliente = None
    elif venda.cliente_id is None:
        raise ValidationError(
            "Selecione um cliente ou marque Consumidor Final."
        )

    venda.numero = gerar_proximo_numero_venda()
    venda.criada_por = usuario

    subtotal = sum(
        (item["preco_unitario"] * item["quantidade"] for item in itens),
        Decimal("0.00"),
    )

    desconto_itens = sum(
        (item["desconto"] for item in itens),
        Decimal("0.00"),
    )

    desconto_geral = converter_decimal(form.cleaned_data.get("desconto"))
    frete = converter_decimal(form.cleaned_data.get("frete"))

    total = subtotal - desconto_itens - desconto_geral + frete

    if desconto_geral < 0:
        raise ValidationError("O desconto geral não pode ser negativo.")

    if frete < 0:
        raise ValidationError("O frete não pode ser negativo.")

    if total < 0:
        raise ValidationError("O total da venda não pode ser negativo.")

    venda.subtotal = subtotal
    venda.desconto = desconto_geral + desconto_itens
    venda.frete = frete
    venda.total = total
    venda.valor_recebido = Decimal("0.00")
    venda.save()

    produtos_encontrados = Produto.objects.in_bulk(
        [item["produto_id"] for item in itens]
    )

    objetos = []

    for item in itens:
        produto = produtos_encontrados.get(int(item["produto_id"]))

        if produto is None:
            raise ValidationError("Um dos produtos selecionados não existe.")

        objetos.append(
            ItemVenda(
                venda=venda,
                produto=produto,
                quantidade=item["quantidade"],
                preco_unitario=item["preco_unitario"],
                desconto=item["desconto"],
                total=item["total"],
            )
        )

    ItemVenda.objects.bulk_create(objetos)

    return venda