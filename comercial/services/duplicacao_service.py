from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from comercial.models import ItemOrcamento, Orcamento


@transaction.atomic
def duplicar_orcamento(*, orcamento, responsavel):
    if not orcamento or not orcamento.pk:
        raise ValidationError(
            "O orçamento original não foi identificado."
        )

    if not responsavel or not responsavel.is_authenticated:
        raise ValidationError(
            "Não foi possível identificar o responsável pela duplicação."
        )

    orcamento_original = (
        Orcamento.objects
        .select_for_update()
        .prefetch_related("itens__produto")
        .get(pk=orcamento.pk)
    )

    hoje = timezone.localdate()

    dias_validade = (
        orcamento_original.data_validade
        - orcamento_original.data_emissao
    ).days

    if dias_validade < 0:
        dias_validade = 7

    nova_validade = hoje + timedelta(days=dias_validade)

    novo_orcamento = Orcamento.objects.create(
        cliente=orcamento_original.cliente,
        cliente_nome=orcamento_original.cliente_nome,
        cliente_documento=orcamento_original.cliente_documento,
        cliente_telefone=orcamento_original.cliente_telefone,
        cliente_email=orcamento_original.cliente_email,
        vendedor=responsavel,
        data_emissao=hoje,
        data_validade=nova_validade,
        status=Orcamento.Status.RASCUNHO,
        subtotal=orcamento_original.subtotal,
        desconto=orcamento_original.desconto,
        frete=orcamento_original.frete,
        total=orcamento_original.total,
        condicoes_comerciais=(
            orcamento_original.condicoes_comerciais
        ),
        observacoes=orcamento_original.observacoes,
    )

    itens = [
        ItemOrcamento(
            orcamento=novo_orcamento,
            produto=item.produto,
            quantidade=item.quantidade,
            valor_unitario=item.valor_unitario,
            desconto=item.desconto,
            total=item.total,
        )
        for item in orcamento_original.itens.all()
    ]

    ItemOrcamento.objects.bulk_create(itens)

    return novo_orcamento