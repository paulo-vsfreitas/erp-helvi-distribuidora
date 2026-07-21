import calendar
from datetime import date
from decimal import Decimal

from django.db import transaction
from django.db.models import Prefetch, Q, Sum
from django.utils import timezone

from financeiro.models import (
    ContaReceber,
    HistoricoContaReceber,
    MovimentacaoFinanceira,
    ParcelaReceber,
    RecebimentoConta,
)


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


def adicionar_meses(data_base, quantidade_meses):
    """
    Avança uma data preservando o dia sempre que possível.

    Exemplo:
    31/01 + 1 mês = último dia de fevereiro.
    """
    mes_total = data_base.month - 1 + quantidade_meses
    ano = data_base.year + mes_total // 12
    mes = mes_total % 12 + 1

    ultimo_dia_mes = calendar.monthrange(ano, mes)[1]
    dia = min(data_base.day, ultimo_dia_mes)

    return date(ano, mes, dia)


def registrar_historico_conta_receber(
    *,
    conta,
    tipo_evento,
    descricao,
    usuario,
    dados=None,
):
    """
    Centraliza a criação do histórico da Conta a Receber.
    """
    return HistoricoContaReceber.objects.create(
        conta_receber=conta,
        tipo_evento=tipo_evento,
        descricao=descricao,
        dados=dados or {},
        usuario=usuario,
    )


@transaction.atomic
def criar_conta_receber_manual(
    *,
    dados,
    usuario,
):
    """
    Cria uma Conta a Receber manual e gera suas parcelas.

    O valor é dividido igualmente entre as parcelas.
    Eventual diferença de centavos é aplicada na última parcela.
    """
    dados = dados.copy()

    quantidade_parcelas = dados.pop("quantidade_parcelas")
    primeiro_vencimento = dados.pop("primeiro_vencimento")

    valor_total = dados["valor_total"]

    if quantidade_parcelas <= 0:
        raise ValueError(
            "A quantidade de parcelas deve ser maior que zero."
        )

    if valor_total <= 0:
        raise ValueError(
            "O valor total da conta deve ser maior que zero."
        )

    conta = ContaReceber.objects.create(
        **dados,
        criado_por=usuario,
    )

    valor_base = (
        valor_total / quantidade_parcelas
    ).quantize(Decimal("0.01"))

    valor_distribuido = Decimal("0.00")
    parcelas_criadas = []

    for numero in range(1, quantidade_parcelas + 1):
        if numero == quantidade_parcelas:
            valor_parcela = valor_total - valor_distribuido
        else:
            valor_parcela = valor_base
            valor_distribuido += valor_parcela

        vencimento = adicionar_meses(
            primeiro_vencimento,
            numero - 1,
        )

        parcela = ParcelaReceber.objects.create(
            conta_receber=conta,
            numero=numero,
            data_vencimento=vencimento,
            valor_original=valor_parcela,
            observacoes=(
                "Parcela gerada no cadastro manual "
                "da Conta a Receber."
            ),
        )

        parcelas_criadas.append(parcela)

    registrar_historico_conta_receber(
        conta=conta,
        tipo_evento=HistoricoContaReceber.EVENTO_CRIACAO,
        descricao="Conta a Receber criada manualmente.",
        dados={
            "valor_total": str(conta.valor_total),
            "quantidade_parcelas": quantidade_parcelas,
            "primeiro_vencimento": primeiro_vencimento.isoformat(),
        },
        usuario=usuario,
    )

    for parcela in parcelas_criadas:
        registrar_historico_conta_receber(
            conta=conta,
            tipo_evento=(
                HistoricoContaReceber.EVENTO_PARCELA_CRIADA
            ),
            descricao=(
                f"Parcela {parcela.numero} criada com vencimento "
                f"em {parcela.data_vencimento.strftime('%d/%m/%Y')}."
            ),
            dados={
                "parcela_id": parcela.pk,
                "numero": parcela.numero,
                "vencimento": parcela.data_vencimento.isoformat(),
                "valor": str(parcela.valor_original),
            },
            usuario=usuario,
        )

    return conta


