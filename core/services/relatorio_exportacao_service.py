import csv
from io import BytesIO, StringIO

from django.http import HttpResponse
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from configuracoes.models import Empresa


PDF_OFICIAL = {
    "vendas", "contas-receber", "contas-pagar", "fluxo-caixa",
    "posicao-estoque", "compras",
    "use-helvi-financeiro",
}


def exportar_csv(relatorio, slug):
    buffer = StringIO()
    writer = csv.writer(buffer, delimiter=";")
    writer.writerow(relatorio["colunas"])
    for linha in relatorio["linhas"]:
        writer.writerow(linha["valores"])
    response = HttpResponse("\ufeff" + buffer.getvalue(), content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="relatorio-{slug}.csv"'
    return response


def _texto(valor, estilo):
    return Paragraph(str(valor or "—").replace("&", "&amp;").replace("<", "&lt;"), estilo)


def exportar_pdf(relatorio, slug, periodo):
    if slug not in PDF_OFICIAL:
        raise ValueError("Este relatório não possui PDF oficial.")

    buffer = BytesIO()
    empresa = Empresa.objects.first()
    nome = empresa.nome_fantasia if empresa else "ERP Helvi"
    styles = getSampleStyleSheet()
    normal = ParagraphStyle("normal", parent=styles["BodyText"], fontName="Helvetica", fontSize=7, leading=9)
    cabecalho = ParagraphStyle("cabecalho", parent=normal, fontName="Helvetica-Bold", textColor=colors.white, alignment=TA_CENTER)
    titulo = ParagraphStyle("titulo", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=16, textColor=colors.HexColor("#242424"), spaceAfter=4)
    meta = ParagraphStyle("meta", parent=normal, fontSize=8, textColor=colors.HexColor("#666666"))

    def rodape(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#D8D2C4"))
        canvas.line(14 * mm, 11 * mm, 283 * mm, 11 * mm)
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(colors.HexColor("#666666"))
        canvas.drawString(14 * mm, 7 * mm, nome)
        canvas.drawRightString(283 * mm, 7 * mm, f"Página {doc.page}")
        canvas.restoreState()

    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), leftMargin=14 * mm, rightMargin=14 * mm, topMargin=13 * mm, bottomMargin=16 * mm, title=relatorio["titulo"], author=nome)
    elementos = [
        Paragraph(nome, meta),
        Paragraph(relatorio["titulo"], titulo),
        Paragraph(f"{relatorio['subtitulo']}<br/>Período: {periodo}<br/>Emitido em {timezone.localtime():%d/%m/%Y %H:%M}", meta),
        Spacer(1, 5 * mm),
    ]
    kpis = [[_texto(k["titulo"], cabecalho), _texto(k["valor"], normal)] for k in relatorio["kpis"]]
    tabela_kpis = Table(kpis, colWidths=[36 * mm, 45 * mm], hAlign="LEFT")
    tabela_kpis.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#A77E1F")), ("GRID", (0, 0), (-1, -1), .35, colors.HexColor("#D8D2C4")), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("ALIGN", (1, 0), (1, -1), "RIGHT"), ("BOTTOMPADDING", (0, 0), (-1, -1), 5), ("TOPPADDING", (0, 0), (-1, -1), 5)]))
    elementos.extend([tabela_kpis, Spacer(1, 5 * mm)])

    dados = [[_texto(c, cabecalho) for c in relatorio["colunas"]]]
    dados.extend([[_texto(v, normal) for v in linha["valores"]] for linha in relatorio["linhas"]])
    largura = 269 * mm / max(len(relatorio["colunas"]), 1)
    tabela = Table(dados, colWidths=[largura] * len(relatorio["colunas"]), repeatRows=1, hAlign="LEFT")
    tabela.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#242424")), ("GRID", (0, 0), (-1, -1), .3, colors.HexColor("#D8D2C4")), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7F5F0")]), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4), ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    elementos.append(tabela)
    doc.build(elementos, onFirstPage=rodape, onLaterPages=rodape)
    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="relatorio-{slug}.pdf"'
    return response
