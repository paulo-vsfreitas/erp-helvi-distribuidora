from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone

from financeiro.models import (
    ContaFinanceira,
    ContaPagar,
    MovimentacaoFinanceira,
    ParcelaPagar,
)


def formatar_moeda(valor):
    """
    Converte Decimal para o padrão monetário brasileiro.
    Exemplo: 1250.50 -> R$ 1.250,50
    """
    valor = valor or Decimal("0.00")

    valor_formatado = f"{valor:,.2f}"

    valor_formatado = (
        valor_formatado
        .replace(",", "TEMP")
        .replace(".", ",")
        .replace("TEMP", ".")
    )

    return f"R$ {valor_formatado}"


def obter_dados_dashboard_financeiro():
    """
    Centraliza as consultas e os dados exibidos no dashboard financeiro.
    """

    hoje = timezone.localdate()

    contas_ativas = ContaPagar.objects.exclude(
        status=ContaPagar.STATUS_CANCELADA,
    )

    totais = contas_ativas.aggregate(
        valor_total=Sum("valor_total"),
        valor_pago=Sum("valor_pago"),
    )

    valor_total = totais["valor_total"] or Decimal("0.00")
    valor_pago = totais["valor_pago"] or Decimal("0.00")
    total_a_pagar = max(
        valor_total - valor_pago,
        Decimal("0.00"),
    )

    quantidade_contas_vencidas = (
        ContaPagar.objects
        .filter(
            parcelas__data_vencimento__lt=hoje,
            parcelas__status__in=[
                ParcelaPagar.STATUS_PENDENTE,
                ParcelaPagar.STATUS_PARCIAL,
            ],
        )
        .exclude(
            status=ContaPagar.STATUS_CANCELADA,
        )
        .distinct()
        .count()
    )

    quantidade_contas_financeiras = ContaFinanceira.objects.filter(
        ativo=True,
    ).count()

    quantidade_contas_pendentes = contas_ativas.filter(
        status__in=[
            ContaPagar.STATUS_PENDENTE,
            ContaPagar.STATUS_PARCIAL,
        ],
    ).count()

    quantidade_parcelas_pendentes = ParcelaPagar.objects.filter(
        status__in=[
            ParcelaPagar.STATUS_PENDENTE,
            ParcelaPagar.STATUS_PARCIAL,
        ],
        conta_pagar__status__in=[
            ContaPagar.STATUS_PENDENTE,
            ContaPagar.STATUS_PARCIAL,
        ],
    ).count()

    quantidade_movimentacoes_hoje = (
        MovimentacaoFinanceira.objects
        .filter(
            data_movimentacao=hoje,
            estornada=False,
        )
        .count()
    )

    saldo_financeiro = sum(
        (
            conta.saldo_atual
            for conta in ContaFinanceira.objects.filter(ativo=True)
        ),
        Decimal("0.00"),
    )

    proximos_vencimentos = (
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

    contas_vencidas = (
        ParcelaPagar.objects
        .filter(
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
        .select_related(
            "conta_pagar",
            "conta_pagar__fornecedor",
        )
        .order_by(
            "data_vencimento",
            "conta_pagar__numero",
        )[:5]
    )

    ultimas_movimentacoes = (
        MovimentacaoFinanceira.objects
        .select_related(
            "conta_financeira",
            "categoria",
        )
        .order_by(
            "-data_movimentacao",
            "-criado_em",
        )[:5]
    )

    cards = [
        {
            "titulo": "Total a pagar",
            "valor": formatar_moeda(total_a_pagar),
            "icone": "bi bi-wallet2",
            "cor": "warning",
        },
        {
            "titulo": "Total pago",
            "valor": formatar_moeda(valor_pago),
            "icone": "bi bi-check-circle",
            "cor": "success",
        },
        {
            "titulo": "Contas vencidas",
            "valor": quantidade_contas_vencidas,
            "icone": "bi bi-exclamation-triangle",
            "cor": "danger",
        },
        {
            "titulo": "Contas financeiras",
            "valor": quantidade_contas_financeiras,
            "icone": "bi bi-bank",
            "cor": "primary",
        },
    ]

    return {
        "cards": cards,
        "hoje": hoje,
        "total_a_pagar": total_a_pagar,
        "total_pago": valor_pago,
        "quantidade_contas_vencidas": quantidade_contas_vencidas,
        "quantidade_contas_financeiras": quantidade_contas_financeiras,
        "quantidade_contas_pendentes": quantidade_contas_pendentes,
        "quantidade_parcelas_pendentes": quantidade_parcelas_pendentes,
        "quantidade_movimentacoes_hoje": quantidade_movimentacoes_hoje,
        "saldo_financeiro_formatado": formatar_moeda(
            saldo_financeiro
        ),
        "proximos_vencimentos": proximos_vencimentos,
        "contas_vencidas": contas_vencidas,
        "ultimas_movimentacoes": ultimas_movimentacoes,
    }