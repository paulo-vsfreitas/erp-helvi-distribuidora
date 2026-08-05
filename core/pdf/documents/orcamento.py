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
from core.pdf.elements.quantities import resumo_quantidades
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
            exibir_data_emissao=False,
        )

    def build(self):
        self._header()
        self._dados()
        self._cliente()
        self._entrega()
        self._itens()
        self._resumo_quantidades()
        self._financeiro()
        self._informacoes_comerciais()
        self._assinaturas()

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
            [Paragraph(f"<b>Status:</b> {self.orcamento.get_status_display()}", TEXT), Paragraph(f"<b>Vendedor:</b> {vendedor}", TEXT)],
            [Paragraph(f"<b>Emissão:</b> {self.orcamento.data_emissao:%d/%m/%Y}", TEXT), Paragraph(f"<b>Validade:</b> {self.orcamento.data_validade:%d/%m/%Y}", TEXT)],
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

    def _entrega(self):
        self._section("ENTREGA")
        if self.orcamento.tipo_entrega == "envio":
            endereco = ", ".join(filter(None, [
                self.orcamento.entrega_logradouro, self.orcamento.entrega_numero,
                self.orcamento.entrega_complemento, self.orcamento.entrega_bairro,
                self.orcamento.entrega_cidade, self.orcamento.entrega_estado,
                self.orcamento.entrega_cep,
            ]))
        else:
            endereco = "Retirada no estabelecimento"
        tabela = Table([[
            Paragraph(f"<b>Modalidade:</b> {self.orcamento.get_tipo_entrega_display()}", TEXT),
            Paragraph(f"<b>Endereço:</b> {endereco or '-'}", TEXT),
        ]], colWidths=[150, 360])
        tabela.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), reportlab_colors.HexColor("#FFF9E9")),
            ("BOX", (0, 0), (-1, -1), 0.5, helvi_colors.HELVI_GOLD),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("PADDING", (0, 0), (-1, -1), 7),
        ]))
        self.pdf.story.extend([tabela, Spacer(1, 5 * mm)])

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
                "Cor",
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
            produto = item.produto.modelo or "Produto sem modelo"

            if item.produto.marca:
                produto += f" | {item.produto.marca.nome}"

            dados.append(
                [
                    Paragraph(item.produto.codigo or "Não informado", TEXT),
                    Paragraph(produto, TEXT),
                    Paragraph(str(item.variacao_cor or "Sem variação"), TEXT),
                    Paragraph(str(item.quantidade), TEXT),
                    Paragraph(moeda(item.valor_unitario), TEXT),
                    Paragraph(moeda(item.desconto), TEXT),
                    Paragraph(moeda(item.total), TEXT),
                ]
            )

        tabela = Table(
            dados,
            colWidths=[
                50,
                130,
                65,
                35,
                70,
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

    def _resumo_quantidades(self):
        self.pdf.story.append(resumo_quantidades(
            produtos=self.orcamento.quantidade_produtos,
            itens=self.orcamento.quantidade_itens,
            pecas=self.orcamento.quantidade_pecas,
        ))

    def _financeiro(self):
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

        self.pdf.story.append(KeepTogether([
            Paragraph("RESUMO FINANCEIRO", SUBTITLE),
            Spacer(1, 1 * mm),
            tabela,
        ]))

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

    def _assinaturas(self):
        tabela = Table([
            ["", ""],
            [Paragraph("Cliente / responsável", TEXT), Paragraph("Helvi Distribuidora", TEXT)],
        ], colWidths=[220, 220], hAlign="CENTER")
        tabela.setStyle(TableStyle([
            ("LINEABOVE", (0, 1), (-1, 1), 0.5, helvi_colors.GRAY_700),
            ("ALIGN", (0, 1), (-1, 1), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, 0), 22),
        ]))
        self.pdf.story.extend([Spacer(1, 10 * mm), KeepTogether(tabela)])

    def _section(self, titulo):
        self.pdf.story.append(
            Paragraph(
                titulo,
                SUBTITLE,
            )
        )
        self.pdf.story.append(Spacer(1, 1 * mm))
