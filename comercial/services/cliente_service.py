from django.db import transaction

from comercial.models import Orcamento


@transaction.atomic
def vincular_cliente_ao_orcamento(*, orcamento, cliente):
    if orcamento.status != Orcamento.Status.APROVADO:
        raise ValueError(
            "O cliente somente pode ser vinculado a um orçamento aprovado."
        )

    if orcamento.venda_gerada_id:
        raise ValueError(
            "Não é possível alterar o cliente após a conversão em venda."
        )

    orcamento.cliente = cliente
    orcamento.cliente_nome = str(cliente)

    if hasattr(cliente, "documento"):
        orcamento.cliente_documento = cliente.documento or ""

    if hasattr(cliente, "telefone"):
        orcamento.cliente_telefone = cliente.telefone or ""

    if hasattr(cliente, "email"):
        orcamento.cliente_email = cliente.email or ""

    orcamento.save(
        update_fields=[
            "cliente",
            "cliente_nome",
            "cliente_documento",
            "cliente_telefone",
            "cliente_email",
            "atualizado_em",
        ]
    )

    return orcamento