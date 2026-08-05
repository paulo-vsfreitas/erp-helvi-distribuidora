from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import transaction
from django.contrib.auth import get_user_model

from produtos.models import Produto, VariacaoCor
from vendas.models import ItemVenda, Venda
from vendas.services.numero_service import gerar_proximo_numero_venda


def pode_editar_vendedor(usuario):
    return bool(
        usuario
        and usuario.is_authenticated
        and (usuario.eh_administrador or usuario.eh_gerente or usuario.eh_financeiro)
    )


def resolver_vendedor(*, usuario, vendedor_id=None, vendedor_atual=None):
    if not pode_editar_vendedor(usuario):
        return vendedor_atual or usuario

    vendedor_id = str(vendedor_id or "").strip()
    if not vendedor_id:
        raise ValidationError("Selecione o vendedor responsável pela venda.")

    Usuario = get_user_model()
    vendedor = Usuario.objects.filter(
        pk=vendedor_id,
        is_active=True,
        perfil__in=[
            Usuario.Perfil.ADMINISTRADOR,
            Usuario.Perfil.GERENTE,
            Usuario.Perfil.VENDEDOR,
        ],
    ).first()
    if vendedor is None:
        raise ValidationError("O vendedor selecionado não está disponível.")
    return vendedor


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
    variacoes = post.getlist("variacao_cor_id[]")

    itens = []
    itens_adicionados = set()

    for indice, produto_id in enumerate(produtos):
        produto_id = str(produto_id or "").strip()

        if not produto_id:
            continue

        variacao_cor_id = variacoes[indice] if indice < len(variacoes) else ""
        variacao_cor_id = str(variacao_cor_id or "").strip()
        chave_item = (produto_id, variacao_cor_id)
        if chave_item in itens_adicionados:
            raise ValidationError(
                "Uma combinação de produto e cor foi adicionada mais de uma vez. "
                "Altere somente a quantidade do item já existente."
            )

        itens_adicionados.add(chave_item)

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
                "variacao_cor_id": int(variacao_cor_id) if variacao_cor_id else None,
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
    venda.criada_por = resolver_vendedor(
        usuario=usuario,
        vendedor_id=post.get("vendedor"),
        vendedor_atual=usuario,
    )

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

        variacao_cor = None
        if item["variacao_cor_id"]:
            variacao_cor = VariacaoCor.objects.filter(
                pk=item["variacao_cor_id"], produto=produto
            ).first()
            if variacao_cor is None:
                raise ValidationError("A variação de cor selecionada não pertence ao produto.")
        elif produto.variacoes_cor.exists():
            raise ValidationError(
                f"Selecione a cor do produto {produto}."
            )

        objetos.append(
            ItemVenda(
                venda=venda,
                produto=produto,
                variacao_cor=variacao_cor,
                quantidade=item["quantidade"],
                preco_unitario=item["preco_unitario"],
                custo_unitario=produto.preco_custo,
                desconto=item["desconto"],
                total=item["total"],
            )
        )

    ItemVenda.objects.bulk_create(objetos)

    return venda


@transaction.atomic
def editar_venda_em_aberto(*, venda, form, post, usuario):
    itens = extrair_itens(post)
    venda = Venda.objects.select_for_update().get(pk=venda.pk)

    if venda.status != Venda.STATUS_EM_ABERTO:
        raise ValidationError("Somente vendas em aberto podem ser editadas.")
    if venda.estoque_baixado or venda.financeiro_gerado:
        raise ValidationError("Esta venda possui integrações processadas e não pode ser editada.")

    venda.criada_por = resolver_vendedor(
        usuario=usuario,
        vendedor_id=post.get("vendedor"),
        vendedor_atual=venda.criada_por,
    )

    for campo, valor in form.cleaned_data.items():
        if hasattr(venda, campo):
            setattr(venda, campo, valor)

    tipo_cliente = post.get("tipo_cliente", "cadastrado")
    if tipo_cliente == "consumidor_final":
        venda.cliente = None
    elif venda.cliente_id is None:
        raise ValidationError("Selecione um cliente ou marque Consumidor Final.")

    subtotal = sum(
        (item["preco_unitario"] * item["quantidade"] for item in itens),
        Decimal("0.00"),
    )
    desconto_itens = sum((item["desconto"] for item in itens), Decimal("0.00"))
    desconto_geral = converter_decimal(form.cleaned_data.get("desconto"))
    frete = converter_decimal(form.cleaned_data.get("frete"))
    total = subtotal - desconto_itens - desconto_geral + frete
    if desconto_geral < 0 or frete < 0 or total < 0:
        raise ValidationError("Os totais informados para a venda são inválidos.")

    venda.subtotal = subtotal
    venda.desconto = desconto_geral + desconto_itens
    venda.frete = frete
    venda.total = total
    venda.save()

    produtos = Produto.objects.in_bulk([item["produto_id"] for item in itens])
    novos_itens = []
    for item in itens:
        produto = produtos.get(item["produto_id"])
        if produto is None:
            raise ValidationError("Um dos produtos selecionados não existe.")
        variacao = None
        if item["variacao_cor_id"]:
            variacao = VariacaoCor.objects.filter(
                pk=item["variacao_cor_id"], produto=produto
            ).first()
            if variacao is None:
                raise ValidationError("A variação de cor selecionada não pertence ao produto.")
        elif produto.variacoes_cor.exists():
            raise ValidationError(
                f"Selecione a cor do produto {produto}."
            )
        novos_itens.append(ItemVenda(
            venda=venda,
            produto=produto,
            variacao_cor=variacao,
            quantidade=item["quantidade"],
            preco_unitario=item["preco_unitario"],
            custo_unitario=produto.preco_custo,
            desconto=item["desconto"],
            total=item["total"],
        ))

    venda.itens.all().delete()
    ItemVenda.objects.bulk_create(novos_itens)
    return venda


@transaction.atomic
def alterar_vendedor_da_venda(*, venda, vendedor_id, usuario, senha):
    if not pode_editar_vendedor(usuario):
        raise ValidationError("Você não tem permissão para alterar o vendedor.")
    if not senha or not usuario.check_password(senha):
        raise ValidationError("Senha de autorização inválida.")
    venda = Venda.objects.select_for_update().get(pk=venda.pk)
    venda.criada_por = resolver_vendedor(
        usuario=usuario,
        vendedor_id=vendedor_id,
        vendedor_atual=venda.criada_por,
    )
    venda.save(update_fields=["criada_por"])
    return venda
