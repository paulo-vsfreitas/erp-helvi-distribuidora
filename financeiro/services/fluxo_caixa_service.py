from decimal import Decimal

from django.db.models import Q, Sum

from financeiro.forms.fluxo_caixa import (
    FluxoCaixaFiltroForm,
)
from financeiro.models import (
    ContaFinanceira,
    MovimentacaoFinanceira,
)
from financeiro.services.dashboard_service import (
    formatar_moeda,
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


def _obter_valor_assinado(movimentacao):
    """
    Retorna o impacto da movimentação no saldo.

    Entradas e estornos de saída somam.
    Saídas e estornos de entrada subtraem.
    Ajustes permanecem neutros, seguindo a mesma regra
    atual do saldo da ContaFinanceira.
    """
    if movimentacao.tipo in TIPOS_ENTRADA:
        return movimentacao.valor

    if movimentacao.tipo in TIPOS_SAIDA:
        return -movimentacao.valor

    return ZERO


def _obter_origem_exibicao(movimentacao):
    """
    Identifica a origem funcional da movimentação.
    """
    if movimentacao.baixa_pagar_id:
        return "Conta a pagar"

    if movimentacao.recebimento_conta_id:
        return "Conta a receber"

    if movimentacao.origem:
        return movimentacao.origem

    return "Movimentação manual"


def _somar_movimentacoes(
    queryset,
    tipos,
):
    return (
        queryset
        .filter(tipo__in=tipos)
        .aggregate(total=Sum("valor"))["total"]
        or ZERO
    )


def _obter_saldo_anterior(
    *,
    data_inicial,
    conta_financeira=None,
):
    """
    Calcula o saldo existente antes do início do período.

    Quando uma conta é selecionada, calcula somente o
    saldo anterior daquela conta.

    Sem conta selecionada, consolida todas as contas
    financeiras.
    """
    contas = ContaFinanceira.objects.all()

    if conta_financeira:
        contas = contas.filter(pk=conta_financeira.pk)

    saldo_anterior = ZERO

    for conta in contas:
        saldo_conta = conta.saldo_inicial

        movimentacoes_anteriores = (
            MovimentacaoFinanceira.objects
            .filter(
                conta_financeira=conta,
                estornada=False,
            )
        )

        if data_inicial:
            movimentacoes_anteriores = (
                movimentacoes_anteriores
                .filter(
                    data_movimentacao__lt=data_inicial,
                )
            )

        entradas = _somar_movimentacoes(
            movimentacoes_anteriores,
            TIPOS_ENTRADA,
        )

        saidas = _somar_movimentacoes(
            movimentacoes_anteriores,
            TIPOS_SAIDA,
        )

        saldo_conta += entradas - saidas
        saldo_anterior += saldo_conta

    return saldo_anterior


def obter_fluxo_caixa(parametros):
    """
    Filtra as movimentações e monta o fluxo de caixa
    com saldo acumulado.
    """
    form = FluxoCaixaFiltroForm(parametros or None)

    movimentacoes = (
        MovimentacaoFinanceira.objects
        .select_related(
            "conta_financeira",
            "categoria",
            "criado_por",
            "baixa_pagar",
            "recebimento_conta",
        )
    )

    filtros = {
        "data_inicial": None,
        "data_final": None,
        "conta_financeira": None,
        "categoria": None,
        "tipo": "",
        "status": FluxoCaixaFiltroForm.STATUS_VALIDAS,
        "busca": "",
    }

    if form.is_valid():
        filtros.update(form.cleaned_data)

        data_inicial = filtros["data_inicial"]
        data_final = filtros["data_final"]
        conta_financeira = filtros["conta_financeira"]
        categoria = filtros["categoria"]
        tipo = filtros["tipo"]
        status = filtros["status"]
        busca = filtros["busca"]

        if data_inicial:
            movimentacoes = movimentacoes.filter(
                data_movimentacao__gte=data_inicial,
            )

        if data_final:
            movimentacoes = movimentacoes.filter(
                data_movimentacao__lte=data_final,
            )

        if conta_financeira:
            movimentacoes = movimentacoes.filter(
                conta_financeira=conta_financeira,
            )

        if categoria:
            movimentacoes = movimentacoes.filter(
                categoria=categoria,
            )

        if tipo:
            movimentacoes = movimentacoes.filter(
                tipo=tipo,
            )

        if (
            status
            == FluxoCaixaFiltroForm.STATUS_ESTORNADAS
        ):
            movimentacoes = movimentacoes.filter(
                estornada=True,
            )

        elif status == FluxoCaixaFiltroForm.STATUS_TODAS:
            pass

        else:
            movimentacoes = movimentacoes.filter(
                estornada=False,
            )

        if busca:
            movimentacoes = movimentacoes.filter(
                Q(descricao__icontains=busca)
                | Q(origem__icontains=busca)
                | Q(
                    conta_financeira__nome__icontains=busca
                )
                | Q(categoria__nome__icontains=busca)
            )

    else:
        movimentacoes = movimentacoes.filter(
            estornada=False,
        )

    movimentacoes = movimentacoes.order_by(
        "data_movimentacao",
        "criado_em",
        "pk",
    )

    saldo_anterior = _obter_saldo_anterior(
        data_inicial=filtros["data_inicial"],
        conta_financeira=filtros["conta_financeira"],
    )

    saldo_acumulado = saldo_anterior
    total_entradas = ZERO
    total_saidas = ZERO

    linhas = []

    for movimentacao in movimentacoes:
        valor_assinado = _obter_valor_assinado(
            movimentacao
        )

        entrada = ZERO
        saida = ZERO

        if valor_assinado > ZERO:
            entrada = valor_assinado
            total_entradas += entrada

        elif valor_assinado < ZERO:
            saida = abs(valor_assinado)
            total_saidas += saida

        if not movimentacao.estornada:
            saldo_acumulado += valor_assinado

        linhas.append(
            {
                "movimentacao": movimentacao,
                "entrada": entrada,
                "saida": saida,
                "saldo_acumulado": saldo_acumulado,
                "origem_exibicao": (
                    _obter_origem_exibicao(
                        movimentacao
                    )
                ),
            }
        )

    resultado_periodo = total_entradas - total_saidas

    return {
        "form": form,
        "linhas": linhas,

        "saldo_anterior": saldo_anterior,
        "saldo_anterior_formatado": formatar_moeda(
            saldo_anterior
        ),

        "total_entradas": total_entradas,
        "total_entradas_formatado": formatar_moeda(
            total_entradas
        ),

        "total_saidas": total_saidas,
        "total_saidas_formatado": formatar_moeda(
            total_saidas
        ),

        "resultado_periodo": resultado_periodo,
        "resultado_periodo_formatado": formatar_moeda(
            resultado_periodo
        ),

        "saldo_final": saldo_acumulado,
        "saldo_final_formatado": formatar_moeda(
            saldo_acumulado
        ),

        "quantidade_movimentacoes": len(linhas),
    }