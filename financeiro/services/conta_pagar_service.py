import calendar
from datetime import date
from decimal import Decimal

from django.db import transaction
from django.db.models import Prefetch, Q, Sum
from django.utils import timezone

from financeiro.models import (
    CategoriaFinanceira,
    ContaPagar,
    HistoricoContaPagar,
    ParcelaPagar,
    BaixaPagar,
    MovimentacaoFinanceira,
)




NOME_CATEGORIA_COMPRA = "Compra de mercadorias"



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


def obter_ou_criar_categoria_compra():
    """
    Obtém a categoria padrão utilizada nas contas geradas por Compras.

    A categoria é criada automaticamente na primeira integração.
    Caso já exista como receita ou esteja inativa, a integração é
    interrompida para evitar classificação financeira incorreta.
    """

    categoria, criada = CategoriaFinanceira.objects.get_or_create(
        nome=NOME_CATEGORIA_COMPRA,
        defaults={
            "tipo": CategoriaFinanceira.TIPO_DESPESA,
            "descricao": (
                "Despesas geradas automaticamente pelo módulo de Compras."
            ),
            "ativo": True,
        },
    )

    if categoria.tipo != CategoriaFinanceira.TIPO_DESPESA:
        raise ValueError(
            'A categoria "Compra de mercadorias" existe, '
            "mas não está classificada como despesa."
        )

    if not categoria.ativo:
        raise ValueError(
            'A categoria financeira "Compra de mercadorias" está inativa. '
            "Reative-a antes de receber a compra."
        )

    return categoria


@transaction.atomic
def criar_conta_pagar_compra(*, compra, usuario):
    """
    Gera a Conta a Pagar vinculada a uma Compra.

    A operação é idempotente:
    - uma Compra terá no máximo uma Conta a Pagar;
    - chamadas repetidas não criam duplicidade;
    - inconsistências entre a flag financeiro_gerado e o vínculo
      financeiro são detectadas.
    """

    compra_model = compra.__class__

    compra = (
    compra_model.objects
        .select_for_update()
        .get(pk=compra.pk)
    )

    conta_existente = (
        ContaPagar.objects
        .select_for_update()
        .filter(compra=compra)
        .first()
    )

    if conta_existente:
        if not compra.financeiro_gerado:
            compra.financeiro_gerado = True
            compra.save(
                update_fields=[
                    "financeiro_gerado",
                    "atualizado_em",
                ]
            )

        return conta_existente

    if compra.financeiro_gerado:
        raise ValueError(
            "A compra está marcada como financeiro gerado, "
            "mas nenhuma Conta a Pagar vinculada foi encontrada."
        )

    if compra.total <= 0:
        raise ValueError(
            "Não é possível gerar uma Conta a Pagar "
            "para uma compra sem valor financeiro."
        )

    categoria = obter_ou_criar_categoria_compra()

    # Uma conta gerada pelo fluxo operacional de Compras sempre nasce
    # pendente. Valores pagos somente podem existir após uma baixa
    # financeira registrada.
    valor_pago_inicial = Decimal("0.00")

    conta = ContaPagar.objects.create(
        descricao=f"Compra #{compra.numero} — {compra.fornecedor_nome}",
        fornecedor=compra.fornecedor,
        compra=compra,
        categoria=categoria,
        data_emissao=compra.data_compra,
        data_competencia=compra.data_compra,
        valor_total=compra.total,
        valor_pago=valor_pago_inicial,
        observacoes=(
            "Conta gerada automaticamente no recebimento "
            f"da compra #{compra.numero}."
        ),
        criado_por=usuario,
    )

    # A Compra ainda não possui condições de pagamento/vencimentos.
    # Nesta primeira versão, a parcela automática vence na data
    # em que o recebimento é realizado.
    parcela = ParcelaPagar.objects.create(
        conta_pagar=conta,
        numero=1,
        data_vencimento=timezone.localdate(),
        valor_original=compra.total,
        valor_pago=valor_pago_inicial,
        observacoes=(
            "Parcela gerada automaticamente a partir "
            f"da compra #{compra.numero}."
        ),
    )

    HistoricoContaPagar.objects.create(
        conta_pagar=conta,
        tipo_evento=HistoricoContaPagar.EVENTO_INTEGRACAO_COMPRA,
        descricao=(
            f"Conta a Pagar gerada automaticamente "
            f"a partir da compra #{compra.numero}."
        ),
        dados={
            "compra_id": compra.pk,
            "compra_numero": compra.numero,
            "parcela_id": parcela.pk,
            "valor_total": str(compra.total),
            "valor_pago_inicial": str(valor_pago_inicial),
            "vencimento_inicial": parcela.data_vencimento.isoformat(),
        },
        usuario=usuario,
    )

    compra.financeiro_gerado = True
    compra.save(
        update_fields=[
            "financeiro_gerado",
            "atualizado_em",
        ]
    )

    return conta


