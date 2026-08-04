from dataclasses import dataclass

from django.db import transaction
from django.utils import timezone
from django.utils.formats import date_format

from comercial.models import (
    CompartilhamentoOrcamento,
    Orcamento,
)
from core.communication import (
    enviar_email_com_anexo,
    gerar_url_whatsapp,
)
from configuracoes.models import Empresa
from configuracoes.services import renderizar_modelo_mensagem
from core.formatters import formatar_moeda_br
from core.pdf.documents.orcamento import OrcamentoPDF


def obter_configuracao_empresa():
    return Empresa.objects.only(
        "nome_fantasia",
        "razao_social",
        "assunto_padrao_email",
        "mensagem_padrao_email",
        "mensagem_padrao_whatsapp",
    ).first()


def nome_empresa(empresa=None):
    empresa = empresa or obter_configuracao_empresa()

    if empresa:
        return empresa.nome_fantasia or empresa.razao_social

    return "Helvi Distribuidora"


@dataclass(frozen=True)
class ResultadoCompartilhamento:
    sucesso: bool
    canal: str
    url: str = ""
    mensagem: str = ""


def formatar_moeda(valor):
    return formatar_moeda_br(valor)


def contexto_modelo_mensagem(orcamento, empresa=None):
    empresa = empresa or obter_configuracao_empresa()
    vendedor = (
        orcamento.vendedor.get_full_name()
        or orcamento.vendedor.username
    )

    return {
        "CLIENTE": orcamento.cliente_nome or "Cliente",
        "ORCAMENTO": orcamento.codigo,
        "TOTAL": formatar_moeda(orcamento.total),
        "VALIDADE": date_format(
            orcamento.data_validade,
            format="d/m/Y",
            use_l10n=False,
        ),
        "VENDEDOR": vendedor,
        "EMPRESA": nome_empresa(empresa),
    }


def renderizar_modelo_configurado(modelo, orcamento, empresa):
    return renderizar_modelo_mensagem(
        modelo,
        contexto_modelo_mensagem(orcamento, empresa),
    )

# ==========================================================
# MENSAGENS PADRÃO
#
# Futuramente estas mensagens serão carregadas do módulo:
#
# Configurações → Mensagens
#
# Variáveis suportadas:
#
# {CLIENTE}
# {ORCAMENTO}
# {TOTAL}
# {VALIDADE}
# {VENDEDOR}
# {EMPRESA}
#
# ==========================================================
def gerar_mensagem_whatsapp(orcamento):
    configuracao = obter_configuracao_empresa()
    if configuracao and configuracao.mensagem_padrao_whatsapp.strip():
        return renderizar_modelo_configurado(
            configuracao.mensagem_padrao_whatsapp,
            orcamento,
            configuracao,
        )

    cliente = orcamento.cliente_nome or "Cliente"
    empresa = nome_empresa(configuracao)

    vendedor = (
        orcamento.vendedor.get_full_name()
        or orcamento.vendedor.username
    )

    emissao = date_format(
        orcamento.data_emissao,
        format="d/m/Y",
        use_l10n=False,
    )

    validade = date_format(
        orcamento.data_validade,
        format="d/m/Y",
        use_l10n=False,
    )

    return f"""Olá, {cliente}! 👋

Segue o orçamento {orcamento.codigo} da {empresa}.

📅 Emissão: {emissao}
📅 Validade: {validade}

📦 Itens: {orcamento.quantidade_itens}
👓 Peças: {orcamento.quantidade_pecas}

💰 Valor total: {formatar_moeda(orcamento.total)}

Segue também o PDF do orçamento.

Qualquer dúvida estou à disposição.

Atenciosamente,

{vendedor}
{empresa}
"""

def gerar_mensagem_email(orcamento):
    configuracao = obter_configuracao_empresa()
    if configuracao and configuracao.mensagem_padrao_email.strip():
        return renderizar_modelo_configurado(
            configuracao.mensagem_padrao_email,
            orcamento,
            configuracao,
        )

    cliente = orcamento.cliente_nome or "Cliente"
    empresa = nome_empresa(configuracao)

    vendedor = (
        orcamento.vendedor.get_full_name()
        or orcamento.vendedor.username
    )

    emissao = date_format(
        orcamento.data_emissao,
        format="d/m/Y",
        use_l10n=False,
    )

    validade = date_format(
        orcamento.data_validade,
        format="d/m/Y",
        use_l10n=False,
    )

    return f"""Olá, {cliente}!

    Segue em anexo o orçamento {orcamento.codigo} da {empresa}.

    Data de emissão: {emissao}
    Validade: {validade}
    Quantidade de peças: {orcamento.quantidade_pecas}
    Valor total: {formatar_moeda(orcamento.total)}

    Qualquer dúvida, estamos à disposição.

    Atenciosamente,

    {vendedor}
    {empresa}
    """


