from core.services.indicadores import (
    criar_indicador,
    formatar_moeda,
)

from decimal import Decimal

from django.db.models import (
    Count,
    DecimalField,
    ExpressionWrapper,
    F,
    Sum,
    Value,
)
from django.db.models.functions import Coalesce

from vendas.models import ItemVenda, Venda


ZERO_DECIMAL = Value(
    Decimal("0.00"),
    output_field=DecimalField(
        max_digits=12,
        decimal_places=2,
    ),
)


def obter_vendas_filtradas(filtros):
    vendas = (
        Venda.objects
        .select_related(
            "cliente",
            "criada_por",
            "finalizada_por",
            "conta_financeira",
        )
        .annotate(
            total_pecas=Coalesce(
                Sum("itens__quantidade"),
                Value(0),
            ),
        )
        .order_by("-data_venda", "-numero")
    )

    data_inicial = filtros.get("data_inicial")
    data_final = filtros.get("data_final")
    cliente = filtros.get("cliente")
    vendedor = filtros.get("vendedor")
    forma_pagamento = filtros.get("forma_pagamento")
    status = filtros.get("status")
    status_pagamento = filtros.get("status_pagamento")
    consumidor_final = filtros.get("consumidor_final")

    if data_inicial:
        vendas = vendas.filter(
            data_venda__date__gte=data_inicial,
        )

    if data_final:
        vendas = vendas.filter(
            data_venda__date__lte=data_final,
        )

    if cliente:
        vendas = vendas.filter(
            cliente=cliente,
        )

    if vendedor:
        vendas = vendas.filter(
            finalizada_por=vendedor,
        )

    if forma_pagamento:
        vendas = vendas.filter(
            forma_pagamento=forma_pagamento,
        )

    if status:
        vendas = vendas.filter(
            status=status,
        )

    if status_pagamento:
        vendas = vendas.filter(
            status_pagamento=status_pagamento,
        )

    if consumidor_final == "sim":
        vendas = vendas.filter(
            cliente__isnull=True,
        )

    elif consumidor_final == "nao":
        vendas = vendas.filter(
            cliente__isnull=False,
        )

    return vendas


def calcular_indicadores_relatorio(vendas):
    vendas_finalizadas = vendas.filter(
        status=Venda.STATUS_FINALIZADA,
    )

    valores = vendas_finalizadas.aggregate(
        quantidade_vendas=Count(
            "pk",
            distinct=True,
        ),
        faturamento=Coalesce(
            Sum("total"),
            ZERO_DECIMAL,
        ),
        total_recebido=Coalesce(
            Sum("valor_recebido"),
            ZERO_DECIMAL,
        ),
        clientes_atendidos=Count(
            "cliente",
            distinct=True,
        ),
    )

    quantidade_vendas = valores["quantidade_vendas"]
    faturamento = valores["faturamento"]
    total_recebido = valores["total_recebido"]

    saldo_pendente = max(
        faturamento - total_recebido,
        Decimal("0.00"),
    )

    ticket_medio = Decimal("0.00")

    if quantidade_vendas:
        ticket_medio = faturamento / quantidade_vendas

    quantidade_pecas = (
        ItemVenda.objects
        .filter(
            venda__in=vendas_finalizadas,
        )
        .aggregate(
            total=Coalesce(
                Sum("quantidade"),
                Value(0),
            ),
        )
        ["total"]
    )

    return {
        "quantidade_vendas": quantidade_vendas,
        "faturamento": faturamento,
        "total_recebido": total_recebido,
        "saldo_pendente": saldo_pendente,
        "ticket_medio": ticket_medio,
        "quantidade_pecas": quantidade_pecas,
        "clientes_atendidos": valores["clientes_atendidos"],
    }


def obter_resumo_formas_pagamento(vendas):
    return (
        vendas
        .filter(
            status=Venda.STATUS_FINALIZADA,
        )
        .values(
            "forma_pagamento",
        )
        .annotate(
            quantidade=Count(
                "pk",
                distinct=True,
            ),
            total=Coalesce(
                Sum("total"),
                ZERO_DECIMAL,
            ),
        )
        .order_by("-total")
    )


def obter_resumo_status_pagamento(vendas):
    return (
        vendas
        .filter(
            status=Venda.STATUS_FINALIZADA,
        )
        .values(
            "status_pagamento",
        )
        .annotate(
            quantidade=Count(
                "pk",
                distinct=True,
            ),
            total=Coalesce(
                Sum("total"),
                ZERO_DECIMAL,
            ),
        )
        .order_by("-total")
    )


def obter_produtos_mais_vendidos(vendas, limite=10):
    return (
        ItemVenda.objects
        .filter(
            venda__in=vendas.filter(
                status=Venda.STATUS_FINALIZADA,
            ),
        )
        .values(
            "produto_id",
            "produto__codigo",
            "produto__modelo",
        )
        .annotate(
            quantidade=Sum("quantidade"),
            total=Coalesce(
                Sum("total"),
                ZERO_DECIMAL,
            ),
        )
        .order_by(
            "-quantidade",
            "-total",
        )[:limite]
    )

def montar_kpis_relatorio_vendas(indicadores):
    return [
        criar_indicador(
            titulo="Faturamento",
            valor=formatar_moeda(
                indicadores["faturamento"],
            ),
            icone="bi-cash-stack",
            subtitulo="Vendas finalizadas no período",
        ),
        criar_indicador(
            titulo="Vendas",
            valor=indicadores["quantidade_vendas"],
            icone="bi-cart-check",
            subtitulo="Vendas finalizadas",
        ),
        criar_indicador(
            titulo="Peças vendidas",
            valor=indicadores["quantidade_pecas"],
            icone="bi-box-seam",
            subtitulo="Quantidade total de produtos",
        ),
        criar_indicador(
            titulo="Ticket médio",
            valor=formatar_moeda(
                indicadores["ticket_medio"],
            ),
            icone="bi-graph-up-arrow",
            subtitulo="Média por venda",
        ),
        criar_indicador(
            titulo="Total recebido",
            valor=formatar_moeda(
                indicadores["total_recebido"],
            ),
            icone="bi-wallet2",
            subtitulo="Valores já recebidos",
        ),
        criar_indicador(
            titulo="Saldo pendente",
            valor=formatar_moeda(
                indicadores["saldo_pendente"],
            ),
            icone="bi-hourglass-split",
            subtitulo="Valores ainda não recebidos",
        ),
        criar_indicador(
            titulo="Clientes",
            valor=indicadores["clientes_atendidos"],
            icone="bi-people",
            subtitulo="Clientes cadastrados atendidos",
        ),
    ]