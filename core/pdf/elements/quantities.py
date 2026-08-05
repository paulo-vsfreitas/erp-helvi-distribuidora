from reportlab.lib.units import mm
from reportlab.platypus import KeepTogether, Paragraph, Spacer, Table, TableStyle

from core.pdf import colors as helvi_colors
from core.pdf.styles import LABEL, SUBTITLE


def resumo_quantidades(*, produtos, itens, pecas):
    """Cria o resumo quantitativo compartilhado por documentos comerciais."""
    dados = [[
        Paragraph("PRODUTOS", LABEL),
        Paragraph("ITENS / VARIAÇÕES", LABEL),
        Paragraph("PEÇAS", LABEL),
    ], [
        Paragraph(f"<b>{produtos}</b>", SUBTITLE),
        Paragraph(f"<b>{itens}</b>", SUBTITLE),
        Paragraph(f"<b>{pecas}</b>", SUBTITLE),
    ]]
    tabela = Table(dados, colWidths=[58 * mm] * 3, hAlign="LEFT")
    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), helvi_colors.GRAY_100),
        ("BOX", (0, 0), (-1, -1), 0.5, helvi_colors.GRAY_300),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, helvi_colors.GRAY_300),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, 0), 6),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 3),
        ("TOPPADDING", (0, 1), (-1, 1), 3),
        ("BOTTOMPADDING", (0, 1), (-1, 1), 7),
        ("TEXTCOLOR", (0, 1), (-1, 1), helvi_colors.HELVI_GOLD),
    ]))
    return KeepTogether([
        Paragraph("RESUMO DE QUANTIDADES", SUBTITLE),
        Spacer(1, 1 * mm),
        tabela,
        Spacer(1, 6 * mm),
    ])
