from django.db import transaction
from decimal import Decimal

from django.db.models import Q, Sum

from financeiro.models import ContaFinanceira


def listar_contas_financeiras(
    busca="",
    tipo="",
    status="ativas",
):
    todas_contas = ContaFinanceira.objects.all()

    busca = (busca or "").strip()
    tipo = (tipo or "").strip()
    status = (status or "ativas").strip()

    conta_padrao = (
        todas_contas
        .filter(conta_padrao=True)
        .first()
    )

    indicadores = {
        "total": todas_contas.count(),
        "ativas": todas_contas.filter(ativo=True).count(),
        "inativas": todas_contas.filter(ativo=False).count(),
        "conta_padrao": conta_padrao,
    }

    contas_filtradas = todas_contas

    if busca:
        contas_filtradas = contas_filtradas.filter(
            Q(nome__icontains=busca)
            | Q(instituicao__icontains=busca)
            | Q(identificador__icontains=busca)
            | Q(numero_conta__icontains=busca)
            | Q(agencia__icontains=busca)
        )

    tipos_validos = {
        valor
        for valor, _rotulo in ContaFinanceira.TIPO_CHOICES
    }

    if tipo in tipos_validos:
        contas_filtradas = contas_filtradas.filter(tipo=tipo)

    if status == "ativas":
        contas_filtradas = contas_filtradas.filter(ativo=True)
    elif status == "inativas":
        contas_filtradas = contas_filtradas.filter(ativo=False)

    return {
        "contas": contas_filtradas.order_by(
            "-conta_padrao",
            "nome",
        ),
        "indicadores": indicadores,
    }


@transaction.atomic
def salvar_conta_financeira(form):
    conta = form.save(commit=False)

    if conta.conta_padrao:
        contas_padrao = (
            ContaFinanceira.objects
            .select_for_update()
            .exclude(pk=conta.pk)
            .filter(conta_padrao=True)
        )

        contas_padrao.update(conta_padrao=False)

    conta.save()

    return conta


@transaction.atomic
def inativar_conta_financeira(conta):
    if not conta.ativo:
        raise ValueError(
            "Esta conta financeira já está inativa."
        )

    if conta.conta_padrao:
        raise ValueError(
            "A conta padrão não pode ser inativada. "
            "Defina outra conta como padrão primeiro."
        )

    conta.ativo = False
    conta.save(
        update_fields=[
            "ativo",
            "data_atualizacao",
        ]
    )

    return conta


@transaction.atomic
def reativar_conta_financeira(conta):
    if conta.ativo:
        raise ValueError(
            "Esta conta financeira já está ativa."
        )

    conta.ativo = True
    conta.save(
        update_fields=[
            "ativo",
            "data_atualizacao",
        ]
    )

    return conta

def formatar_moeda(valor):
    valor = valor or Decimal("0.00")

    formatado = f"{valor:,.2f}"

    formatado = (
        formatado
        .replace(",", "TEMP")
        .replace(".", ",")
        .replace("TEMP", ".")
    )

    return f"R$ {formatado}"

def obter_dados_ficha_conta_financeira(conta):
    movimentacoes_validas = conta.movimentacoes.filter(
        estornada=False,
    )

    totais = movimentacoes_validas.aggregate(
        total_entradas=Sum(
            "valor",
            filter=Q(
                tipo__in=[
                    conta.movimentacoes.model.TIPO_ENTRADA,
                    conta.movimentacoes.model.TIPO_ESTORNO_SAIDA,
                ]
            ),
        ),
        total_saidas=Sum(
            "valor",
            filter=Q(
                tipo__in=[
                    conta.movimentacoes.model.TIPO_SAIDA,
                    conta.movimentacoes.model.TIPO_ESTORNO_ENTRADA,
                ]
            ),
        ),
    )

    total_entradas = (
        totais["total_entradas"]
        or Decimal("0.00")
    )

    total_saidas = (
        totais["total_saidas"]
        or Decimal("0.00")
    )

    ultimas_movimentacoes = (
        movimentacoes_validas
        .select_related(
            "categoria",
            "criado_por",
        )
        .order_by(
            "-data_movimentacao",
            "-criado_em",
        )[:10]
    )

    cards = [
        {
            "titulo": "Saldo atual",
            "valor": formatar_moeda(conta.saldo_atual),
            "icone": "bi bi-wallet2",
            "cor": "primary",
        },
        {
            "titulo": "Total de entradas",
            "valor": formatar_moeda(total_entradas),
            "icone": "bi bi-arrow-down-circle",
            "cor": "success",
        },
        {
            "titulo": "Total de saídas",
            "valor": formatar_moeda(total_saidas),
            "icone": "bi bi-arrow-up-circle",
            "cor": "danger",
        },
        {
            "titulo": "Saldo inicial",
            "valor": formatar_moeda(conta.saldo_inicial),
            "icone": "bi bi-cash-stack",
            "cor": "warning",
        },
    ]

    return {
        "cards": cards,
        "total_entradas": total_entradas,
        "total_saidas": total_saidas,
        "ultimas_movimentacoes": ultimas_movimentacoes,
    }