def obter_dados_ficha_conta_pagar(conta_id):
    """
    Carrega os dados necessários para o Workspace da Conta a Pagar.

    Toda a preparação fica no service para evitar consultas e
    regras espalhadas pela view e pelo template.
    """

    parcelas_queryset = (
        ParcelaPagar.objects
        .prefetch_related(
            Prefetch(
                "baixas",
                queryset=(
                    BaixaPagar.objects
                    .select_related(
                        "conta_financeira",
                        "registrado_por",
                        "estornada_por",
                    )
                    .order_by(
                        "-data_pagamento",
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
        HistoricoContaPagar.objects
        .select_related("usuario")
        .order_by(
            "-criado_em",
            "-id",
        )
    )

    conta = (
        ContaPagar.objects
        .select_related(
            "fornecedor",
            "compra",
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
            baixa_pagar__parcela__conta_pagar=conta,
        )
        .select_related(
            "conta_financeira",
            "categoria",
            "baixa_pagar",
            "criado_por",
        )
        .order_by(
            "-data_movimentacao",
            "-criado_em",
        )
    )

    total_parcelas = conta.parcelas.count()

    parcelas_pagas = conta.parcelas.filter(
        status=ParcelaPagar.STATUS_PAGA,
    ).count()

    parcelas_pendentes = conta.parcelas.filter(
        status__in=[
            ParcelaPagar.STATUS_PENDENTE,
            ParcelaPagar.STATUS_PARCIAL,
        ],
    ).count()

    if conta.valor_total > 0:
        percentual_pago = min(
            (conta.valor_pago / conta.valor_total) * Decimal("100"),
            Decimal("100.00"),
        )
    else:
        percentual_pago = Decimal("0.00")

    hoje = timezone.localdate()

    parcelas_exibicao = []

    for parcela in conta.parcelas.all():
        if parcela.status == ParcelaPagar.STATUS_PAGA:
            parcela.badge_class = "text-bg-success"
            parcela.situacao_texto = "Paga"
            parcela.detalhe_vencimento = ""

        elif parcela.status == ParcelaPagar.STATUS_CANCELADA:
            parcela.badge_class = "text-bg-secondary"
            parcela.situacao_texto = "Cancelada"
            parcela.detalhe_vencimento = ""

        elif parcela.data_vencimento < hoje:
            dias_atraso = (hoje - parcela.data_vencimento).days

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

        elif parcela.status == ParcelaPagar.STATUS_PARCIAL:
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
        HistoricoContaPagar.EVENTO_CRIACAO: "bi bi-plus-circle",
        HistoricoContaPagar.EVENTO_EDICAO: "bi bi-pencil",
        HistoricoContaPagar.EVENTO_PARCELA_CRIADA: "bi bi-calendar-plus",
        HistoricoContaPagar.EVENTO_PARCELA_EDITADA: "bi bi-calendar-event",
        HistoricoContaPagar.EVENTO_BAIXA: "bi bi-cash-coin",
        HistoricoContaPagar.EVENTO_ESTORNO: "bi bi-arrow-counterclockwise",
        HistoricoContaPagar.EVENTO_CANCELAMENTO: "bi bi-x-circle",
        HistoricoContaPagar.EVENTO_REATIVACAO: "bi bi-arrow-clockwise",
        HistoricoContaPagar.EVENTO_INTEGRACAO_COMPRA: "bi bi-cart-check",
        HistoricoContaPagar.EVENTO_OUTRO: "bi bi-clock-history",
    }

    historicos_exibicao = []

    for historico in conta.historicos.all():
        historico.icone = icones_historico.get(
            historico.tipo_evento,
            "bi bi-clock-history",
        )

        historicos_exibicao.append(historico)

    totais_movimentados = movimentacoes.filter(estornada=False).aggregate(
        saidas=Sum(
            "valor",
            filter=Q(tipo=MovimentacaoFinanceira.TIPO_SAIDA),
        ),
        estornos=Sum(
            "valor",
            filter=Q(tipo=MovimentacaoFinanceira.TIPO_ESTORNO_SAIDA),
        ),
    )
    valor_movimentado = max(
        (totais_movimentados["saidas"] or Decimal("0.00"))
        - (totais_movimentados["estornos"] or Decimal("0.00")),
        Decimal("0.00"),
    )

    cards = [
        {
            "titulo": "Status",
            "valor": conta.get_status_display(),
            "icone": "bi bi-activity",
            "cor": (
                "success"
                if conta.status == ContaPagar.STATUS_PAGA
                else "danger"
                if conta.status == ContaPagar.STATUS_CANCELADA
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
            "titulo": "Total desembolsado",
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

    primeira_parcela_pendente = next(
        (
            parcela
            for parcela in parcelas_exibicao
            if parcela.status
            in [
                ParcelaPagar.STATUS_PENDENTE,
                ParcelaPagar.STATUS_PARCIAL,
            ]
        ),
        None,
    )

    return {
        "conta": conta,
        "cards": cards,
        "parcelas": parcelas_exibicao,
        "historicos": historicos_exibicao,
        "movimentacoes": movimentacoes[:20],
        "total_parcelas": total_parcelas,
        "parcelas_pagas": parcelas_pagas,
        "parcelas_pendentes": parcelas_pendentes,
        "valor_movimentado": valor_movimentado,
        "percentual_pago": percentual_pago,
        "primeira_parcela_pendente": primeira_parcela_pendente,
    }

def listar_contas_pagar(request):
    """
    Prepara a listagem operacional de Contas a Pagar.

    Aplica os filtros informados na requisição e calcula os
    indicadores financeiros referentes ao resultado encontrado.
    """

    hoje = timezone.localdate()

    busca = (request.GET.get("q") or "").strip()
    fornecedor_id = (request.GET.get("fornecedor") or "").strip()
    categoria_id = (request.GET.get("categoria") or "").strip()
    status = (request.GET.get("status") or "").strip()
    vencimento_inicio = (
        request.GET.get("vencimento_inicio") or ""
    ).strip()
    vencimento_fim = (
        request.GET.get("vencimento_fim") or ""
    ).strip()

    parcelas_queryset = (
        ParcelaPagar.objects
        .order_by(
            "data_vencimento",
            "numero",
        )
    )

    contas = (
        ContaPagar.objects
        .select_related(
            "fornecedor",
            "categoria",
        )
        .prefetch_related(
            Prefetch(
                "parcelas",
                queryset=parcelas_queryset,
                to_attr="parcelas_ordenadas",
            )
        )
        .order_by(
            "-criado_em",
        )
    )

    if busca:
        filtro_busca = (
            Q(descricao__icontains=busca)
            | Q(fornecedor__nome_fantasia__icontains=busca)
            | Q(fornecedor__razao_social__icontains=busca)
        )

        if busca.isdigit():
            filtro_busca |= Q(numero=int(busca))

        contas = contas.filter(filtro_busca)

    if fornecedor_id.isdigit():
        contas = contas.filter(
            fornecedor_id=int(fornecedor_id),
        )

    if categoria_id.isdigit():
        contas = contas.filter(
            categoria_id=int(categoria_id),
        )

    status_validos = {
        valor
        for valor, descricao in (
            ContaPagar._meta
            .get_field("status")
            .choices
        )
    }

    if status in status_validos:
        contas = contas.filter(
            status=status,
        )

    if vencimento_inicio:
        contas = contas.filter(
            parcelas__data_vencimento__gte=vencimento_inicio,
        )

    if vencimento_fim:
        contas = contas.filter(
            parcelas__data_vencimento__lte=vencimento_fim,
        )

    contas = contas.distinct()

    totais = contas.aggregate(
        valor_total=Sum("valor_total"),
        valor_pago=Sum("valor_pago"),
    )

    valor_total = (
        totais["valor_total"]
        or Decimal("0.00")
    )

    valor_pago = (
        totais["valor_pago"]
        or Decimal("0.00")
    )

    saldo_total = valor_total - valor_pago
    quantidade_contas = contas.count()

    contas_vencidas = (
        contas
        .filter(
            parcelas__data_vencimento__lt=hoje,
            parcelas__status__in=[
                ParcelaPagar.STATUS_PENDENTE,
                ParcelaPagar.STATUS_PARCIAL,
            ],
        )
        .distinct()
        .count()
    )

    contas_exibicao = list(contas)

    for conta in contas_exibicao:
        parcelas_abertas = [
            parcela
            for parcela in conta.parcelas_ordenadas
            if parcela.status in [
                ParcelaPagar.STATUS_PENDENTE,
                ParcelaPagar.STATUS_PARCIAL,
            ]
        ]

        conta.proximo_vencimento = (
            parcelas_abertas[0].data_vencimento
            if parcelas_abertas
            else None
        )


    modelo_fornecedor = (
        ContaPagar._meta
        .get_field("fornecedor")
        .remote_field
        .model
    )

    fornecedores = (
        modelo_fornecedor.objects
        .filter(
            contas_pagar__isnull=False,
        )
        .distinct()
        .order_by(
            "nome_fantasia",
            "razao_social",
        )
    )

    categorias = (
        CategoriaFinanceira.objects
        .filter(
            tipo=CategoriaFinanceira.TIPO_DESPESA,
            ativo=True,
        )
        .order_by("nome")
    )

    status_opcoes = (
        ContaPagar._meta
        .get_field("status")
        .choices
    )

    filtros_ativos = any(
        [
            busca,
            fornecedor_id,
            categoria_id,
            status,
            vencimento_inicio,
            vencimento_fim,
        ]
    )

    return {
        "contas": contas_exibicao,
        "fornecedores": fornecedores,
        "categorias": categorias,
        "status_opcoes": status_opcoes,
        "quantidade_contas": quantidade_contas,
        "contas_vencidas": contas_vencidas,
        "valor_total": valor_total,
        "valor_pago": valor_pago,
        "saldo_total": saldo_total,
        "filtros_ativos": filtros_ativos,
        "filtros": {
            "q": busca,
            "fornecedor": fornecedor_id,
            "categoria": categoria_id,
            "status": status,
            "vencimento_inicio": vencimento_inicio,
            "vencimento_fim": vencimento_fim,
        },
    }

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


@transaction.atomic
def criar_conta_pagar_manual(
    *,
    dados,
    usuario,
):
    """
    Cria uma Conta a Pagar manual e gera suas parcelas.

    O valor é dividido igualmente entre as parcelas.
    Eventual diferença de centavos é aplicada na última parcela.
    """
    quantidade_parcelas = dados.pop("quantidade_parcelas")
    primeiro_vencimento = dados.pop("primeiro_vencimento")

    valor_total = dados["valor_total"]

    conta = ContaPagar.objects.create(
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

        parcela = ParcelaPagar.objects.create(
            conta_pagar=conta,
            numero=numero,
            data_vencimento=vencimento,
            valor_original=valor_parcela,
            observacoes=(
                "Parcela gerada no cadastro manual "
                "da Conta a Pagar."
            ),
        )

        parcelas_criadas.append(parcela)

    HistoricoContaPagar.objects.create(
        conta_pagar=conta,
        tipo_evento=HistoricoContaPagar.EVENTO_CRIACAO,
        descricao="Conta a Pagar criada manualmente.",
        dados={
            "valor_total": str(conta.valor_total),
            "quantidade_parcelas": quantidade_parcelas,
            "primeiro_vencimento": primeiro_vencimento.isoformat(),
        },
        usuario=usuario,
    )

    for parcela in parcelas_criadas:
        HistoricoContaPagar.objects.create(
            conta_pagar=conta,
            tipo_evento=HistoricoContaPagar.EVENTO_PARCELA_CRIADA,
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
