from reportlab.graphics.shapes import Drawing, Line
from reportlab.lib.units import mm
from reportlab.platypus import (
    KeepTogether,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from reportlab.lib import colors as reportlab_colors

from core.pdf import HelviPDF
from core.pdf import colors as helvi_colors
from core.pdf.styles import SUBTITLE, TEXT


def moeda(valor):
    return (
        f"R$ {valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


class OrcamentoPDF:
    def __init__(self, orcamento):
        self.orcamento = orcamento
        self.pdf = HelviPDF(
            title=f"Orçamento {orcamento.codigo}",
        )

    def build(self):
        self._header()
        self._dados()
        self._cliente()
        self._itens()
        self._financeiro()
        self._informacoes_comerciais()

        return self.pdf.build()

    def _header(self):
        self.pdf.add_header()

        self.pdf.add_title(
            f"ORÇAMENTO Nº {self.orcamento.numero:06d}"
        )

    def _dados(self):
        self._section("DADOS DO ORÇAMENTO")

        vendedor = (
            self.orcamento.vendedor.get_full_name()
            or self.orcamento.vendedor.username
        )

        dados = [
            [
                "Subtotal bruto dos itens",
                moeda(self.orcamento.subtotal),
            ],

            [
                "(-) Desconto geral",
                moeda(self.orcamento.desconto),
            ],
            [
                "(+) Frete",
                moeda(self.orcamento.frete),
            ],
            [
                "TOTAL",
                moeda(self.orcamento.total),
            ],
        ]

        tabela = Table(
            dados,
            colWidths=[160, 100],
        )

        tabela.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ]
            )
        )

        self.pdf.story.append(tabela)
        self.pdf.story.append(Spacer(1, 5 * mm))

    def _cliente(self):
        self._section("CLIENTE OU INTERESSADO")

        dados = [
            [
                Paragraph(
                    f"<b>Nome:</b> {self.orcamento.cliente_nome}",
                    TEXT,
                ),
                Paragraph(
                    "<b>Tipo:</b> "
                    + (
                        "Cliente cadastrado"
                        if self.orcamento.cliente_id
                        else "Interessado avulso"
                    ),
                    TEXT,
                ),
            ],
            [
                Paragraph(
                    f"<b>CPF / CNPJ:</b> "
                    f"{self.orcamento.cliente_documento or '-'}",
                    TEXT,
                ),
                Paragraph(
                    f"<b>Telefone / WhatsApp:</b> "
                    f"{self.orcamento.cliente_telefone or '-'}",
                    TEXT,
                ),
            ],
            [
                Paragraph(
                    f"<b>E-mail:</b> "
                    f"{self.orcamento.cliente_email or '-'}",
                    TEXT,
                ),
                "",
            ],
        ]

        tabela = Table(
            dados,
            colWidths=[255, 255],
        )

        tabela.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ]
            )
        )

        self.pdf.story.append(tabela)
        self.pdf.story.append(Spacer(1, 5 * mm))

    def _itens(self):
        self._section("PRODUTOS")

        dados = [
            [
                "Código",
                "Produto",
                "Qtd.",
                "Unitário",
                "Desconto",
                "Total",
            ]
        ]

        for item in self.orcamento.itens.select_related(
            "produto",
            "produto__marca",
        ):
            produto = item.produto.modelo

            if item.produto.marca:
                produto += f" | {item.produto.marca.nome}"

            dados.append(
                [
                    Paragraph(str(item.produto.codigo), TEXT),
                    Paragraph(produto, TEXT),
                    Paragraph(str(item.quantidade), TEXT),
                    Paragraph(moeda(item.valor_unitario), TEXT),
                    Paragraph(moeda(item.desconto), TEXT),
                    Paragraph(moeda(item.total), TEXT),
                ]
            )

        tabela = Table(
            dados,
            colWidths=[
                55,
                180,
                40,
                80,
                75,
                80,
            ],
            repeatRows=1,
        )

        estilos = [
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
                "ALIGN",
                (2, 1),
                (2, -1),
                "CENTER",
            ),
            (
                "ALIGN",
                (3, 1),
                (-1, -1),
                "RIGHT",
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

        for linha in range(1, len(dados)):
            if linha % 2 == 0:
                estilos.append(
                    (
                        "BACKGROUND",
                        (0, linha),
                        (-1, linha),
                        reportlab_colors.whitesmoke,
                    )
                )

        tabela.setStyle(TableStyle(estilos))

        self.pdf.story.append(tabela)
        self.pdf.story.append(Spacer(1, 6 * mm))

    def _financeiro(self):
        self._section("RESUMO FINANCEIRO")

        itens = list(
            self.orcamento.itens.all()
        )

        desconto_itens = sum(
            (
                item.desconto
                for item in itens
            ),
            0,
        )

        subtotal_liquido = (
            self.orcamento.subtotal
            - desconto_itens
        )

        dados = [
            [
                "Valor dos produtos",
                moeda(self.orcamento.subtotal),
            ],
            [
                "(-) Descontos dos produtos",
                moeda(desconto_itens),
            ],
            [
                "Subtotal",
                moeda(subtotal_liquido),
            ],
            [
                "(-) Desconto comercial",
                moeda(self.orcamento.desconto),
            ],
            [
                "(+) Frete",
                moeda(self.orcamento.frete),
            ],
            [
                "TOTAL DO ORÇAMENTO",
                moeda(self.orcamento.total),
            ],
        ]

        tabela = Table(
            dados,
            colWidths=[170, 110],
            hAlign="RIGHT",
        )

        tabela.setStyle(
            TableStyle(
                [
                    (
                        "ALIGN",
                        (1, 0),
                        (-1, -1),
                        "RIGHT",
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
                    (
                        "BACKGROUND",
                        (0, 5),
                        (-1, 5),
                        helvi_colors.HELVI_GOLD,
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 5),
                        (-1, 5),
                        reportlab_colors.white,
                    ),
                    (
                        "FONTNAME",
                        (0, 5),
                        (-1, 5),
                        "Helvetica-Bold",
                    ),
                ]
            )
        )

        self.pdf.story.append(
            KeepTogether(
                [tabela]
            )
        )

        self.pdf.story.append(
            Spacer(
                1,
                6 * mm,
            )
        )

    def _informacoes_comerciais(self):
        blocos = []

        if self.orcamento.condicoes_comerciais.strip():
            blocos.append(
                (
                    "CONDIÇÕES COMERCIAIS",
                    self.orcamento.condicoes_comerciais,
                )
            )

        if self.orcamento.observacoes.strip():
            blocos.append(
                (
                    "OBSERVAÇÕES",
                    self.orcamento.observacoes,
                )
            )

        for titulo, texto in blocos:
            self._section(titulo)

            caixa = Table(
                [[Paragraph(texto, TEXT)]],
                colWidths=[500],
            )

            caixa.setStyle(
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
                            "BACKGROUND",
                            (0, 0),
                            (-1, -1),
                            reportlab_colors.whitesmoke,
                        ),
                        ("LEFTPADDING", (0, 0), (-1, -1), 8),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                        ("TOPPADDING", (0, 0), (-1, -1), 8),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ]
                )
            )

            self.pdf.story.append(caixa)
            self.pdf.story.append(Spacer(1, 5 * mm))

    def _section(self, titulo):
        self.pdf.story.append(
            Paragraph(
                titulo,
                SUBTITLE,
            )
        )

        desenho = Drawing(500, 1)

        desenho.add(
            Line(
                0,
                0,
                500,
                0,
            )
        )

        self.pdf.story.append(desenho)
        self.pdf.story.append(Spacer(1, 3 * mm))