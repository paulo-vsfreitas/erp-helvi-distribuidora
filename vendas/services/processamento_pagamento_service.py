from decimal import Decimal

from django.core.exceptions import ValidationError
from django.utils import timezone

from financeiro.models import (
    CategoriaFinanceira,
    ContaReceber,
    HistoricoContaReceber,
    ParcelaReceber,
)
from financeiro.services.conta_receber_service import (
    adicionar_meses,
    criar_conta_receber_manual,
    registrar_historico_conta_receber,
)
from financeiro.services.recebimento_service import (
    registrar_recebimento,
)
from vendas.models import Venda


FORMAS_RECEBIMENTO_IMEDIATO = {
    Venda.FORMA_PIX,
    Venda.FORMA_DINHEIRO,
    Venda.FORMA_CARTAO_DEBITO,
    Venda.FORMA_CARTAO_CREDITO,
    Venda.FORMA_TRANSFERENCIA,
}


def obter_documento_cliente(cliente):
    if not cliente:
        return ""

    for campo in (
        "cpf_cnpj",
        "documento",
        "cnpj",
        "cpf",
    ):
        valor = getattr(cliente, campo, None)

        if valor:
            return str(valor)

    return ""


def obter_nome_cliente(cliente):
    if not cliente:
        return "Consumidor Final"

    for campo in (
        "nome_fantasia",
        "razao_social",
        "nome",
    ):
        valor = getattr(cliente, campo, None)

        if valor:
            return str(valor)

    return str(cliente)


def obter_categoria_receita_vendas():
    categoria, _ = CategoriaFinanceira.objects.get_or_create(
        nome="Receita de Vendas",
        tipo=CategoriaFinanceira.TIPO_RECEITA,
    )

    return categoria


def criar_conta_venda_com_entrada(
    *,
    venda,
    usuario,
    valor_entrada,
    quantidade_parcelas,
    primeiro_vencimento,
    categoria,
):
    """
    Cria uma Conta a Receber com:

    - uma parcela imediata referente à entrada;
    - parcelas futuras referentes ao saldo restante.
    """
    hoje = timezone.localdate()
    saldo_parcelar = venda.total - valor_entrada

    if valor_entrada <= 0:
        raise ValidationError(
            "O valor da entrada deve ser maior que zero."
        )

    if valor_entrada >= venda.total:
        raise ValidationError(
            "Em uma venda parcelada, a entrada deve ser menor "
            "que o valor total da venda."
        )

    if quantidade_parcelas <= 0:
        raise ValidationError(
            "A quantidade de parcelas deve ser maior que zero."
        )

    conta = ContaReceber.objects.create(
        descricao=f"Venda nº {venda.numero}",
        cliente=venda.cliente,
        nome_devedor=obter_nome_cliente(venda.cliente),
        documento_devedor=obter_documento_cliente(
            venda.cliente
        ),
        categoria=categoria,
        origem=ContaReceber.ORIGEM_VENDA,
        origem_id=venda.pk,
        origem_descricao=f"Venda nº {venda.numero}",
        data_emissao=hoje,
        data_competencia=hoje,
        valor_total=venda.total,
        observacoes=(
            "Conta gerada automaticamente pela "
            f"finalização da venda nº {venda.numero}."
        ),
        criado_por=usuario,
    )

    parcela_entrada = ParcelaReceber.objects.create(
        conta_receber=conta,
        numero=1,
        data_vencimento=hoje,
        valor_original=valor_entrada,
        observacoes=(
            f"Entrada da venda nº {venda.numero}."
        ),
    )

    registrar_historico_conta_receber(
        conta=conta,
        tipo_evento=(
            HistoricoContaReceber.EVENTO_PARCELA_CRIADA
        ),
        descricao="Parcela de entrada criada.",
        dados={
            "parcela_id": parcela_entrada.pk,
            "numero": parcela_entrada.numero,
            "vencimento": hoje.isoformat(),
            "valor": str(valor_entrada),
            "tipo": "entrada",
        },
        usuario=usuario,
    )

    valor_base = (
        saldo_parcelar / quantidade_parcelas
    ).quantize(Decimal("0.01"))

    valor_distribuido = Decimal("0.00")

    for indice in range(quantidade_parcelas):
        numero = indice + 2

        if indice == quantidade_parcelas - 1:
            valor_parcela = (
                saldo_parcelar - valor_distribuido
            )
        else:
            valor_parcela = valor_base
            valor_distribuido += valor_parcela

        vencimento = adicionar_meses(
            primeiro_vencimento,
            indice,
        )

        parcela = ParcelaReceber.objects.create(
            conta_receber=conta,
            numero=numero,
            data_vencimento=vencimento,
            valor_original=valor_parcela,
            observacoes=(
                f"Parcela da venda nº {venda.numero}."
            ),
        )

        registrar_historico_conta_receber(
            conta=conta,
            tipo_evento=(
                HistoricoContaReceber.EVENTO_PARCELA_CRIADA
            ),
            descricao=(
                f"Parcela {parcela.numero} criada com vencimento "
                f"em {vencimento.strftime('%d/%m/%Y')}."
            ),
            dados={
                "parcela_id": parcela.pk,
                "numero": parcela.numero,
                "vencimento": vencimento.isoformat(),
                "valor": str(valor_parcela),
                "tipo": "parcela",
            },
            usuario=usuario,
        )

    registrar_historico_conta_receber(
        conta=conta,
        tipo_evento=HistoricoContaReceber.EVENTO_CRIACAO,
        descricao=(
            "Conta a Receber criada automaticamente "
            "pela finalização da venda."
        ),
        dados={
            "venda_id": venda.pk,
            "valor_total": str(venda.total),
            "valor_entrada": str(valor_entrada),
            "saldo_parcelado": str(saldo_parcelar),
            "quantidade_parcelas": quantidade_parcelas,
        },
        usuario=usuario,
    )

    return conta


