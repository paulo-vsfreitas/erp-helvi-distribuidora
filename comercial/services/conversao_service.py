from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from comercial.models import Orcamento
from comercial.services.orcamento_service import recalcular_totais
from vendas.models import ItemVenda, Venda
from vendas.services.numero_service import gerar_proximo_numero_venda


@transaction.atomic
def converter_orcamento_em_venda(orcamento, *, usuario):
    if not usuario or not usuario.is_authenticated:
        raise ValidationError(
            "Não foi possível identificar o usuário responsável."
        )

    orcamento_id = (
        orcamento.pk
        if isinstance(orcamento, Orcamento)
        else orcamento
    )

    orcamento = (
        Orcamento.objects
        .select_for_update()
        .get(pk=orcamento_id)
    )

    if orcamento.venda_gerada_id:
        raise ValidationError(
            "Este orçamento já foi convertido em venda."
        )

    if orcamento.status != Orcamento.Status.APROVADO:
        raise ValidationError(
            "Somente orçamentos aprovados podem ser convertidos."
        )

    if not orcamento.cliente_id:
        raise ValidationError(
            "Para converter o orçamento em venda, selecione um cliente "
            "cadastrado antes da conversão."
        )

    orcamento = recalcular_totais(orcamento)

    itens_orcamento = list(
        orcamento.itens
        .select_for_update()
        .select_related("produto")
        .order_by("pk")
    )

    if not itens_orcamento:
        raise ValidationError(
            "Não é possível converter um orçamento sem itens."
        )

    desconto_itens = sum(
        (item.desconto for item in itens_orcamento),
        Decimal("0.00"),
    )

    venda = Venda.objects.create(
        numero=gerar_proximo_numero_venda(),
        cliente=orcamento.cliente,
        subtotal=orcamento.subtotal,
        desconto=(orcamento.desconto or Decimal("0.00")) + desconto_itens,
        frete=orcamento.frete,
        total=orcamento.total,
        observacoes=orcamento.observacoes,
        status=Venda.STATUS_EM_ABERTO,
        status_pagamento=Venda.PAGAMENTO_PENDENTE,
        criada_por=usuario,
    )

    itens_venda = [
        ItemVenda(
            venda=venda,
            produto=item.produto,
            quantidade=item.quantidade,
            preco_unitario=item.valor_unitario,
            desconto=item.desconto,
            total=item.total,
        )
        for item in itens_orcamento
    ]

    ItemVenda.objects.bulk_create(itens_venda)

    orcamento.status = Orcamento.Status.CONVERTIDO
    orcamento.convertido_em = timezone.now()
    orcamento.venda_gerada = venda

    orcamento.save(
        update_fields=[
            "status",
            "convertido_em",
            "venda_gerada",
            "atualizado_em",
        ]
    )

    return venda
