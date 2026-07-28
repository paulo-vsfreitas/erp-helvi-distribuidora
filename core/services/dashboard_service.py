from decimal import Decimal

from django.db.models import (
    DecimalField,
    ExpressionWrapper,
    F,
    Sum,
)
from django.utils import timezone

from financeiro.models import (
    ContaFinanceira,
    ContaReceber,
    ParcelaReceber,
)
from produtos.models import Produto
from vendas.models import Venda


VALOR_ZERO = Decimal("0.00")


def obter_vendas_hoje():
    hoje = timezone.localdate()

    vendas = Venda.objects.filter(
        data_venda__date=hoje,
        status=Venda.STATUS_FINALIZADA,
    )

    total = vendas.aggregate(
        total=Sum("total")
    )["total"] or VALOR_ZERO

    return {
        "quantidade": vendas.count(),
        "valor": total,
    }


def obter_faturamento_mes():
    hoje = timezone.localdate()
    inicio_mes = hoje.replace(day=1)

    vendas = Venda.objects.filter(
        data_venda__date__gte=inicio_mes,
        data_venda__date__lte=hoje,
        status=Venda.STATUS_FINALIZADA,
    )

    total = vendas.aggregate(
        total=Sum("total")
    )["total"] or VALOR_ZERO

    return {
        "quantidade": vendas.count(),
        "valor": total,
    }


def obter_saldo_financeiro():
    contas = (
        ContaFinanceira.objects
        .filter(ativo=True)
        .prefetch_related("movimentacoes")
    )

    saldo_total = sum(
        (
            conta.saldo_atual
            for conta in contas
        ),
        VALOR_ZERO,
    )

    return {
        "quantidade_contas": contas.count(),
        "valor": saldo_total,
    }


def obter_contas_receber():
    expressao_saldo = ExpressionWrapper(
        F("valor_total") - F("valor_recebido"),
        output_field=DecimalField(
            max_digits=14,
            decimal_places=2,
        ),
    )

    contas = ContaReceber.objects.filter(
        status__in=[
            ContaReceber.STATUS_PENDENTE,
            ContaReceber.STATUS_PARCIAL,
        ],
    )

    total = contas.aggregate(
        total=Sum(expressao_saldo)
    )["total"] or VALOR_ZERO

    return {
        "quantidade": contas.count(),
        "valor": total,
    }


def obter_resumo_produtos():
    produtos_ativos = Produto.objects.filter(
        ativo=True,
    )

    estoque_baixo = produtos_ativos.filter(
        estoque_minimo__gt=0,
        estoque_atual__lte=F("estoque_minimo"),
    )

    unidades_estoque = produtos_ativos.aggregate(
        total=Sum("estoque_atual")
    )["total"] or 0

    return {
        "quantidade_produtos": produtos_ativos.count(),
        "unidades_estoque": unidades_estoque,
        "estoque_baixo": estoque_baixo.count(),
    }


def obter_alertas_financeiros():
    hoje = timezone.localdate()

    status_em_aberto = [
        ParcelaReceber.STATUS_PENDENTE,
        ParcelaReceber.STATUS_PARCIAL,
    ]

    parcelas_vencidas = ParcelaReceber.objects.filter(
        status__in=status_em_aberto,
        data_vencimento__lt=hoje,
    )

    parcelas_hoje = ParcelaReceber.objects.filter(
        status__in=status_em_aberto,
        data_vencimento=hoje,
    )

    saldo_vencido = ExpressionWrapper(
        F("valor_original") - F("valor_recebido"),
        output_field=DecimalField(
            max_digits=14,
            decimal_places=2,
        ),
    )

    valor_vencido = parcelas_vencidas.aggregate(
        total=Sum(saldo_vencido)
    )["total"] or VALOR_ZERO

    valor_vencendo_hoje = parcelas_hoje.aggregate(
        total=Sum(saldo_vencido)
    )["total"] or VALOR_ZERO

    return {
        "parcelas_vencidas": parcelas_vencidas.count(),
        "valor_vencido": valor_vencido,
        "parcelas_hoje": parcelas_hoje.count(),
        "valor_vencendo_hoje": valor_vencendo_hoje,
    }


def obter_ultimas_vendas():
    return (
        Venda.objects
        .filter(
            status=Venda.STATUS_FINALIZADA,
        )
        .select_related(
            "cliente",
            "finalizada_por",
        )
        .order_by(
            "-finalizada_em",
            "-id",
        )[:5]
    )


def obter_contexto_dashboard():
    produtos = obter_resumo_produtos()
    alertas_financeiros = obter_alertas_financeiros()

    return {
        "dashboard": {
            "vendas_hoje": obter_vendas_hoje(),
            "faturamento_mes": obter_faturamento_mes(),
            "saldo_financeiro": obter_saldo_financeiro(),
            "contas_receber": obter_contas_receber(),
            "produtos": produtos,
            "alertas": {
                "estoque_baixo": produtos["estoque_baixo"],
                **alertas_financeiros,
            },
            "ultimas_vendas": obter_ultimas_vendas(),
        }
    }