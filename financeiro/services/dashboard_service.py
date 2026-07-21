from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone

from financeiro.models import (
    ContaFinanceira,
    ContaPagar,
    ContaReceber,
    MovimentacaoFinanceira,
    ParcelaPagar,
    ParcelaReceber,
)


ZERO = Decimal("0.00")


def formatar_moeda(valor):
    """
    Converte um valor monetário para o padrão brasileiro.

    Exemplo:
        Decimal("1250.50") -> R$ 1.250,50
    """
    valor = valor or ZERO

    valor_formatado = f"{valor:,.2f}"

    valor_formatado = (
        valor_formatado
        .replace(",", "TEMP")
        .replace(".", ",")
        .replace("TEMP", ".")
    )

    return f"R$ {valor_formatado}"


def _obter_total_agregado(queryset, campo="valor"):
    """
    Retorna a soma de um campo do queryset, garantindo Decimal zero
    quando não houver registros.
    """
    return (
        queryset.aggregate(total=Sum(campo))["total"]
        or ZERO
    )


def _obter_saldo_total_contas_financeiras():
    """
    Soma os saldos atuais de todas as contas financeiras ativas.
    """
    return sum(
        (
            conta.saldo_atual
            for conta in ContaFinanceira.objects.filter(ativo=True)
        ),
        ZERO,
    )


