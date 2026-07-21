from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from financeiro.models import (
    BaixaPagar,
    ContaFinanceira,
    ContaPagar,
    HistoricoContaPagar,
    MovimentacaoFinanceira,
    ParcelaPagar,
)


def _normalizar_decimal(valor, valor_padrao="0.00"):
    """
    Converte valores recebidos pelo service para Decimal.

    O formulário normalmente já entrega Decimal, mas esta proteção permite
    que o service também seja utilizado por integrações, APIs ou testes.
    """
    if valor in (None, ""):
        return Decimal(valor_padrao)

    if isinstance(valor, Decimal):
        return valor

    return Decimal(str(valor))


def _validar_baixa(
    *,
    parcela,
    conta_financeira,
    valor,
    juros,
    multa,
    desconto,
):
    conta_pagar = parcela.conta_pagar

    if conta_pagar.status == ContaPagar.STATUS_CANCELADA:
        raise ValidationError(
            "Não é possível registrar uma baixa em uma conta cancelada."
        )

    if parcela.status == ParcelaPagar.STATUS_CANCELADA:
        raise ValidationError(
            "Não é possível registrar uma baixa em uma parcela cancelada."
        )

    if (
        parcela.status == ParcelaPagar.STATUS_PAGA
        or parcela.saldo <= 0
    ):
        raise ValidationError(
            "Esta parcela já está totalmente paga."
        )

    if not conta_financeira.ativo:
        raise ValidationError(
            "A conta financeira selecionada está inativa."
        )

    if valor <= 0:
        raise ValidationError(
            "O valor principal da baixa deve ser maior que zero."
        )

    if juros < 0:
        raise ValidationError(
            "O valor dos juros não pode ser negativo."
        )

    if multa < 0:
        raise ValidationError(
            "O valor da multa não pode ser negativo."
        )

    if desconto < 0:
        raise ValidationError(
            "O desconto não pode ser negativo."
        )

    if valor > parcela.saldo:
        raise ValidationError(
            (
                "O valor principal informado é maior que o saldo "
                f"da parcela, que é de R$ {parcela.saldo:.2f}."
            )
        )

    valor_movimentado = valor + juros + multa - desconto

    if valor_movimentado <= 0:
        raise ValidationError(
            "O valor movimentado deve ser maior que zero."
        )

    if desconto > valor + juros + multa:
        raise ValidationError(
            "O desconto não pode superar a soma do valor, juros e multa."
        )


def _atualizar_valores_da_conta(conta_pagar):
    """
    Recalcula o valor pago da conta com base nas parcelas.

    O recálculo é mais seguro que simplesmente somar o valor da baixa,
    pois mantém a conta consistente mesmo com pagamentos parciais,
    futuras edições ou estornos.
    """
    total_pago = conta_pagar.parcelas.aggregate(
        total=Sum("valor_pago")
    )["total"] or Decimal("0.00")

    conta_pagar.valor_pago = total_pago
    conta_pagar.save(
        update_fields=[
            "valor_pago",
            "status",
            "atualizado_em",
        ]
    )


@transaction.atomic
def registrar_baixa(
    *,
    parcela,
    conta_financeira,
    valor,
    data_pagamento=None,
    forma_pagamento=BaixaPagar.FORMA_PIX,
    juros=Decimal("0.00"),
    multa=Decimal("0.00"),
    desconto=Decimal("0.00"),
    observacao="",
    usuario,
):
    """
    Registra uma baixa financeira em uma parcela de conta a pagar.

    A operação:

    1. bloqueia os registros envolvidos;
    2. valida a parcela, a conta e os valores;
    3. cria a BaixaPagar;
    4. cria a saída em MovimentacaoFinanceira;
    5. atualiza a parcela;
    6. atualiza a ContaPagar;
    7. registra o histórico da operação.

    Todos os passos são executados dentro da mesma transação.
    """
    parcela_id = (
        parcela.pk
        if isinstance(parcela, ParcelaPagar)
        else parcela
    )

    conta_financeira_id = (
        conta_financeira.pk
        if isinstance(conta_financeira, ContaFinanceira)
        else conta_financeira
    )

    parcela = (
        ParcelaPagar.objects
        .select_for_update()
        .select_related(
            "conta_pagar",
            "conta_pagar__categoria",
        )
        .get(pk=parcela_id)
    )

    conta_pagar = (
        ContaPagar.objects
        .select_for_update()
        .get(pk=parcela.conta_pagar_id)
    )

    conta_financeira = (
        ContaFinanceira.objects
        .select_for_update()
        .get(pk=conta_financeira_id)
    )

    valor = _normalizar_decimal(valor)
    juros = _normalizar_decimal(juros)
    multa = _normalizar_decimal(multa)
    desconto = _normalizar_decimal(desconto)

    data_pagamento = data_pagamento or timezone.localdate()
    observacao = (observacao or "").strip()

    _validar_baixa(
        parcela=parcela,
        conta_financeira=conta_financeira,
        valor=valor,
        juros=juros,
        multa=multa,
        desconto=desconto,
    )

    baixa = BaixaPagar.objects.create(
        parcela=parcela,
        conta_financeira=conta_financeira,
        data_pagamento=data_pagamento,
        valor=valor,
        juros=juros,
        multa=multa,
        desconto=desconto,
        forma_pagamento=forma_pagamento,
        observacao=observacao,
        registrado_por=usuario,
    )

    MovimentacaoFinanceira.objects.create(
        conta_financeira=conta_financeira,
        categoria=conta_pagar.categoria,
        baixa_pagar=baixa,
        tipo=MovimentacaoFinanceira.TIPO_SAIDA,
        data_movimentacao=data_pagamento,
        valor=baixa.valor_movimentado,
        descricao=(
            f"Pagamento da conta #{conta_pagar.numero} — "
            f"parcela {parcela.numero}"
        ),
        origem="conta_pagar",
        criado_por=usuario,
    )

    parcela.valor_pago += valor
    parcela.save(
        update_fields=[
            "valor_pago",
            "status",
            "atualizado_em",
        ]
    )

    _atualizar_valores_da_conta(conta_pagar)

    if conta_pagar.status == ContaPagar.STATUS_PAGA:
        descricao = (
            "Conta totalmente paga. "
            f"Parcela {parcela.numero} quitada."
        )

    elif parcela.status == ParcelaPagar.STATUS_PAGA:
        descricao = (
            f"Parcela {parcela.numero} quitada."
        )

    else:
        descricao = (
            "Pagamento parcial registrado "
            f"na parcela {parcela.numero}."
        )

    HistoricoContaPagar.objects.create(
        conta_pagar=conta_pagar,
        tipo_evento=HistoricoContaPagar.EVENTO_BAIXA,
        descricao=descricao,
        dados={
            "baixa_id": baixa.pk,
            "parcela_id": parcela.pk,
            "parcela": parcela.numero,
            "numero_parcela": parcela.numero,
            "conta_financeira_id": conta_financeira.pk,
            "conta_financeira": conta_financeira.nome,
            "data_pagamento": data_pagamento.isoformat(),
            "valor": str(valor),
            "valor_principal": str(valor),
            "juros": str(juros),
            "multa": str(multa),
            "desconto": str(desconto),
            "valor_movimentado": str(
                baixa.valor_movimentado
            ),
            "saldo_parcela": str(parcela.saldo),
            "saldo_conta": str(conta_pagar.saldo),
            "forma_pagamento": (
                baixa.get_forma_pagamento_display()
            ),
        },
        usuario=usuario,
    )

    return baixa