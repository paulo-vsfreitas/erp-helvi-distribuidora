from decimal import Decimal

from compras.models import Compra
from django.urls import reverse


def moeda(valor):
    """
    Formata um valor decimal no padrão monetário brasileiro.
    """
    valor = valor or Decimal("0.00")

    return (
        f"R$ {valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def obter_resumo_compras(fornecedor):
    """
    Retorna os principais indicadores e as compras recentes
    vinculadas ao fornecedor.
    """
    compras = fornecedor.compras.order_by(
        "-data_compra",
        "-id",
    )

    quantidade = compras.count()

    valor_total = sum(
        compras.values_list("total", flat=True),
        Decimal("0.00"),
    )

    valor_pago = sum(
        compras.values_list("valor_pago", flat=True),
        Decimal("0.00"),
    )

    saldo_em_aberto = max(
        valor_total - valor_pago,
        Decimal("0.00"),
    )

    ticket_medio = (
        valor_total / quantidade
        if quantidade
        else Decimal("0.00")
    )

    ultima_compra = compras.first()

    return {
        "quantidade": quantidade,
        "valor_total": valor_total,
        "valor_pago": valor_pago,
        "saldo_em_aberto": saldo_em_aberto,
        "ticket_medio": ticket_medio,
        "ultima_compra": ultima_compra,
        "historico_compras": compras[:10],
    }


def montar_contexto_ficha_fornecedor(fornecedor):
    """
    Monta todo o contexto necessário para a ficha do fornecedor.
    """
    resumo = obter_resumo_compras(fornecedor)

    nome_exibicao = (
        fornecedor.nome_fantasia
        or fornecedor.razao_social
    )

    ficha_resumo = [
        {
            "label": "Código",
            "valor": fornecedor.codigo,
        },
        {
            "label": "Status",
            "valor": (
                "Ativo"
                if fornecedor.ativo
                else "Inativo"
            ),
        },
        {
            "label": "Compras",
            "valor": resumo["quantidade"],
        },
        {
            "label": "Última compra",
            "valor": (
                resumo["ultima_compra"].data_compra.strftime(
                    "%d/%m/%Y"
                )
                if resumo["ultima_compra"]
                else "—"
            ),
        },
    ]

    dados_cadastrais = [
        {
            "label": "Tipo de pessoa",
            "valor": fornecedor.get_tipo_pessoa_display(),
        },
        {
            "label": "Razão social / Nome",
            "valor": fornecedor.razao_social,
        },
        {
            "label": "Nome fantasia",
            "valor": (
                fornecedor.nome_fantasia
                or "Não informado"
            ),
        },
        {
            "label": "CPF / CNPJ",
            "valor": fornecedor.cpf_cnpj,
        },
        {
            "label": "Inscrição estadual",
            "valor": (
                fornecedor.inscricao_estadual
                or "Não informada"
            ),
        },
        {
            "label": "Inscrição municipal",
            "valor": (
                fornecedor.inscricao_municipal
                or "Não informada"
            ),
        },
    ]

    contatos = [
        {
            "label": "Contato principal",
            "valor": (
                fornecedor.contato_principal
                or "Não informado"
            ),
        },
        {
            "label": "Telefone",
            "valor": (
                fornecedor.telefone
                or "Não informado"
            ),
        },
        {
            "label": "WhatsApp",
            "valor": (
                fornecedor.whatsapp
                or "Não informado"
            ),
        },
        {
            "label": "E-mail",
            "valor": (
                fornecedor.email
                or "Não informado"
            ),
        },
        {
            "label": "Site",
            "valor": (
                fornecedor.site
                or "Não informado"
            ),
        },
    ]

    endereco = [
        {
            "label": "CEP",
            "valor": fornecedor.cep or "Não informado",
        },
        {
            "label": "Logradouro",
            "valor": (
                fornecedor.logradouro
                or "Não informado"
            ),
        },
        {
            "label": "Número",
            "valor": fornecedor.numero or "Não informado",
        },
        {
            "label": "Complemento",
            "valor": (
                fornecedor.complemento
                or "Não informado"
            ),
        },
        {
            "label": "Bairro",
            "valor": fornecedor.bairro or "Não informado",
        },
        {
            "label": "Cidade",
            "valor": fornecedor.cidade or "Não informada",
        },
        {
            "label": "Estado",
            "valor": fornecedor.estado or "Não informado",
        },
    ]

    condicoes_comerciais = [
        {
            "label": "Prazo médio de entrega",
            "valor": (
                f"{fornecedor.prazo_medio_entrega} dias"
                if fornecedor.prazo_medio_entrega is not None
                else "Não informado"
            ),
        },
        {
            "label": "Condição de pagamento padrão",
            "valor": (
                fornecedor.condicao_pagamento_padrao
                or "Não informada"
            ),
        },
        {
            "label": "Cadastrado em",
            "valor": fornecedor.criado_em.strftime(
                "%d/%m/%Y às %H:%M"
            ),
        },
        {
            "label": "Última atualização",
            "valor": fornecedor.atualizado_em.strftime(
                "%d/%m/%Y às %H:%M"
            ),
        },
    ]

    resumo_compras = [
        {
            "label": "Total comprado",
            "valor": moeda(resumo["valor_total"]),
        },
        {
            "label": "Valor pago",
            "valor": moeda(resumo["valor_pago"]),
        },
        {
            "label": "Saldo em aberto",
            "valor": moeda(resumo["saldo_em_aberto"]),
        },
        {
            "label": "Ticket médio",
            "valor": moeda(resumo["ticket_medio"]),
        },
    ]

    ficha_acoes = [
    {
        "texto": "Voltar à lista",
        "icone": "bi-arrow-left",
        "url": reverse(
            "fornecedores:lista"
        ),
        "classe": "btn-secondary",
    },
    {
        "texto": "Editar",
        "icone": "bi-pencil",
        "url": reverse(
            "fornecedores:editar",
            kwargs={
                "pk": fornecedor.pk,
            },
        ),
        "classe": "btn-secondary",
    },
    {
        "texto": "Nova compra",
        "icone": "bi-cart-plus",
        "url": (
            f"{reverse('compras:nova')}"
            f"?fornecedor={fornecedor.pk}"
        ),
        "classe": "btn-primary",
    },

    ]

    return {
        "fornecedor": fornecedor,
        "ficha_titulo": nome_exibicao,
        "ficha_subtitulo": (
            f"{fornecedor.codigo} • "
            f"{fornecedor.get_tipo_pessoa_display()}"
        ),
        "ficha_resumo": ficha_resumo,
        "ficha_acoes": ficha_acoes,
        "dados_cadastrais": dados_cadastrais,
        "contatos": contatos,
        "endereco": endereco,
        "condicoes_comerciais": condicoes_comerciais,
        "resumo_compras": resumo_compras,
        "historico_compras": resumo["historico_compras"],
        "nova_compra_url": (
            f"{reverse('compras:nova')}"
            f"?fornecedor={fornecedor.pk}"
        ),
    }