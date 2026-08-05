from reportlab.lib import colors as reportlab_colors

from core.pdf import colors as helvi_colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle

from reportlab.platypus import (
    Paragraph,
    Table,
    TableStyle,
)

from .styles import TEXT


CENTER = ParagraphStyle(
    "Center",
    parent=TEXT,
    alignment=TA_CENTER,
)

RIGHT = ParagraphStyle(
    "Right",
    parent=TEXT,
    alignment=TA_RIGHT,
)

LEFT = ParagraphStyle(
    "Left",
    parent=TEXT,
    alignment=TA_LEFT,
)


def moeda(valor):
    return (
        f"R$ {valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def build_products_table(itens):

    dados = [
        [
            "Código",
            "Produto",
            "Qtd",
            "Unit.",
            "Desc.",
            "Total",
        ]
    ]

    for item in itens:

        dados.append(
            [
                Paragraph(item.produto.codigo or "Não informado", LEFT),
                Paragraph(item.produto.modelo or "Não informado", LEFT),
                Paragraph(str(item.quantidade), CENTER),
                Paragraph(moeda(item.custo_unitario), RIGHT),
                Paragraph(moeda(item.desconto), RIGHT),
                Paragraph(moeda(item.total), RIGHT),
            ]
        )

    tabela = Table(
        dados,
        colWidths=[
            55,
            180,
            40,
            70,
            70,
            70,
        ],
    )

    tabela.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    helvi_colors.HELVI_GOLD,
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    reportlab_colors.white,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.3,
                    reportlab_colors.grey,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    for linha in range(1, len(dados)):
        if linha % 2 == 0:
            tabela.setStyle(
                TableStyle(
                    [
                        (
                            "BACKGROUND",
                            (0, linha),
                            (-1, linha),
                            reportlab_colors.whitesmoke,
                        )
                    ]
                )
            )

    return tabela
