from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from comercial.models import ItemOrcamento, Orcamento
from produtos.models import Produto



ZERO = Decimal("0.00")

def _converter_decimal(valor, campo, valor_padrao=ZERO):
    if valor in [None, ""]:
        return valor_padrao

    valor_normalizado = str(valor).strip().replace(" ", "")

    if "," in valor_normalizado:
        valor_normalizado = (
            valor_normalizado
            .replace(".", "")
            .replace(",", ".")
        )

    try:
        return Decimal(valor_normalizado)
    except (InvalidOperation, ValueError, TypeError):
        raise ValidationError(
            {
                campo: "Informe um valor válido."
            }
        )


def _converter_quantidade(valor):
    try:
        quantidade = int(valor)
    except (TypeError, ValueError):
        raise ValidationError(
            {
                "itens": "Informe uma quantidade válida para todos os produtos."
            }
        )

    if quantidade <= 0:
        raise ValidationError(
            {
                "itens": "A quantidade dos produtos deve ser maior que zero."
            }
        )

    return quantidade


def _normalizar_itens(itens):
    if not isinstance(itens, list) or not itens:
        raise ValidationError(
            {
                "itens": "Adicione pelo menos um produto ao orçamento."
            }
        )

    itens_normalizados = []
    produtos_ids = []
    produtos_repetidos = set()

    for indice, item in enumerate(itens, start=1):
        if not isinstance(item, dict):
            raise ValidationError(
                {
                    "itens": f"O item {indice} possui um formato inválido."
                }
            )

        produto_id = item.get("produto_id")

        try:
            produto_id = int(produto_id)
        except (TypeError, ValueError):
            raise ValidationError(
                {
                    "itens": f"Selecione um produto válido no item {indice}."
                }
            )

        if produto_id in produtos_ids:
            produtos_repetidos.add(produto_id)

        produtos_ids.append(produto_id)

        quantidade = _converter_quantidade(
            item.get("quantidade")
        )

        valor_unitario = _converter_decimal(
            item.get("valor_unitario"),
            campo="itens",
        )

        desconto = _converter_decimal(
            item.get("desconto"),
            campo="itens",
        )

        if valor_unitario <= ZERO:
            raise ValidationError(
                {
                    "itens": (
                        f"O valor unitário do item {indice} "
                        "deve ser maior que zero."
                    )
                }
            )

        if desconto < ZERO:
            raise ValidationError(
                {
                    "itens": (
                        f"O desconto do item {indice} "
                        "não pode ser negativo."
                    )
                }
            )

        valor_bruto = valor_unitario * quantidade

        if desconto > valor_bruto:
            raise ValidationError(
                {
                    "itens": (
                        f"O desconto do item {indice} não pode ser "
                        "maior que o valor bruto do produto."
                    )
                }
            )

        itens_normalizados.append(
            {
                "produto_id": produto_id,
                "quantidade": quantidade,
                "valor_unitario": valor_unitario,
                "desconto": desconto,
                "total": valor_bruto - desconto,
            }
        )

    if produtos_repetidos:
        raise ValidationError(
            {
                "itens": (
                    "Um mesmo produto não pode ser adicionado "
                    "mais de uma vez ao orçamento."
                )
            }
        )

    produtos = (
        Produto.objects
        .filter(
            pk__in=produtos_ids,
            ativo=True,
        )
        .in_bulk()
    )

    produtos_nao_encontrados = (
        set(produtos_ids) - set(produtos.keys())
    )

    if produtos_nao_encontrados:
        raise ValidationError(
            {
                "itens": (
                    "Um ou mais produtos selecionados não existem "
                    "ou estão inativos."
                )
            }
        )

    for item in itens_normalizados:
        item["produto"] = produtos[item["produto_id"]]

    return itens_normalizados


def _validar_orcamento_persistido(orcamento):
    if not orcamento or not orcamento.pk:
        raise ValidationError(
            "O orçamento precisa estar salvo antes desta operação."
        )


