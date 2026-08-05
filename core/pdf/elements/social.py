from pathlib import Path

from django.conf import settings
from reportlab.graphics.shapes import Circle, Drawing, Rect, String
from reportlab.lib import colors
from reportlab.platypus import Image, Paragraph, Table, TableStyle

from core.pdf.styles import TEXT


def _whatsapp_icon():
    arquivo = Path(settings.BASE_DIR) / "static" / "img" / "icons" / "whatsapp.png"
    return Image(str(arquivo), width=14, height=14)


def _instagram_icon():
    desenho = Drawing(12, 12)
    desenho.add(Rect(1, 1, 10, 10, 2.5, fillColor=None, strokeColor=colors.HexColor("#C13584"), strokeWidth=1.5))
    desenho.add(Circle(6, 6, 2.4, fillColor=None, strokeColor=colors.HexColor("#C13584"), strokeWidth=1.3))
    desenho.add(Circle(8.8, 8.8, 0.8, fillColor=colors.HexColor("#F56040"), strokeColor=None))
    return desenho


def _facebook_icon():
    desenho = Drawing(12, 12)
    desenho.add(Circle(6, 6, 5.5, fillColor=colors.HexColor("#1877F2"), strokeColor=None))
    desenho.add(String(4.4, 2.0, "f", fontName="Helvetica-Bold", fontSize=9, fillColor=colors.white))
    return desenho


def build_social_channels(empresa):
    canais = []
    if empresa.exibir_whatsapp_pdf and empresa.whatsapp:
        canais.append((_whatsapp_icon(), empresa.whatsapp))
    if empresa.exibir_instagram_pdf and empresa.instagram:
        usuario = empresa.instagram.strip()
        if not usuario.startswith("@"):
            usuario = f"@{usuario}"
        canais.append((_instagram_icon(), usuario))
    if empresa.exibir_facebook_pdf and empresa.facebook:
        canais.append((_facebook_icon(), empresa.facebook))

    if not canais:
        return None

    celulas = []
    larguras = []
    for icone, texto in canais:
        celulas.extend([icone, Paragraph(texto, TEXT)])
        larguras.extend([17, 100])

    tabela = Table([celulas], colWidths=larguras, hAlign="LEFT")
    tabela.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))
    return tabela
