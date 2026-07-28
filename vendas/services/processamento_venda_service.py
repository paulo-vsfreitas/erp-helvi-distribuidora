from datetime import datetime
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from financeiro.models import ContaFinanceira
from vendas.models import Venda
from vendas.services.cadastro_service import (
    converter_decimal,
    criar_venda,
)
from vendas.services.finalizacao_service import (
    finalizar_venda,
)


FORMAS_PAGAMENTO_AVISTA = {
    Venda.FORMA_PIX,
    Venda.FORMA_DINHEIRO,
    Venda.FORMA_CARTAO_DEBITO,
    Venda.FORMA_CARTAO_CREDITO,
    Venda.FORMA_TRANSFERENCIA,
}


def converter_data(valor, *, obrigatoria=False):
    valor = str(valor or "").strip()

    if not valor:
        if obrigatoria:
            raise ValidationError(
                "Informe a data do primeiro vencimento."
            )

        return None

    try:
        return datetime.strptime(
            valor,
            "%Y-%m-%d",
        ).date()

    except ValueError:
        raise ValidationError(
            "A data do primeiro vencimento é inválida."
        )


def converter_quantidade_parcelas(valor):
    try:
        quantidade = int(valor or 1)

    except (TypeError, ValueError):
        raise ValidationError(
            "A quantidade de parcelas é inválida."
        )

    if quantidade <= 0:
        raise ValidationError(
            "A quantidade de parcelas deve ser maior que zero."
        )

    if quantidade > 60:
        raise ValidationError(
            "A quantidade máxima permitida é de 60 parcelas."
        )

    return quantidade


def obter_conta_financeira(post, *, obrigatoria):
    conta_id = str(
        post.get("conta_financeira") or ""
    ).strip()

    if not conta_id:
        if obrigatoria:
            raise ValidationError(
                "Selecione a conta financeira que receberá o valor."
            )

        return None

    try:
        return ContaFinanceira.objects.get(
            pk=conta_id,
            ativo=True,
        )

    except (
        ContaFinanceira.DoesNotExist,
        ValueError,
        TypeError,
    ):
        raise ValidationError(
            "A conta financeira selecionada é inválida ou está inativa."
        )


def validar_pagamento_avista(
    *,
    venda,
    post,
):
    if venda.forma_pagamento not in FORMAS_PAGAMENTO_AVISTA:
        raise ValidationError(
            "Selecione uma forma de pagamento válida para uma "
            "venda à vista."
        )

    valor_entregue = converter_decimal(
        post.get("valor_entregue")
    )

    if valor_entregue <= 0:
        raise ValidationError(
            "Informe o valor entregue pelo cliente."
        )

    if venda.forma_pagamento != Venda.FORMA_DINHEIRO:
        if valor_entregue != venda.total:
            raise ValidationError(
                "Para Pix, cartão ou transferência, o valor "
                "informado deve ser igual ao total da venda."
            )

    if valor_entregue < venda.total:
        raise ValidationError(
            "O valor entregue é menor que o total da venda."
        )

    troco = max(
        valor_entregue - venda.total,
        Decimal("0.00"),
    )

    return {
        "valor_entrada": Decimal("0.00"),
        "quantidade_parcelas": 1,
        "primeiro_vencimento": timezone.localdate(),
        "valor_recebimento": venda.total,
        "troco": troco,
    }


def validar_pagamento_prazo(
    *,
    venda,
    post,
):
    if venda.cliente_id is None:
        raise ValidationError(
            "Vendas a prazo exigem um cliente cadastrado."
        )

    valor_entrada = converter_decimal(
        post.get("valor_entrada")
    )

    if valor_entrada < 0:
        raise ValidationError(
            "O valor da entrada não pode ser negativo."
        )

    if valor_entrada >= venda.total:
        raise ValidationError(
            "Para pagamento a prazo, a entrada deve ser menor "
            "que o total da venda."
        )

    quantidade_parcelas = converter_quantidade_parcelas(
        post.get("quantidade_parcelas")
    )

    primeiro_vencimento = converter_data(
        post.get("primeiro_vencimento"),
        obrigatoria=True,
    )

    return {
        "valor_entrada": valor_entrada,
        "quantidade_parcelas": quantidade_parcelas,
        "primeiro_vencimento": primeiro_vencimento,
        "valor_recebimento": valor_entrada,
        "troco": Decimal("0.00"),
    }


@transaction.atomic
def processar_nova_venda(
    *,
    form,
    post,
    usuario,
):
    acao = str(
        post.get("acao") or "salvar"
    ).strip()

    if acao not in ("salvar", "finalizar"):
        raise ValidationError(
            "A ação solicitada para a venda é inválida."
        )

    venda = criar_venda(
        form=form,
        post=post,
        usuario=usuario,
    )

    if acao == "salvar":
        return {
            "venda": venda,
            "finalizada": False,
            "troco": Decimal("0.00"),
        }

    condicao = str(
        post.get("condicao_pagamento") or "avista"
    ).strip()

    if condicao not in ("avista", "aprazo"):
        raise ValidationError(
            "A condição de pagamento é inválida."
        )

    if condicao == "avista":
        pagamento = validar_pagamento_avista(
            venda=venda,
            post=post,
        )
    else:
        pagamento = validar_pagamento_prazo(
            venda=venda,
            post=post,
        )

    conta_financeira = obter_conta_financeira(
        post,
        obrigatoria=pagamento["valor_recebimento"] > 0,
    )

    venda.conta_financeira = conta_financeira
    venda.valor_entrada = pagamento["valor_entrada"]
    venda.quantidade_parcelas = pagamento[
        "quantidade_parcelas"
    ]
    venda.primeiro_vencimento = pagamento[
        "primeiro_vencimento"
    ]

    venda.save(
        update_fields=[
            "conta_financeira",
            "valor_entrada",
            "quantidade_parcelas",
            "primeiro_vencimento",
        ]
    )

    venda = finalizar_venda(
        venda_id=venda.pk,
        usuario=usuario,
    )

    troco = pagamento["troco"]

    if troco > 0:
        venda.valor_troco = troco

        venda.save(
            update_fields=[
                "valor_troco",
            ]
        )

    venda.refresh_from_db()

    return {
        "venda": venda,
        "finalizada": True,
        "troco": troco,
    }