def _recalcular_totais_bloqueado(orcamento):
    """
    Recalcula os itens e os totais gerais do orçamento.

    Esta função pressupõe que está sendo executada dentro de uma
    transação e que o orçamento já foi bloqueado para atualização.
    """
    itens = list(
        ItemOrcamento.objects
        .select_for_update()
        .filter(orcamento=orcamento)
        .order_by("id")
    )

    subtotal = ZERO
    total_liquido_itens = ZERO

    for item in itens:
        valor_bruto = item.valor_unitario * item.quantidade

        if item.desconto > valor_bruto:
            raise ValidationError(
                {
                    "desconto": (
                        f"O desconto do produto {item.produto} não pode "
                        "ser maior que o valor bruto do item."
                    )
                }
            )

        total_item = valor_bruto - item.desconto

        subtotal += valor_bruto
        total_liquido_itens += total_item

        if item.total != total_item:
            item.total = total_item
            item.save(
                update_fields=[
                    "total",
                    "atualizado_em",
                ]
            )

    desconto_geral = orcamento.desconto or ZERO
    frete = orcamento.frete or ZERO

    if desconto_geral < ZERO:
        raise ValidationError(
            {"desconto": "O desconto geral não pode ser negativo."}
        )

    if frete < ZERO:
        raise ValidationError(
            {"frete": "O frete não pode ser negativo."}
        )

    if desconto_geral > total_liquido_itens:
        raise ValidationError(
            {
                "desconto": (
                    "O desconto geral não pode ser maior que o valor "
                    "líquido dos itens."
                )
            }
        )

    total = total_liquido_itens - desconto_geral + frete

    orcamento.subtotal = subtotal
    orcamento.total = total

    orcamento.save(
        update_fields=[
            "subtotal",
            "total",
            "atualizado_em",
        ]
    )

    return orcamento

@transaction.atomic
def criar_orcamento(*, dados, itens, vendedor):
    """
    Cria um orçamento e seus itens dentro de uma única transação.

    Parâmetros:
    - dados: dados já validados pelo OrcamentoForm;
    - itens: lista de produtos recebida da interface;
    - vendedor: usuário autenticado responsável pelo orçamento.
    """
    if not vendedor or not vendedor.is_authenticated:
        raise ValidationError(
            "Não foi possível identificar o vendedor responsável."
        )

    itens_normalizados = _normalizar_itens(itens)

    orcamento = Orcamento.objects.create(
        cliente=dados.get("cliente"),
        cliente_nome=dados["cliente_nome"],
        cliente_documento=dados.get("cliente_documento", ""),
        cliente_telefone=dados.get("cliente_telefone", ""),
        cliente_email=dados.get("cliente_email", ""),
        vendedor=vendedor,
        data_emissao=timezone.localdate(),
        data_validade=dados["data_validade"],
        desconto=dados.get("desconto", Decimal("0.00")),
        frete=dados.get("frete", Decimal("0.00")),
        condicoes_comerciais=dados.get(
            "condicoes_comerciais",
            "",
        ),
        observacoes=dados.get("observacoes", ""),
    )

    ItemOrcamento.objects.bulk_create(
        [
            ItemOrcamento(
                orcamento=orcamento,
                produto=item["produto"],
                quantidade=item["quantidade"],
                valor_unitario=item["valor_unitario"],
                desconto=item["desconto"],
                total=item["total"],
            )
            for item in itens_normalizados
        ]
    )

    orcamento_bloqueado = (
        Orcamento.objects
        .select_for_update()
        .get(pk=orcamento.pk)
    )

    return _recalcular_totais_bloqueado(
        orcamento_bloqueado
    )

@transaction.atomic
def recalcular_totais(orcamento):
    """
    Recalcula e grava os valores do orçamento e de seus itens.

    subtotal:
        Soma bruta dos produtos antes dos descontos.

    desconto dos itens:
        Gravado em cada ItemOrcamento.

    desconto do orçamento:
        Desconto geral aplicado após os descontos individuais.

    total:
        Itens líquidos - desconto geral + frete.
    """
    _validar_orcamento_persistido(orcamento)

    orcamento_bloqueado = (
        Orcamento.objects
        .select_for_update()
        .get(pk=orcamento.pk)
    )

    return _recalcular_totais_bloqueado(orcamento_bloqueado)


def _validar_possui_itens(orcamento):
    if not orcamento.itens.exists():
        raise ValidationError(
            "O orçamento precisa possuir pelo menos um item."
        )