def gerar_conta_receber_venda(
    *,
    venda,
    usuario,
    quantidade_parcelas=1,
    primeiro_vencimento=None,
    valor_entrada=Decimal("0.00"),
):
    """
    Gera a Conta a Receber vinculada à venda.

    A função é idempotente: se a conta já existir,
    ela será reutilizada.
    """
    conta_existente = (
        ContaReceber.objects
        .filter(
            origem=ContaReceber.ORIGEM_VENDA,
            origem_id=venda.pk,
        )
        .first()
    )

    if conta_existente:
        venda.financeiro_gerado = True
        return conta_existente

    hoje = timezone.localdate()
    primeiro_vencimento = primeiro_vencimento or hoje
    categoria_vendas = obter_categoria_receita_vendas()

    if valor_entrada > 0:
        conta = criar_conta_venda_com_entrada(
            venda=venda,
            usuario=usuario,
            valor_entrada=valor_entrada,
            quantidade_parcelas=quantidade_parcelas,
            primeiro_vencimento=primeiro_vencimento,
            categoria=categoria_vendas,
        )
    else:
        conta = criar_conta_receber_manual(
            dados={
                "descricao": f"Venda nº {venda.numero}",
                "cliente": venda.cliente,
                "nome_devedor": obter_nome_cliente(
                    venda.cliente
                ),
                "documento_devedor": obter_documento_cliente(
                    venda.cliente
                ),
                "categoria": categoria_vendas,
                "origem": ContaReceber.ORIGEM_VENDA,
                "origem_id": venda.pk,
                "origem_descricao": (
                    f"Venda nº {venda.numero}"
                ),
                "data_emissao": hoje,
                "data_competencia": hoje,
                "valor_total": venda.total,
                "observacoes": (
                    "Conta gerada automaticamente pela "
                    f"finalização da venda nº {venda.numero}."
                ),
                "quantidade_parcelas": quantidade_parcelas,
                "primeiro_vencimento": primeiro_vencimento,
            },
            usuario=usuario,
        )

    registrar_historico_conta_receber(
        conta=conta,
        tipo_evento=(
            HistoricoContaReceber.EVENTO_INTEGRACAO_VENDA
        ),
        descricao=(
            "Conta integrada automaticamente com "
            f"a venda nº {venda.numero}."
        ),
        dados={
            "venda_id": venda.pk,
            "venda_numero": venda.numero,
            "valor_total": str(venda.total),
            "valor_entrada": str(valor_entrada),
            "quantidade_parcelas": quantidade_parcelas,
        },
        usuario=usuario,
    )

    venda.financeiro_gerado = True

    return conta


def processar_pagamento_venda(
    *,
    venda,
    usuario,
    conta_financeira=None,
):
    """
    Orquestra o processamento financeiro da venda.

    Responsabilidades:

    - gerar a Conta a Receber;
    - gerar parcelas;
    - registrar recebimento imediato;
    - registrar recebimento da entrada;
    - atualizar os dados financeiros da venda.

    Não realiza baixa de estoque.
    Não finaliza o status operacional da venda.
    """
    quantidade_parcelas = venda.quantidade_parcelas or 1

    primeiro_vencimento = (
        venda.primeiro_vencimento
        or timezone.localdate()
    )

    valor_entrada = (
        venda.valor_entrada
        or Decimal("0.00")
    )

    pagamento_imediato = (
        venda.forma_pagamento
        in FORMAS_RECEBIMENTO_IMEDIATO
        and valor_entrada <= 0
    )

    if pagamento_imediato:
        quantidade_parcelas = 1
        primeiro_vencimento = timezone.localdate()

    conta = gerar_conta_receber_venda(
        venda=venda,
        usuario=usuario,
        quantidade_parcelas=quantidade_parcelas,
        primeiro_vencimento=primeiro_vencimento,
        valor_entrada=valor_entrada,
    )

    possui_entrada = valor_entrada > 0

    if not pagamento_imediato and not possui_entrada:
        venda.valor_recebido = Decimal("0.00")
        venda.valor_troco = Decimal("0.00")
        venda.status_pagamento = Venda.PAGAMENTO_PENDENTE

        venda.save(
            update_fields=[
                "valor_recebido",
                "valor_troco",
                "status_pagamento",
            ]
        )

        return conta

    if conta_financeira is None:
        raise ValidationError(
            "Selecione uma conta financeira para registrar "
            "o recebimento."
        )

    parcela = (
        conta.parcelas
        .order_by("numero")
        .first()
    )

    if parcela is None:
        raise ValidationError(
            "A Conta a Receber foi criada sem parcelas."
        )

    if pagamento_imediato:
        valor_receber = venda.total
    else:
        valor_receber = valor_entrada

    registrar_recebimento(
        parcela=parcela,
        conta_financeira=conta_financeira,
        data_recebimento=timezone.localdate(),
        valor=valor_receber,
        forma_recebimento=venda.forma_pagamento,
        observacao=(
            "Recebimento automático referente à "
            f"venda nº {venda.numero}."
        ),
        usuario=usuario,
    )

    venda.valor_recebido = valor_receber
    venda.valor_troco = Decimal("0.00")

    if valor_receber >= venda.total:
        venda.status_pagamento = Venda.PAGAMENTO_PAGO

    elif valor_receber > 0:
        venda.status_pagamento = Venda.PAGAMENTO_PARCIAL

    else:
        venda.status_pagamento = Venda.PAGAMENTO_PENDENTE

    venda.save(
        update_fields=[
            "valor_recebido",
            "valor_troco",
            "status_pagamento",
        ]
    )

    return conta
