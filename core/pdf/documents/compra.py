from reportlab.graphics.shapes import Drawing, Line
from reportlab.lib import colors as reportlab_colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    KeepTogether,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from core.pdf import HelviPDF
from core.pdf.elements.purchase_info import build_purchase_info
from core.pdf.elements.summary import build_summary
from core.pdf.styles import SUBTITLE, TEXT
from core.pdf.tables import build_products_table


class CompraPDF:
    """
    Monta o documento PDF de uma compra.
    """

    def __init__(self, compra):
        self.compra = compra
        self.pdf = HelviPDF(
            title=f"Compra {compra.numero}",
        )

    def build(self):
        self._header()
        self._dados()
        self._itens()
        self._financeiro()
        self._observacoes()

        return self.pdf.build()

    def _header(self):
        self.pdf.add_header()

        self.pdf.add_title(
            f"COMPRA Nº {self.compra.numero:06d}"
        )

    def _dados(self):
        self._section("DADOS DA COMPRA")

        self.pdf.story.extend(
            build_purchase_info(
                self.compra,
            )
        )

    def _itens(self):
        self._section("ITENS DA COMPRA")

        self.pdf.story.append(
            build_products_table(
                self.compra.itens.select_related(
                    "produto",
                )
            )
        )

        self.pdf.story.append(
            Spacer(
                1,
                6 * mm,
            )
        )

    def _financeiro(self):

        self.pdf.story.append(
            KeepTogether(
                [
                    build_summary(
                        self.compra,
                    )
                ]
            )
        )

        self.pdf.story.append(
            Spacer(
                1,
                6 * mm,
            )
        )

    def _observacoes(self):
        observacoes = (
            self.compra.observacoes
            or ""
        ).strip()

        if not observacoes:
            return

        self._section("OBSERVAÇÕES")

        caixa_observacoes = Table(
            [
                [
                    Paragraph(
                        observacoes,
                        TEXT,
                    )
                ]
            ],
            colWidths=[450],
        )

        caixa_observacoes.setStyle(
            TableStyle(
                [
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        reportlab_colors.grey,
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        8,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        8,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        8,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        8,
                    ),
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        reportlab_colors.whitesmoke,
                    ),
                ]
            )
        )

        self.pdf.story.append(
            caixa_observacoes
        )

        self.pdf.story.append(
            Spacer(
                1,
                6 * mm,
            )
        )
    def _section(self, titulo):
        self.pdf.story.append(
            Paragraph(
                titulo,
                SUBTITLE,
            )
        )

        desenho = Drawing(
            480,
            1,
        )

        desenho.add(
            Line(
                0,
                0,
                480,
                0,
            )
        )

        self.pdf.story.append(desenho)

        self.pdf.story.append(
            Spacer(
                1,
                3 * mm,
            )
        )