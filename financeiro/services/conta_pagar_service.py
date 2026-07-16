from decimal import Decimal

from django.db import transaction
from django.db.models import Prefetch, Sum
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
def criar_conta_pagar_compra(compra, usuario):
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

    valor_pago_importado = min(
        compra.valor_pago or Decimal("0.00"),
        compra.total,
    )

    conta = ContaPagar.objects.create(
        descricao=f"Compra #{compra.numero} — {compra.fornecedor_nome}",
        fornecedor=compra.fornecedor,
        compra=compra,
        categoria=categoria,
        data_emissao=compra.data_compra,
        data_competencia=compra.data_compra,
        valor_total=compra.total,
        valor_pago=valor_pago_importado,
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
        valor_pago=valor_pago_importado,
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
            "valor_pago_importado": str(valor_pago_importado),
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
            "titulo": "Valor pago",
            "valor": formatar_moeda(conta.valor_pago),
            "icone": "bi bi-check-circle",
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
        "parcelas_pagas": parcelas_pagas,
        "parcelas_pendentes": parcelas_pendentes,
        "valor_movimentado": valor_movimentado,
        "percentual_pago": percentual_pago,
        
    }