def _validar_datas(orcamento):
    if orcamento.data_validade < orcamento.data_emissao:
        raise ValidationError(
            {
                "data_validade": (
                    "A validade não pode ser anterior à data de emissão."
                )
            }
        )


@transaction.atomic
def enviar_orcamento(orcamento):
    """
    Marca o orçamento como enviado.

    Permitido para:
    - Rascunho;
    - Rejeitado, após eventual revisão comercial.
    """
    _validar_orcamento_persistido(orcamento)

    orcamento_bloqueado = (
        Orcamento.objects
        .select_for_update()
        .get(pk=orcamento.pk)
    )

    status_permitidos = {
        Orcamento.Status.RASCUNHO,
        Orcamento.Status.REJEITADO,
    }

    if orcamento_bloqueado.status not in status_permitidos:
        raise ValidationError(
            "Somente orçamentos em rascunho ou rejeitados podem ser enviados."
        )

    _validar_possui_itens(orcamento_bloqueado)
    _validar_datas(orcamento_bloqueado)
    _recalcular_totais_bloqueado(orcamento_bloqueado)

    agora = timezone.now()

    orcamento_bloqueado.status = Orcamento.Status.ENVIADO
    orcamento_bloqueado.enviado_em = agora
    orcamento_bloqueado.rejeitado_em = None

    orcamento_bloqueado.save(
        update_fields=[
            "status",
            "enviado_em",
            "rejeitado_em",
            "atualizado_em",
        ]
    )

    return orcamento_bloqueado


@transaction.atomic
def aprovar_orcamento(orcamento):
    """
    Aprova um orçamento previamente enviado.
    """
    _validar_orcamento_persistido(orcamento)

    orcamento_bloqueado = (
        Orcamento.objects
        .select_for_update()
        .get(pk=orcamento.pk)
    )

    if orcamento_bloqueado.status != Orcamento.Status.ENVIADO:
        raise ValidationError(
            "Somente orçamentos enviados podem ser aprovados."
        )

    _validar_possui_itens(orcamento_bloqueado)
    _recalcular_totais_bloqueado(orcamento_bloqueado)

    orcamento_bloqueado.status = Orcamento.Status.APROVADO
    orcamento_bloqueado.aprovado_em = timezone.now()

    orcamento_bloqueado.save(
        update_fields=[
            "status",
            "aprovado_em",
            "atualizado_em",
        ]
    )

    return orcamento_bloqueado


@transaction.atomic
def rejeitar_orcamento(orcamento):
    """
    Rejeita um orçamento previamente enviado.
    """
    _validar_orcamento_persistido(orcamento)

    orcamento_bloqueado = (
        Orcamento.objects
        .select_for_update()
        .get(pk=orcamento.pk)
    )

    if orcamento_bloqueado.status != Orcamento.Status.ENVIADO:
        raise ValidationError(
            "Somente orçamentos enviados podem ser rejeitados."
        )

    orcamento_bloqueado.status = Orcamento.Status.REJEITADO
    orcamento_bloqueado.rejeitado_em = timezone.now()

    orcamento_bloqueado.save(
        update_fields=[
            "status",
            "rejeitado_em",
            "atualizado_em",
        ]
    )

    return orcamento_bloqueado


@transaction.atomic
def cancelar_orcamento(orcamento):
    """
    Cancela um orçamento ainda não convertido em venda.
    """
    _validar_orcamento_persistido(orcamento)

    orcamento_bloqueado = (
        Orcamento.objects
        .select_for_update()
        .get(pk=orcamento.pk)
    )

    if orcamento_bloqueado.status == Orcamento.Status.CONVERTIDO:
        raise ValidationError(
            "Um orçamento convertido em venda não pode ser cancelado."
        )

    if orcamento_bloqueado.status == Orcamento.Status.CANCELADO:
        raise ValidationError(
            "Este orçamento já está cancelado."
        )

    orcamento_bloqueado.status = Orcamento.Status.CANCELADO
    orcamento_bloqueado.cancelado_em = timezone.now()

    orcamento_bloqueado.save(
        update_fields=[
            "status",
            "cancelado_em",
            "atualizado_em",
        ]
    )

    return orcamento_bloqueado