def listar_contas_receber(request):
    """
    Retorna as Contas a Receber com os filtros da listagem.
    """
    contas = (
        ContaReceber.objects
        .select_related(
            "cliente",
            "categoria",
        )
        .order_by(
            "-criado_em",
        )
    )

    busca = (request.GET.get("q") or "").strip()
    status = (request.GET.get("status") or "").strip()
    origem = (request.GET.get("origem") or "").strip()
    vencidas = request.GET.get("vencidas")

    if busca:
        filtros = (
            Q(descricao__icontains=busca)
            | Q(nome_devedor__icontains=busca)
            | Q(documento_devedor__icontains=busca)
        )

        if busca.isdigit():
            filtros |= Q(numero=int(busca))

        contas = contas.filter(filtros)

    if status:
        contas = contas.filter(status=status)

    if origem:
        contas = contas.filter(origem=origem)

    if vencidas:
        hoje = timezone.localdate()

        contas = contas.filter(
            parcelas__data_vencimento__lt=hoje,
            parcelas__status__in=[
                ParcelaReceber.STATUS_PENDENTE,
                ParcelaReceber.STATUS_PARCIAL,
            ],
        ).distinct()

    return {
        "contas": contas,
        "busca": busca,
        "status_selecionado": status,
        "origem_selecionada": origem,
        "somente_vencidas": bool(vencidas),
    }


