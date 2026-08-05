from django.utils import timezone

from configuracoes.services.empresa_service import obter_empresa
from core.pdf import colors


def draw_footer(canvas, doc):
    """
    Desenha o rodapé institucional em todas as páginas do PDF.
    """
    canvas.saveState()

    empresa = obter_empresa()
    largura_pagina, _ = doc.pagesize

    margem_esquerda = doc.leftMargin
    margem_direita = largura_pagina - doc.rightMargin

    canvas.setStrokeColor(colors.HELVI_GOLD)
    canvas.setLineWidth(0.8)
    canvas.line(
        margem_esquerda,
        42,
        margem_direita,
        42,
    )

    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.GRAY_700)

    nome_empresa = (
        empresa.nome_fantasia
        or empresa.razao_social
        or "Helvi Distribuidora"
    )

    canvas.drawString(
        margem_esquerda,
        29,
        f"Documento emitido automaticamente pelo ERP Helvi | {nome_empresa}",
    )

    emitido_em = timezone.localtime().strftime(
        "%d/%m/%Y às %H:%M"
    )

    canvas.drawCentredString(
        largura_pagina / 2,
        9,
        emitido_em,
    )

    canvas.drawRightString(
        margem_direita,
        29,
        f"Página {canvas.getPageNumber()}",
    )

    if empresa.exibir_site_pdf and empresa.site:
        canvas.drawCentredString(
            largura_pagina / 2,
            19,
            empresa.site,
        )

    canvas.restoreState()