def obter_dados_dashboard_financeiro():
    """
    Centraliza as consultas e os indicadores do dashboard financeiro.

    O dashboard apresenta:

    - saldo atual das contas financeiras;
    - total pendente a receber;
    - total pendente a pagar;
    - resultado financeiro do mês;
    - entradas e saídas de hoje;
    - valores vencidos;
    - próximos recebimentos e pagamentos;
    - últimas movimentações.
    """
    hoje = timezone.localdate()
    inicio_mes = hoje.replace(day=1)

    contas_pagar_ativas = ContaPagar.objects.exclude(
        status=ContaPagar.STATUS_CANCELADA,
    )

    contas_receber_ativas = ContaReceber.objects.exclude(
        status=ContaReceber.STATUS_CANCELADA,
    )

    contas_pagar_abertas = contas_pagar_ativas.filter(
        status__in=[
            ContaPagar.STATUS_PENDENTE,
            ContaPagar.STATUS_PARCIAL,
        ],
    )

    contas_receber_abertas = contas_receber_ativas.filter(
        status__in=[
            ContaReceber.STATUS_PENDENTE,
            ContaReceber.STATUS_PARCIAL,
        ],
    )

    totais_pagar = contas_pagar_ativas.aggregate(
        valor_total=Sum("valor_total"),
        valor_pago=Sum("valor_pago"),
    )

    valor_total_pagar = (
        totais_pagar["valor_total"]
        or ZERO
    )

    valor_pago = (
        totais_pagar["valor_pago"]
        or ZERO
    )

    total_a_pagar = max(
        valor_total_pagar - valor_pago,
        ZERO,
    )

    totais_receber = contas_receber_ativas.aggregate(
        valor_total=Sum("valor_total"),
        valor_recebido=Sum("valor_recebido"),
    )

    valor_total_receber = (
        totais_receber["valor_total"]
        or ZERO
    )

    valor_recebido = (
        totais_receber["valor_recebido"]
        or ZERO
    )

    total_a_receber = max(
        valor_total_receber - valor_recebido,
        ZERO,
    )

    movimentacoes_validas = MovimentacaoFinanceira.objects.filter(
        estornada=False,
    )

    movimentacoes_mes = movimentacoes_validas.filter(
        data_movimentacao__range=[
            inicio_mes,
            hoje,
        ],
    )

    entradas_mes = _obter_total_agregado(
        movimentacoes_mes.filter(
            tipo=MovimentacaoFinanceira.TIPO_ENTRADA,
        )
    )

    saidas_mes = _obter_total_agregado(
        movimentacoes_mes.filter(
            tipo=MovimentacaoFinanceira.TIPO_SAIDA,
        )
    )

    resultado_mes = entradas_mes - saidas_mes

    entradas_hoje = _obter_total_agregado(
        movimentacoes_validas.filter(
            tipo=MovimentacaoFinanceira.TIPO_ENTRADA,
            data_movimentacao=hoje,
        )
    )

    saidas_hoje = _obter_total_agregado(
        movimentacoes_validas.filter(
            tipo=MovimentacaoFinanceira.TIPO_SAIDA,
            data_movimentacao=hoje,
        )
    )

    parcelas_pagar_vencidas = ParcelaPagar.objects.filter(
        data_vencimento__lt=hoje,
        status__in=[
            ParcelaPagar.STATUS_PENDENTE,
            ParcelaPagar.STATUS_PARCIAL,
        ],
        conta_pagar__status__in=[
            ContaPagar.STATUS_PENDENTE,
            ContaPagar.STATUS_PARCIAL,
        ],
    )

    parcelas_receber_vencidas = ParcelaReceber.objects.filter(
        data_vencimento__lt=hoje,
        status__in=[
            ParcelaReceber.STATUS_PENDENTE,
            ParcelaReceber.STATUS_PARCIAL,
        ],
        conta_receber__status__in=[
            ContaReceber.STATUS_PENDENTE,
            ContaReceber.STATUS_PARCIAL,
        ],
    )

    total_pagar_vencido = sum(
        (
            parcela.saldo
            for parcela in parcelas_pagar_vencidas
        ),
        ZERO,
    )

    total_receber_vencido = sum(
        (
            parcela.saldo
            for parcela in parcelas_receber_vencidas
        ),
        ZERO,
    )

    proximos_pagamentos = (
        ParcelaPagar.objects
        .filter(
            data_vencimento__gte=hoje,
            status__in=[
                ParcelaPagar.STATUS_PENDENTE,
                ParcelaPagar.STATUS_PARCIAL,
            ],
            conta_pagar__status__in=[
                ContaPagar.STATUS_PENDENTE,
                ContaPagar.STATUS_PARCIAL,
            ],
        )
        .select_related(
            "conta_pagar",
            "conta_pagar__fornecedor",
            "conta_pagar__categoria",
        )
        .order_by(
            "data_vencimento",
            "conta_pagar__numero",
            "numero",
        )[:5]
    )

    proximos_recebimentos = (
        ParcelaReceber.objects
        .filter(
            data_vencimento__gte=hoje,
            status__in=[
                ParcelaReceber.STATUS_PENDENTE,
                ParcelaReceber.STATUS_PARCIAL,
            ],
            conta_receber__status__in=[
                ContaReceber.STATUS_PENDENTE,
                ContaReceber.STATUS_PARCIAL,
            ],
        )
        .select_related(
            "conta_receber",
            "conta_receber__cliente",
            "conta_receber__categoria",
        )
        .order_by(
            "data_vencimento",
            "conta_receber__numero",
            "numero",
        )[:5]
    )

    contas_pagar_vencidas = (
        parcelas_pagar_vencidas
        .select_related(
            "conta_pagar",
            "conta_pagar__fornecedor",
        )
        .order_by(
            "data_vencimento",
            "conta_pagar__numero",
            "numero",
        )[:5]
    )

    contas_receber_vencidas = (
        parcelas_receber_vencidas
        .select_related(
            "conta_receber",
            "conta_receber__cliente",
        )
        .order_by(
            "data_vencimento",
            "conta_receber__numero",
            "numero",
        )[:5]
    )

    ultimas_movimentacoes = (
        movimentacoes_validas
        .select_related(
            "conta_financeira",
            "categoria",
        )
        .order_by(
            "-data_movimentacao",
            "-criado_em",
        )[:8]
    )

    saldo_financeiro = (
        _obter_saldo_total_contas_financeiras()
    )

    quantidade_contas_financeiras = (
        ContaFinanceira.objects
        .filter(ativo=True)
        .count()
    )

    quantidade_movimentacoes_hoje = (
        movimentacoes_validas
        .filter(data_movimentacao=hoje)
        .count()
    )

    cards = [
        {
            "titulo": "Saldo financeiro",
            "valor": formatar_moeda(saldo_financeiro),
            "icone": "bi bi-bank",
            "cor": "primary",
        },
        {
            "titulo": "Total a receber",
            "valor": formatar_moeda(total_a_receber),
            "icone": "bi bi-arrow-down-circle",
            "cor": "success",
        },
        {
            "titulo": "Total a pagar",
            "valor": formatar_moeda(total_a_pagar),
            "icone": "bi bi-arrow-up-circle",
            "cor": "danger",
        },
        {
            "titulo": "Resultado do mês",
            "valor": formatar_moeda(resultado_mes),
            "icone": "bi bi-graph-up-arrow",
            "cor": (
                "success"
                if resultado_mes >= ZERO
                else "danger"
            ),
        },
    ]

    return {
        "cards": cards,
        "hoje": hoje,
        "inicio_mes": inicio_mes,

        "saldo_financeiro": saldo_financeiro,
        "saldo_financeiro_formatado": formatar_moeda(
            saldo_financeiro
        ),

        "total_a_receber": total_a_receber,
        "total_a_receber_formatado": formatar_moeda(
            total_a_receber
        ),

        "total_a_pagar": total_a_pagar,
        "total_a_pagar_formatado": formatar_moeda(
            total_a_pagar
        ),

        "entradas_mes": entradas_mes,
        "entradas_mes_formatado": formatar_moeda(
            entradas_mes
        ),

        "saidas_mes": saidas_mes,
        "saidas_mes_formatado": formatar_moeda(
            saidas_mes
        ),

        "resultado_mes": resultado_mes,
        "resultado_mes_formatado": formatar_moeda(
            resultado_mes
        ),

        "entradas_hoje": entradas_hoje,
        "entradas_hoje_formatado": formatar_moeda(
            entradas_hoje
        ),

        "saidas_hoje": saidas_hoje,
        "saidas_hoje_formatado": formatar_moeda(
            saidas_hoje
        ),

        "total_receber_vencido": total_receber_vencido,
        "total_receber_vencido_formatado": formatar_moeda(
            total_receber_vencido
        ),

        "total_pagar_vencido": total_pagar_vencido,
        "total_pagar_vencido_formatado": formatar_moeda(
            total_pagar_vencido
        ),

        "quantidade_contas_receber_pendentes": (
            contas_receber_abertas.count()
        ),
        "quantidade_contas_pagar_pendentes": (
            contas_pagar_abertas.count()
        ),

        "quantidade_contas_receber_vencidas": (
            parcelas_receber_vencidas
            .values("conta_receber_id")
            .distinct()
            .count()
        ),

        "quantidade_contas_pagar_vencidas": (
            parcelas_pagar_vencidas
            .values("conta_pagar_id")
            .distinct()
            .count()
        ),

        "quantidade_contas_financeiras": (
            quantidade_contas_financeiras
        ),

        "quantidade_movimentacoes_hoje": (
            quantidade_movimentacoes_hoje
        ),

        "proximos_recebimentos": proximos_recebimentos,
        "proximos_pagamentos": proximos_pagamentos,

        "contas_receber_vencidas": contas_receber_vencidas,
        "contas_pagar_vencidas": contas_pagar_vencidas,

        "ultimas_movimentacoes": ultimas_movimentacoes,

        # Compatibilidade temporária com o template anterior.
        "total_desembolsado": saidas_mes,
        "quantidade_contas_vencidas": (
            parcelas_pagar_vencidas
            .values("conta_pagar_id")
            .distinct()
            .count()
        ),
        "quantidade_contas_pendentes": (
            contas_pagar_abertas.count()
        ),
        "quantidade_parcelas_pendentes": (
            ParcelaPagar.objects
            .filter(
                status__in=[
                    ParcelaPagar.STATUS_PENDENTE,
                    ParcelaPagar.STATUS_PARCIAL,
                ],
                conta_pagar__status__in=[
                    ContaPagar.STATUS_PENDENTE,
                    ContaPagar.STATUS_PARCIAL,
                ],
            )
            .count()
        ),
        "proximos_vencimentos": proximos_pagamentos,
        "contas_vencidas": contas_pagar_vencidas,
    }