def gerar_assunto_email(orcamento):
    configuracao = obter_configuracao_empresa()
    if configuracao and configuracao.assunto_padrao_email.strip():
        return renderizar_modelo_configurado(
            configuracao.assunto_padrao_email,
            orcamento,
            configuracao,
        )

    return f"{nome_empresa(configuracao)} • Orçamento {orcamento.codigo}"


def gerar_pdf_orcamento_bytes(orcamento):
    return OrcamentoPDF(orcamento).build()


def registrar_historico(
    *,
    orcamento,
    canal,
    destinatario,
    assunto,
    mensagem,
    resultado,
    usuario,
    detalhe="",
):
    return CompartilhamentoOrcamento.objects.create(
        orcamento=orcamento,
        canal=canal,
        destinatario=destinatario,
        assunto=assunto,
        mensagem=mensagem,
        resultado=resultado,
        realizado_por=usuario,
        detalhe=detalhe,
    )


def marcar_orcamento_como_enviado(orcamento):
    if orcamento.status == Orcamento.Status.RASCUNHO:
        orcamento.status = Orcamento.Status.ENVIADO
        orcamento.enviado_em = timezone.now()
        orcamento.save(
            update_fields=[
                "status",
                "enviado_em",
                "atualizado_em",
            ]
        )


def compartilhar_por_whatsapp(
    *,
    orcamento,
    telefone,
    mensagem,
    usuario,
    marcar_enviado=False,
):
    try:
        url = gerar_url_whatsapp(
            telefone=telefone,
            mensagem=mensagem,
        )

        with transaction.atomic():
            registrar_historico(
                orcamento=orcamento,
                canal=CompartilhamentoOrcamento.Canal.WHATSAPP,
                destinatario=telefone,
                assunto="",
                mensagem=mensagem,
                resultado=CompartilhamentoOrcamento.Resultado.PREPARADO,
                usuario=usuario,
                detalhe=(
                    "Link do WhatsApp preparado. "
                    "O envio final depende da confirmação do usuário."
                ),
            )

        return ResultadoCompartilhamento(
            sucesso=True,
            canal=CompartilhamentoOrcamento.Canal.WHATSAPP,
            url=url,
            mensagem="WhatsApp preparado com sucesso.",
        )

    except Exception as erro:
        registrar_historico(
            orcamento=orcamento,
            canal=CompartilhamentoOrcamento.Canal.WHATSAPP,
            destinatario=telefone,
            assunto="",
            mensagem=mensagem,
            resultado=CompartilhamentoOrcamento.Resultado.FALHA,
            usuario=usuario,
            detalhe=str(erro),
        )

        raise


def compartilhar_por_email(
    *,
    orcamento,
    email,
    assunto,
    mensagem,
    usuario,
    marcar_enviado=False,
):
    try:
        pdf = gerar_pdf_orcamento_bytes(orcamento)

        enviar_email_com_anexo(
            destinatario=email,
            assunto=assunto,
            mensagem=mensagem,
            nome_arquivo=f"{orcamento.codigo.lower()}.pdf",
            arquivo=pdf,
        )

        with transaction.atomic():
            registrar_historico(
                orcamento=orcamento,
                canal=CompartilhamentoOrcamento.Canal.EMAIL,
                destinatario=email,
                assunto=assunto,
                mensagem=mensagem,
                resultado=CompartilhamentoOrcamento.Resultado.ENVIADO,
                usuario=usuario,
                detalhe="E-mail enviado com PDF anexado.",
            )

            if marcar_enviado:
                marcar_orcamento_como_enviado(orcamento)

        return ResultadoCompartilhamento(
            sucesso=True,
            canal=CompartilhamentoOrcamento.Canal.EMAIL,
            mensagem="E-mail enviado com sucesso.",
        )

    except Exception as erro:
        registrar_historico(
            orcamento=orcamento,
            canal=CompartilhamentoOrcamento.Canal.EMAIL,
            destinatario=email,
            assunto=assunto,
            mensagem=mensagem,
            resultado=CompartilhamentoOrcamento.Resultado.FALHA,
            usuario=usuario,
            detalhe=str(erro),
        )

        raise


def compartilhar_orcamento(
    *,
    orcamento,
    dados,
    usuario,
):
    canal = dados["canal"]

    if canal == CompartilhamentoOrcamento.Canal.WHATSAPP:
        return compartilhar_por_whatsapp(
            orcamento=orcamento,
            telefone=dados["telefone"],
            mensagem=dados["mensagem"],
            usuario=usuario,
            marcar_enviado=dados.get("marcar_enviado", False),
        )

    if canal == CompartilhamentoOrcamento.Canal.EMAIL:
        return compartilhar_por_email(
            orcamento=orcamento,
            email=dados["email"],
            assunto=dados["assunto"],
            mensagem=dados["mensagem"],
            usuario=usuario,
            marcar_enviado=dados.get("marcar_enviado", False),
        )

    raise ValueError("O canal de compartilhamento informado é inválido.")
