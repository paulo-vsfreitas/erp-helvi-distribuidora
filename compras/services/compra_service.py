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

@transaction.atomic
def atualizar_compra_com_itens(
    compra,
    form,
    post,
):
    """
    Atualiza os dados gerais e os itens de uma compra ainda não recebida.

    Os pagamentos existentes são preservados e o novo total não pode
    ficar abaixo do valor já pago.
    """

    compra = Compra.objects.select_for_update().get(
        pk=compra.pk
    )

    if (
        compra.entrada_estoque_realizada
        or compra.status == Compra.STATUS_RECEBIDA
    ):
        raise ValueError(
            "Esta compra já foi recebida e não pode ser editada."
        )

    produtos_ids = post.getlist("produto_id[]")
    quantidades = post.getlist("quantidade[]")
    custos = post.getlist("custo_unitario[]")
    descontos = post.getlist("desconto_item[]")

    if not produtos_ids:
        raise ValueError(
            "Adicione pelo menos um produto à compra."
        )

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

    subtotal = Decimal("0.00")
    desconto_total = Decimal("0.00")

    produtos_utilizados = set()
    itens_validados = []

    for index, produto_id in enumerate(produtos_ids):
        try:
            produto_id = int(produto_id)
        except (TypeError, ValueError):
            raise ValueError(
                "Um dos produtos informados é inválido."
            )

        if produto_id in produtos_utilizados:
            raise ValueError(
                "O mesmo produto não pode aparecer mais de uma vez "
                "na compra."
            )

        produtos_utilizados.add(produto_id)

        try:
            produto = Produto.objects.get(pk=produto_id)
        except Produto.DoesNotExist:
            raise ValueError(
                "Um dos produtos selecionados não foi encontrado."
            )

        try:
            quantidade = int(quantidades[index])
        except (TypeError, ValueError):
            raise ValueError(
                "Informe uma quantidade válida."
            )

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

        valor_bruto = (
            Decimal(quantidade) * custo_unitario
        )

        if desconto > valor_bruto:
            raise ValueError(
                f"O desconto do produto {produto} não pode ser "
                "maior que o valor bruto do item."
            )

        total_item = valor_bruto - desconto

        itens_validados.append(
            {
                "produto": produto,
                "quantidade": quantidade,
                "custo_unitario": custo_unitario,
                "desconto": desconto,
                "total": total_item,
            }
        )

        subtotal += valor_bruto
        desconto_total += desconto

    frete = form.cleaned_data.get(
        "frete",
        Decimal("0.00"),
    )

    novo_total = (
        subtotal
        - desconto_total
        + frete
    )

    if novo_total < compra.valor_pago:
        valor_pago_formatado = (
            f"{compra.valor_pago:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

        raise ValueError(
            "O total da compra não pode ficar abaixo do valor "
            f"já pago de R$ {valor_pago_formatado}."
        )

    # Atualiza os dados gerais da compra.
    compra.fornecedor_nome = form.cleaned_data[
        "fornecedor_nome"
    ]

    compra.fornecedor_documento = form.cleaned_data.get(
        "fornecedor_documento",
        "",
    )

    compra.fornecedor_telefone = form.cleaned_data.get(
        "fornecedor_telefone",
        "",
    )

    compra.data_compra = form.cleaned_data[
        "data_compra"
    ]

    compra.previsao_entrega = form.cleaned_data.get(
        "previsao_entrega"
    )

    compra.frete = frete

    compra.observacoes = form.cleaned_data.get(
        "observacoes",
        "",
    )

    compra.subtotal = subtotal
    compra.desconto = desconto_total

    # Os pagamentos não são alterados.
    # O save recalculará total e status do pagamento.
    compra.save()

    # Como a compra ainda não movimentou estoque, seus itens podem
    # ser substituídos com segurança.
    compra.itens.all().delete()

    novos_itens = [
        ItemCompra(
            compra=compra,
            produto=item["produto"],
            quantidade=item["quantidade"],
            custo_unitario=item["custo_unitario"],
            desconto=item["desconto"],
            total=item["total"],
        )
        for item in itens_validados
    ]

    ItemCompra.objects.bulk_create(novos_itens)

    return compra

def obter_itens_para_formulario(
    compra=None,
    post=None,
):
    """
    Retorna os itens no formato esperado pelo template de cadastro
    e edição.

    Quando existe POST, preserva os valores digitados pelo usuário
    após algum erro de validação.
    """

    if post:
        produtos_ids = post.getlist("produto_id[]")
        quantidades = post.getlist("quantidade[]")
        custos = post.getlist("custo_unitario[]")
        descontos = post.getlist("desconto_item[]")

        produtos = Produto.objects.filter(
            pk__in=produtos_ids
        )

        produtos_por_id = {
            str(produto.pk): produto
            for produto in produtos
        }

        itens = []

        for index, produto_id in enumerate(produtos_ids):
            produto = produtos_por_id.get(
                str(produto_id)
            )

            if not produto:
                continue

            quantidade = (
                quantidades[index]
                if index < len(quantidades)
                else "1"
            )

            custo_unitario = (
                custos[index]
                if index < len(custos)
                else "0.00"
            )

            desconto = (
                descontos[index]
                if index < len(descontos)
                else "0.00"
            )

            try:
                total = (
                    Decimal(str(quantidade))
                    * decimal_post(custo_unitario)
                    - decimal_post(desconto)
                )
            except (
                InvalidOperation,
                TypeError,
                ValueError,
            ):
                total = Decimal("0.00")

            itens.append(
                {
                    "produto": produto,
                    "quantidade": quantidade,
                    "custo_unitario": custo_unitario,
                    "desconto": desconto,
                    "total": total,
                }
            )

        return itens

    if compra:
        return compra.itens.select_related(
            "produto"
        ).all()

    return []