def obter_dados_ficha_conta_receber(conta_id):
    """
    Carrega todos os dados necessários para a Ficha da Conta a Receber.

    A view apenas recebe o resultado pronto, evitando regras de negócio
    e consultas espalhadas pelo template.
    """
    parcelas_queryset = (
        ParcelaReceber.objects
        .prefetch_related(
            Prefetch(
                "recebimentos",
                queryset=(
                    RecebimentoConta.objects
                    .select_related(
                        "conta_financeira",
                        "registrado_por",
                        "estornado_por",
                    )
                    .order_by(
                        "-data_recebimento",
                        "-registrado_em",
                    )
                ),
            )
        )
        .order_by(
            "data_vencimento",
            "numero",
        )
    )

    historicos_queryset = (
        HistoricoContaReceber.objects
        .select_related("usuario")
        .order_by(
            "-criado_em",
            "-id",
        )
    )

    conta = (
        ContaReceber.objects
        .select_related(
            "cliente",
            "categoria",
            "criado_por",
            "cancelado_por",
        )
        .prefetch_related(
            Prefetch(
                "parcelas",
                queryset=parcelas_queryset,
            ),
            Prefetch(
                "historicos",
                queryset=historicos_queryset,
            ),
        )
        .get(pk=conta_id)
    )

    movimentacoes = (
        MovimentacaoFinanceira.objects
        .filter(
            recebimento_conta__parcela__conta_receber=conta,
        )
        .select_related(
            "conta_financeira",
            "categoria",
            "recebimento_conta",
            "criado_por",
        )
        .order_by(
            "-data_movimentacao",
            "-criado_em",
        )
    )

    total_parcelas = conta.parcelas.count()

    parcelas_recebidas = conta.parcelas.filter(
        status=ParcelaReceber.STATUS_RECEBIDA,
    ).count()

    parcelas_pendentes = conta.parcelas.filter(
        status__in=[
            ParcelaReceber.STATUS_PENDENTE,
            ParcelaReceber.STATUS_PARCIAL,
        ],
    ).count()

    proxima_parcela_receber = (
        conta.parcelas
        .exclude(
            status__in=[
                ParcelaReceber.STATUS_RECEBIDA,
                ParcelaReceber.STATUS_CANCELADA,
            ],
        )
        .order_by(
            "data_vencimento",
            "numero",
        )
        .first()
    )

    if conta.valor_total > 0:
        percentual_recebido = min(
            (
                conta.valor_recebido
                / conta.valor_total
            )
            * Decimal("100"),
            Decimal("100.00"),
        )
    else:
        percentual_recebido = Decimal("0.00")

    hoje = timezone.localdate()
    parcelas_exibicao = []

    for parcela in conta.parcelas.all():
        if parcela.status == ParcelaReceber.STATUS_RECEBIDA:
            parcela.badge_class = "text-bg-success"
            parcela.situacao_texto = "Recebida"
            parcela.detalhe_vencimento = ""

        elif parcela.status == ParcelaReceber.STATUS_CANCELADA:
            parcela.badge_class = "text-bg-secondary"
            parcela.situacao_texto = "Cancelada"
            parcela.detalhe_vencimento = ""

        elif parcela.data_vencimento < hoje:
            dias_atraso = (
                hoje - parcela.data_vencimento
            ).days

            parcela.badge_class = "text-bg-danger"
            parcela.situacao_texto = "Vencida"
            parcela.detalhe_vencimento = (
                f"{dias_atraso} dia"
                if dias_atraso == 1
                else f"{dias_atraso} dias"
            )

        elif parcela.data_vencimento == hoje:
            parcela.badge_class = "text-bg-warning"
            parcela.situacao_texto = "Vence hoje"
            parcela.detalhe_vencimento = ""

        elif parcela.status == ParcelaReceber.STATUS_PARCIAL:
            parcela.badge_class = "text-bg-warning"
            parcela.situacao_texto = "Parcial"

            dias_restantes = (
                parcela.data_vencimento - hoje
            ).days

            parcela.detalhe_vencimento = (
                f"Vence em {dias_restantes} dia"
                if dias_restantes == 1
                else f"Vence em {dias_restantes} dias"
            )

        else:
            parcela.badge_class = "text-bg-primary"
            parcela.situacao_texto = "Pendente"

            dias_restantes = (
                parcela.data_vencimento - hoje
            ).days

            parcela.detalhe_vencimento = (
                f"Vence em {dias_restantes} dia"
                if dias_restantes == 1
                else f"Vence em {dias_restantes} dias"
            )

        parcelas_exibicao.append(parcela)

    icones_historico = {
        HistoricoContaReceber.EVENTO_CRIACAO: (
            "bi bi-plus-circle"
        ),
        HistoricoContaReceber.EVENTO_EDICAO: (
            "bi bi-pencil"
        ),
        HistoricoContaReceber.EVENTO_PARCELA_CRIADA: (
            "bi bi-calendar-plus"
        ),
        HistoricoContaReceber.EVENTO_PARCELA_EDITADA: (
            "bi bi-calendar-event"
        ),
        HistoricoContaReceber.EVENTO_RECEBIMENTO: (
            "bi bi-cash-coin"
        ),
        HistoricoContaReceber.EVENTO_ESTORNO: (
            "bi bi-arrow-counterclockwise"
        ),
        HistoricoContaReceber.EVENTO_CANCELAMENTO: (
            "bi bi-x-circle"
        ),
        HistoricoContaReceber.EVENTO_REATIVACAO: (
            "bi bi-arrow-clockwise"
        ),
        HistoricoContaReceber.EVENTO_INTEGRACAO_VENDA: (
            "bi bi-cart-check"
        ),
        HistoricoContaReceber.EVENTO_OUTRO: (
            "bi bi-clock-history"
        ),
    }

    historicos_exibicao = []

    for historico in conta.historicos.all():
        historico.icone = icones_historico.get(
            historico.tipo_evento,
            "bi bi-clock-history",
        )

        historicos_exibicao.append(historico)

    valor_movimentado = (
        movimentacoes
        .filter(estornada=False)
        .aggregate(total=Sum("valor"))["total"]
        or Decimal("0.00")
    )

    cards = [
        {
            "titulo": "Status",
            "valor": conta.get_status_display(),
            "icone": "bi bi-activity",
            "cor": (
                "success"
                if conta.status == ContaReceber.STATUS_RECEBIDA
                else "danger"
                if conta.status == ContaReceber.STATUS_CANCELADA
                else "warning"
            ),
        },
        {
            "titulo": "Valor total",
            "valor": formatar_moeda(conta.valor_total),
            "icone": "bi bi-cash-stack",
            "cor": "primary",
        },
        {
            "titulo": "Total recebido",
            "valor": formatar_moeda(valor_movimentado),
            "icone": "bi bi-cash-coin",
            "cor": "success",
        },
        {
            "titulo": "Saldo",
            "valor": formatar_moeda(conta.saldo),
            "icone": "bi bi-wallet2",
            "cor": "danger",
        },
    ]

    return {
        "conta": conta,
        "cards": cards,
        "parcelas": parcelas_exibicao,
        "historicos": historicos_exibicao,
        "movimentacoes": movimentacoes[:20],
        "total_parcelas": total_parcelas,
        "parcelas_recebidas": parcelas_recebidas,
        "parcelas_pendentes": parcelas_pendentes,
        "valor_movimentado": valor_movimentado,
        "percentual_recebido": percentual_recebido,
        "proxima_parcela_receber": proxima_parcela_receber,
    }