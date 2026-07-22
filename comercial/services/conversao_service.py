from django.db import transaction
from django.utils import timezone

from comercial.models import Orcamento
from vendas.models import ItemVenda, Venda


@transaction.atomic
def converter_orcamento_em_venda(orcamento):
    if orcamento.status != Orcamento.Status.APROVADO:
        raise ValueError(
            "Somente orçamentos aprovados podem ser convertidos."
        )

    if orcamento.venda_gerada_id:
        raise ValueError(
            "Este orçamento já foi convertido em venda."
        )

    if not orcamento.cliente_id:
        raise ValueError(
            "Para converter o orçamento em venda, selecione um cliente "
            "cadastrado antes da conversão."
        )

    if not orcamento.itens.exists():
        raise ValueError(
            "Não é possível converter um orçamento sem itens."
        )

    venda = Venda.objects.create(
        cliente=orcamento.cliente,
        desconto=orcamento.desconto,
        observacoes=orcamento.observacoes,
        status="aberta",
    )

    itens_venda = [
        ItemVenda(
            venda=venda,
            produto=item.produto,
            quantidade=item.quantidade,
            preco_unitario=item.valor_unitario,
        )
        for item in orcamento.itens.select_related("produto")
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