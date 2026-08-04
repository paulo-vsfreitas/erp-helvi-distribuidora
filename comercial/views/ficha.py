from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404, render

from comercial.forms import CompartilhamentoOrcamentoForm
from comercial.models import Orcamento
from comercial.services.compartilhamento_service import (
    gerar_assunto_email,
    gerar_mensagem_email,
    gerar_mensagem_whatsapp,
)


def montar_timeline_orcamento(orcamento):
    eventos = []

    vendedor_nome = (
        orcamento.vendedor.get_full_name()
        or orcamento.vendedor.username
    )

    eventos.append(
        {
            "tipo": "criado",
            "titulo": "Orçamento criado",
            "descricao": (
                f"Orçamento criado por {vendedor_nome}."
            ),
            "data": orcamento.criado_em,
            "icone": "bi-file-earmark-plus",
            "classe": "timeline-evento-primary",
        }
    )

    for compartilhamento in orcamento.compartilhamentos.select_related(
        "realizado_por"
    ).all():
        responsavel = (
            compartilhamento.realizado_por.get_full_name()
            or compartilhamento.realizado_por.username
        )

        if compartilhamento.canal == "whatsapp":
            if compartilhamento.resultado == "falha":
                titulo = "Falha ao preparar WhatsApp"
                icone = "bi-exclamation-triangle"
                classe = "timeline-evento-danger"
            else:
                titulo = "WhatsApp preparado"
                icone = "bi-whatsapp"
                classe = "timeline-evento-success"

            descricao = (
                f"Mensagem preparada para "
                f"{compartilhamento.destinatario} por {responsavel}."
            )

        else:
            if compartilhamento.resultado == "falha":
                titulo = "Falha no envio do e-mail"
                icone = "bi-envelope-x"
                classe = "timeline-evento-danger"
            else:
                titulo = "E-mail enviado"
                icone = "bi-envelope-check"
                classe = "timeline-evento-info"

            descricao = (
                f"E-mail para {compartilhamento.destinatario} "
                f"por {responsavel}."
            )

        if compartilhamento.detalhe:
            descricao = (
                f"{descricao} {compartilhamento.detalhe}"
            )

        eventos.append(
            {
                "tipo": "compartilhamento",
                "titulo": titulo,
                "descricao": descricao,
                "data": compartilhamento.realizado_em,
                "icone": icone,
                "classe": classe,
            }
        )

    if orcamento.enviado_em:
        eventos.append(
            {
                "tipo": "status",
                "titulo": "Orçamento marcado como enviado",
                "descricao": (
                    "O orçamento passou para o status Enviado."
                ),
                "data": orcamento.enviado_em,
                "icone": "bi-send-check",
                "classe": "timeline-evento-info",
            }
        )

    if orcamento.aprovado_em:
        eventos.append(
            {
                "tipo": "status",
                "titulo": "Orçamento aprovado",
                "descricao": (
                    "A proposta comercial foi aprovada."
                ),
                "data": orcamento.aprovado_em,
                "icone": "bi-check-circle",
                "classe": "timeline-evento-success",
            }
        )

    if orcamento.rejeitado_em:
        eventos.append(
            {
                "tipo": "status",
                "titulo": "Orçamento rejeitado",
                "descricao": (
                    "A proposta comercial foi rejeitada."
                ),
                "data": orcamento.rejeitado_em,
                "icone": "bi-x-circle",
                "classe": "timeline-evento-danger",
            }
        )

    if orcamento.cancelado_em:
        eventos.append(
            {
                "tipo": "status",
                "titulo": "Orçamento cancelado",
                "descricao": (
                    "O orçamento foi cancelado."
                ),
                "data": orcamento.cancelado_em,
                "icone": "bi-slash-circle",
                "classe": "timeline-evento-dark",
            }
        )

    if orcamento.convertido_em:
        descricao = "O orçamento foi convertido em venda."

        if orcamento.venda_gerada:
            descricao = (
                f"Venda nº {orcamento.venda_gerada.numero} "
                f"gerada a partir deste orçamento."
            )

        eventos.append(
            {
                "tipo": "conversao",
                "titulo": "Convertido em venda",
                "descricao": descricao,
                "data": orcamento.convertido_em,
                "icone": "bi-cart-check",
                "classe": "timeline-evento-success",
                "venda": orcamento.venda_gerada,
            }
        )

    return sorted(
        eventos,
        key=lambda evento: evento["data"],
        reverse=True,
    )


@login_required
def ficha_orcamento(request, numero):
    orcamento = get_object_or_404(
        Orcamento.objects
        .select_related(
            "cliente",
            "vendedor",
            "venda_gerada",
        )
        .prefetch_related(
            "itens__produto",
            "itens__produto__marca",
            "compartilhamentos__realizado_por",
        ),
        numero=numero,
    )

    resumo_itens = orcamento.itens.aggregate(
        quantidade_pecas=Sum("quantidade"),
        desconto_itens=Sum("desconto"),
    )

    quantidade_pecas = (
        resumo_itens["quantidade_pecas"]
        or 0
    )

    desconto_itens = (
        resumo_itens["desconto_itens"]
        or 0
    )

    subtotal_liquido = (
        orcamento.subtotal
        - desconto_itens
    )

    mensagem_whatsapp = gerar_mensagem_whatsapp(
        orcamento
    )

    mensagem_email = gerar_mensagem_email(
        orcamento
    )

    assunto_email = gerar_assunto_email(
        orcamento
    )

    form_compartilhamento = CompartilhamentoOrcamentoForm(
        initial={
            "canal": "whatsapp",
            "telefone": orcamento.cliente_telefone,
            "email": orcamento.cliente_email,
            "assunto": assunto_email,
            "mensagem": mensagem_whatsapp,
            "marcar_enviado": True,
        }
    )

    contexto = {
        "orcamento": orcamento,
        "quantidade_itens": orcamento.itens.count(),
        "quantidade_pecas": quantidade_pecas,
        "desconto_itens": desconto_itens,
        "subtotal_liquido": subtotal_liquido,
        "form_compartilhamento": form_compartilhamento,
        "compartilhamentos": (
            orcamento.compartilhamentos
            .select_related("realizado_por")
            .all()[:10]
        ),
        "mensagem_whatsapp": mensagem_whatsapp,
        "mensagem_email": mensagem_email,
        "assunto_email": assunto_email,
        "timeline_eventos": montar_timeline_orcamento(
            orcamento
        ),
    }

    return render(
        request,
        "comercial/ficha_orcamento.html",
        contexto,
    )