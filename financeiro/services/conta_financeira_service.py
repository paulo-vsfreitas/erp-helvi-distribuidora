from decimal import Decimal

from django.db import transaction
from django.db.models import Count, Max, Q, Sum

from financeiro.models import (
    ContaFinanceira,
    MovimentacaoFinanceira,
)




ZERO = Decimal("0.00")


TIPOS_ENTRADA = [
    MovimentacaoFinanceira.TIPO_ENTRADA,
    MovimentacaoFinanceira.TIPO_ESTORNO_SAIDA,
]

TIPOS_SAIDA = [
    MovimentacaoFinanceira.TIPO_SAIDA,
    MovimentacaoFinanceira.TIPO_ESTORNO_ENTRADA,
]


def formatar_moeda(valor):
    valor = valor or ZERO

    formatado = f"{valor:,.2f}"

    formatado = (
        formatado
        .replace(",", "TEMP")
        .replace(".", ",")
        .replace("TEMP", ".")
    )

    return f"R$ {formatado}"


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
        "ativas": todas_contas.filter(
            ativo=True
        ).count(),
        "inativas": todas_contas.filter(
            ativo=False
        ).count(),
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
        contas_filtradas = contas_filtradas.filter(
            tipo=tipo
        )

    if status == "ativas":
        contas_filtradas = contas_filtradas.filter(
            ativo=True
        )

    elif status == "inativas":
        contas_filtradas = contas_filtradas.filter(
            ativo=False
        )

    return {
        "contas": contas_filtradas.order_by(
            "-conta_padrao",
            "nome",
        ),
        "indicadores": indicadores,
    }

def conta_possui_movimentacoes(conta):
    if not conta or not conta.pk:
        return False

    return MovimentacaoFinanceira.objects.filter(
        conta_financeira_id=conta.pk,
    ).exists()


@transaction.atomic
def salvar_conta_financeira(form):
    conta = form.save(commit=False)

    if conta.pk:
        conta_original = (
            ContaFinanceira.objects
            .select_for_update()
            .get(pk=conta.pk)
        )

        if conta_possui_movimentacoes(
            conta_original
        ):
            tipo_alterado = (
                conta.tipo
                != conta_original.tipo
            )

            saldo_inicial_alterado = (
                conta.saldo_inicial
                != conta_original.saldo_inicial
            )

            data_inicial_alterada = (
                conta.data_saldo_inicial
                != conta_original.data_saldo_inicial
            )

            if tipo_alterado:
                raise ValueError(
                    "O tipo da conta não pode ser alterado, "
                    "pois ela já possui movimentações financeiras."
                )

            if saldo_inicial_alterado:
                raise ValueError(
                    "O saldo inicial não pode ser alterado, "
                    "pois a conta já possui movimentações financeiras."
                )

            if data_inicial_alterada:
                raise ValueError(
                    "A data do saldo inicial não pode ser alterada, "
                    "pois a conta já possui movimentações financeiras."
                )

    if conta.conta_padrao:
        contas_padrao = (
            ContaFinanceira.objects
            .select_for_update()
            .exclude(pk=conta.pk)
            .filter(conta_padrao=True)
        )

        contas_padrao.update(
            conta_padrao=False
        )

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


def _obter_origem_exibicao(movimentacao):
    if movimentacao.baixa_pagar_id:
        return "Conta a pagar"

    if movimentacao.recebimento_conta_id:
        return "Conta a receber"

    if movimentacao.origem:
        return movimentacao.origem.replace(
            "_",
            " ",
        ).title()

    return "Movimentação manual"


def obter_dados_ficha_conta_financeira(conta):
    movimentacoes_validas = (
        conta.movimentacoes
        .filter(estornada=False)
    )

    totais = movimentacoes_validas.aggregate(
        total_entradas=Sum(
            "valor",
            filter=Q(
                tipo__in=TIPOS_ENTRADA,
            ),
        ),
        total_saidas=Sum(
            "valor",
            filter=Q(
                tipo__in=TIPOS_SAIDA,
            ),
        ),
        quantidade_movimentacoes=Count("id"),
        ultima_movimentacao=Max(
            "data_movimentacao"
        ),
    )

    total_entradas = (
        totais["total_entradas"]
        or ZERO
    )

    total_saidas = (
        totais["total_saidas"]
        or ZERO
    )

    quantidade_movimentacoes = (
        totais["quantidade_movimentacoes"]
        or 0
    )

    ultima_movimentacao = (
        totais["ultima_movimentacao"]
    )

    resultado_movimentacoes = (
        total_entradas - total_saidas
    )

    movimentacoes_queryset = (
        movimentacoes_validas
        .select_related(
            "categoria",
            "criado_por",
            "baixa_pagar",
            "recebimento_conta",
        )
        .order_by(
            "-data_movimentacao",
            "-criado_em",
            "-pk",
        )
    )

    ultimas_movimentacoes = []

    for movimentacao in movimentacoes_queryset[:10]:
        movimentacao.origem_exibicao = (
            _obter_origem_exibicao(
                movimentacao
            )
        )

        movimentacao.eh_entrada = (
            movimentacao.tipo in TIPOS_ENTRADA
        )

        movimentacao.eh_saida = (
            movimentacao.tipo in TIPOS_SAIDA
        )

        ultimas_movimentacoes.append(
            movimentacao
        )

    cards = [
        {
            "titulo": "Saldo atual",
            "valor": formatar_moeda(
                conta.saldo_atual
            ),
            "icone": "bi bi-wallet2",
            "cor": "primary",
        },
        {
            "titulo": "Total de entradas",
            "valor": formatar_moeda(
                total_entradas
            ),
            "icone": "bi bi-arrow-down-circle",
            "cor": "success",
        },
        {
            "titulo": "Total de saídas",
            "valor": formatar_moeda(
                total_saidas
            ),
            "icone": "bi bi-arrow-up-circle",
            "cor": "danger",
        },
        {
            "titulo": "Movimentações",
            "valor": quantidade_movimentacoes,
            "icone": "bi bi-arrow-left-right",
            "cor": "warning",
        },
    ]

    return {
        "cards": cards,

        "total_entradas": total_entradas,
        "total_entradas_formatado": formatar_moeda(
            total_entradas
        ),

        "total_saidas": total_saidas,
        "total_saidas_formatado": formatar_moeda(
            total_saidas
        ),

        "resultado_movimentacoes": (
            resultado_movimentacoes
        ),
        "resultado_movimentacoes_formatado": (
            formatar_moeda(
                resultado_movimentacoes
            )
        ),

        "saldo_inicial_formatado": formatar_moeda(
            conta.saldo_inicial
        ),

        "saldo_atual_formatado": formatar_moeda(
            conta.saldo_atual
        ),

        "quantidade_movimentacoes": (
            quantidade_movimentacoes
        ),

        "ultima_movimentacao": ultima_movimentacao,

        "ultimas_movimentacoes": (
            ultimas_movimentacoes
        ),
    }