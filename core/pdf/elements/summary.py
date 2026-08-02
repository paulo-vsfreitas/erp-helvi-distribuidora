from reportlab.platypus import Table
from reportlab.platypus import TableStyle
from reportlab.lib import colors as reportlab_colors
from core.pdf import colors as helvi_colors


def moeda(valor):
    return (
        f"R$ {valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def build_summary(compra):

    dados = [
        ["Subtotal", moeda(compra.subtotal)],
        ["(-) Desconto", moeda(compra.desconto)],
        ["(+) Frete", moeda(compra.frete)],
        ["TOTAL", moeda(compra.total)],
    ]

    tabela = Table(
        dados,
        colWidths=[120, 90],
    )

    tabela.setStyle(
        TableStyle(
            [

                ("FONTNAME", (0, 3), (-1, 3), "Helvetica-Bold"),

                ("LINEABOVE", (0, 3), (-1, 3), 0.8, reportlab_colors.black),

                ("ALIGN", (1, 0), (-1, -1), "RIGHT"),

                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),

                (
                    "BACKGROUND",
                    (0, 3),
                    (-1, 3),
                    helvi_colors.HELVI_GOLD,
                ),

                (
                    "TEXTCOLOR",
                    (0, 3),
                    (-1, 3),
                    reportlab_colors.white,
                ),

                (
                    "FONTNAME",
                    (0, 3),
                    (-1, 3),
                    "Helvetica-Bold",
                ),

            ]
        )
    )

    return tabela