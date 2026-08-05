from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Image, Paragraph, Spacer, Table, TableStyle

from configuracoes.services.empresa_service import obter_empresa

from .. import colors
from ..styles import LABEL, TEXT
from .social import build_social_channels


def build_company():
    """
    Retorna o cabeçalho institucional da empresa
    como uma lista de elementos do ReportLab.
    """

    empresa = obter_empresa()

    elementos = []

    logo = None

    if empresa.logo:
        try:
            logo = Image(empresa.logo.path)
            logo._restrictSize(37 * mm, 30 * mm)
        except Exception:
            logo = Spacer(37 * mm, 30 * mm)
    else:
        logo = Spacer(37 * mm, 30 * mm)

    nome_style = ParagraphStyle("EmpresaNome", parent=LABEL, fontSize=12, leading=14)
    detalhe_style = ParagraphStyle("EmpresaDetalhe", parent=TEXT, fontSize=8.5, leading=11)
    identidade = [Paragraph(empresa.nome_fantasia, nome_style)]

    if (
        empresa.razao_social
        and empresa.razao_social.strip().casefold()
        != (empresa.nome_fantasia or "").strip().casefold()
    ):
        identidade.append(Paragraph(empresa.razao_social, detalhe_style))

    dados = []
    if empresa.cnpj:
        dados.append(Paragraph(f"<b>CNPJ:</b> {empresa.cnpj}", detalhe_style))

    if empresa.telefone:
        dados.append(Paragraph(f"<b>Telefone:</b> {empresa.telefone}", detalhe_style))

    if empresa.email:
        dados.append(Paragraph(f"<b>E-mail:</b> {empresa.email}", detalhe_style))

    linhas = [[identidade]]
    if dados:
        tabela_dados = Table(
            [dados[i:i + 2] for i in range(0, len(dados), 2)],
            colWidths=[67 * mm, 67 * mm],
        )
        tabela_dados.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 1),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ]))
        linhas.append([tabela_dados])

    canais = build_social_channels(empresa)
    if canais:
        linhas.append([canais])

    if empresa.endereco_completo:
        linhas.append([Paragraph(f"<b>Endereço:</b> {empresa.endereco_completo}", detalhe_style)])

    bloco_dados = Table(linhas, colWidths=[136 * mm])
    bloco_dados.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 3),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 2),
    ]))

    tabela = Table(
        [
            [
                logo,
                bloco_dados,
            ]
        ],
        colWidths=[
            42 * mm,
            143 * mm,
        ],
    )

    tabela.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (0, 0), "MIDDLE"),
                ("VALIGN", (1, 0), (1, 0), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LINEBELOW", (0, 0), (-1, -1), 1, colors.HELVI_GOLD),
            ]
        )
    )

    elementos.append(tabela)

    elementos.append(
        Spacer(
            1,
            10 * mm,
        )
    )

    return elementos
