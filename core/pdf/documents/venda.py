from html import escape

from reportlab.lib import colors as reportlab_colors
from reportlab.lib.units import mm
from reportlab.platypus import KeepTogether, Paragraph, Spacer, Table, TableStyle
from django.utils import timezone

from configuracoes.services.empresa_service import obter_empresa
from core.formatters import formatar_moeda_br
from core.pdf import HelviPDF
from core.pdf import colors as helvi_colors
from core.pdf.styles import LABEL, RIGHT, SUBTITLE, TEXT
from vendas.models import Venda


def _texto(valor, padrao="Não informado"):
    return escape(str(valor)) if valor not in (None, "") else padrao


class VendaPDF:
    def __init__(self, venda):
        self.venda = venda
        self.empresa = obter_empresa()
        self.pdf = HelviPDF(title=f"Resumo da venda {venda.numero:06d}")

    def build(self):
        self.pdf.add_header()
        self._cabecalho_pedido()
        self._cliente()
        self._entrega()
        self._itens()
        self._fechamento()
        self._observacoes()
        self._assinaturas()
        return self.pdf.build()

    def _titulo_secao(self, titulo):
        self.pdf.story.append(Paragraph(titulo, SUBTITLE))

    def _cabecalho_pedido(self):
        vendedor = self.venda.criada_por or self.venda.finalizada_por
        vendedor_nome = (
            vendedor.get_full_name() or vendedor.username
            if vendedor else "Não informado"
        )
        status_cor = {
            Venda.STATUS_FINALIZADA: helvi_colors.SUCCESS,
            Venda.STATUS_CANCELADA: helvi_colors.DANGER,
        }.get(self.venda.status, helvi_colors.WARNING)
        data_venda_local = timezone.localtime(self.venda.data_venda)
        atualizado_em = timezone.localtime()
        dados = [[
            Paragraph(
                f"<font size='17'><b>RESUMO DO PEDIDO</b></font><br/>"
                f"<font color='#5F6368'>Venda nº {self.venda.numero:06d}</font>",
                TEXT,
            ),
            Paragraph(
                f"<b>{escape(self.venda.get_status_display().upper())}</b><br/>"
                f"Venda: {data_venda_local:%d/%m/%Y às %H:%M}<br/>"
                f"<font size='8'>Atualizado: {atualizado_em:%d/%m/%Y %H:%M}</font>",
                RIGHT,
            ),
        ], [
            Paragraph(f"<b>Vendedor:</b> {_texto(vendedor_nome)}", TEXT),
            Paragraph(
                f"<b>Pagamento:</b> {_texto(self.venda.get_forma_pagamento_display() if self.venda.forma_pagamento else None)}",
                RIGHT,
            ),
        ]]
        tabela = Table(dados, colWidths=[112 * mm, 64 * mm])
        tabela.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), helvi_colors.GRAY_100),
            ("BOX", (0, 0), (-1, -1), 0.8, helvi_colors.HELVI_GOLD),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 9),
            ("RIGHTPADDING", (0, 0), (-1, -1), 9),
            ("TEXTCOLOR", (1, 0), (1, 0), status_cor),
        ]))
        self.pdf.story.extend([tabela, Spacer(1, 7 * mm)])

    def _cliente(self):
        self._titulo_secao("DADOS DO CLIENTE")
        cliente = self.venda.cliente
        if not cliente:
            linhas = [[Paragraph("<b>Cliente:</b> Consumidor final", TEXT), ""]]
        else:
            telefone = cliente.whatsapp or cliente.telefone
            linhas = [
                [Paragraph(f"<b>Nome:</b> {_texto(cliente.nome_fantasia or cliente.razao_social)}", TEXT),
                 Paragraph(f"<b>Razão social:</b> {_texto(cliente.razao_social)}", TEXT)],
                [Paragraph(f"<b>CPF/CNPJ:</b> {_texto(cliente.cnpj)}", TEXT),
                 Paragraph(f"<b>Responsável:</b> {_texto(cliente.responsavel)}", TEXT)],
                [Paragraph(f"<b>Telefone/WhatsApp:</b> {_texto(telefone)}", TEXT),
                 Paragraph(f"<b>E-mail:</b> {_texto(cliente.email)}", TEXT)],
            ]
        tabela = Table(linhas, colWidths=[88 * mm, 88 * mm])
        tabela.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.4, helvi_colors.GRAY_300),
            ("INNERGRID", (0, 0), (-1, -1), 0.25, helvi_colors.GRAY_300),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("PADDING", (0, 0), (-1, -1), 6),
        ]))
        self.pdf.story.extend([tabela, Spacer(1, 6 * mm)])

    def _entrega(self):
        self._titulo_secao("ENTREGA")
        if self.venda.tipo_entrega == Venda.ENTREGA_ENVIO:
            endereco = ", ".join(filter(None, [
                self.venda.entrega_logradouro, self.venda.entrega_numero,
                self.venda.entrega_complemento, self.venda.entrega_bairro,
                self.venda.entrega_cidade,
                f"{self.venda.entrega_estado} - CEP {self.venda.entrega_cep}".strip(" -"),
            ]))
        else:
            endereco = "Retirada no estabelecimento"
        dados = [[
            Paragraph(f"<b>Modalidade:</b> {_texto(self.venda.get_tipo_entrega_display())}", TEXT),
            Paragraph(f"<b>Endereço:</b> {_texto(endereco)}", TEXT),
        ]]
        tabela = Table(dados, colWidths=[52 * mm, 124 * mm])
        tabela.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), reportlab_colors.HexColor("#FFF9E9")),
            ("BOX", (0, 0), (-1, -1), 0.5, helvi_colors.HELVI_GOLD),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("PADDING", (0, 0), (-1, -1), 6),
        ]))
        self.pdf.story.extend([tabela, Spacer(1, 6 * mm)])

    def _itens(self):
        self._titulo_secao("ITENS DO PEDIDO")
        dados = [["Código", "Produto", "Cor", "Qtd.", "Unitário", "Desc.", "Total"]]
        for item in self.venda.itens.all():
            dados.append([
                Paragraph(_texto(item.produto.codigo, "-"), TEXT),
                Paragraph(_texto(item.produto), TEXT),
                Paragraph(_texto(item.variacao_cor, "Sem variação"), TEXT),
                str(item.quantidade),
                formatar_moeda_br(item.preco_unitario),
                formatar_moeda_br(item.desconto),
                formatar_moeda_br(item.total),
            ])
        tabela = Table(
            dados,
            colWidths=[18*mm, 45*mm, 31*mm, 12*mm, 25*mm, 21*mm, 26*mm],
            repeatRows=1,
        )
        estilos = [
            ("BACKGROUND", (0, 0), (-1, 0), helvi_colors.HELVI_GOLD),
            ("TEXTCOLOR", (0, 0), (-1, 0), reportlab_colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.3, helvi_colors.GRAY_300),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (3, 1), (-1, -1), "RIGHT"),
            ("PADDING", (0, 0), (-1, -1), 5),
        ]
        for indice in range(1, len(dados)):
            if indice % 2 == 0:
                estilos.append(("BACKGROUND", (0, indice), (-1, indice), helvi_colors.GRAY_100))
        tabela.setStyle(TableStyle(estilos))
        self.pdf.story.extend([tabela, Spacer(1, 7 * mm)])

    def _fechamento(self):
        resumo = Table([
            ["Subtotal", formatar_moeda_br(self.venda.subtotal)],
            ["Descontos", f"- {formatar_moeda_br(self.venda.desconto)}"],
            ["Frete", formatar_moeda_br(self.venda.frete)],
            ["TOTAL DO PEDIDO", formatar_moeda_br(self.venda.total)],
        ], colWidths=[55 * mm, 40 * mm])
        resumo.setStyle(TableStyle([
            ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
            ("FONTNAME", (0, 0), (-1, -2), "Helvetica"),
            ("LINEABOVE", (0, -1), (-1, -1), 1, helvi_colors.HELVI_GOLD),
            ("BACKGROUND", (0, -1), (-1, -1), helvi_colors.HELVI_BLACK),
            ("TEXTCOLOR", (0, -1), (-1, -1), reportlab_colors.white),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, -1), (-1, -1), 11),
            ("PADDING", (0, 0), (-1, -1), 6),
        ]))
        pagamento = Table([
            [Paragraph("<b>CONDIÇÕES COMERCIAIS</b>", LABEL)],
            [Paragraph(f"Forma de pagamento: {_texto(self.venda.get_forma_pagamento_display() if self.venda.forma_pagamento else None)}", TEXT)],
            [Paragraph(f"Situação do pagamento: {_texto(self.venda.get_status_pagamento_display())}", TEXT)],
            [Paragraph(f"Valor recebido: {formatar_moeda_br(self.venda.valor_recebido)}", TEXT)],
        ], colWidths=[75 * mm])
        pagamento.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.4, helvi_colors.GRAY_300),
            ("BACKGROUND", (0, 0), (-1, 0), helvi_colors.GRAY_100),
            ("PADDING", (0, 0), (-1, -1), 6),
        ]))
        bloco = Table([[pagamento, resumo]], colWidths=[78 * mm, 98 * mm])
        bloco.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
        self.pdf.story.extend([KeepTogether(bloco), Spacer(1, 7 * mm)])

    def _observacoes(self):
        if not self.venda.observacoes and not self.empresa.rodape_documentos:
            return
        self._titulo_secao("OBSERVAÇÕES")
        textos = []
        if self.venda.observacoes:
            textos.append(Paragraph(_texto(self.venda.observacoes), TEXT))
        if self.empresa.rodape_documentos:
            textos.append(Paragraph(_texto(self.empresa.rodape_documentos), TEXT))
        tabela = Table([[textos]], colWidths=[176 * mm])
        tabela.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), helvi_colors.GRAY_100),
            ("BOX", (0, 0), (-1, -1), 0.4, helvi_colors.GRAY_300),
            ("PADDING", (0, 0), (-1, -1), 7),
        ]))
        self.pdf.story.extend([tabela, Spacer(1, 12 * mm)])

    def _assinaturas(self):
        tabela = Table([
            ["", ""],
            [Paragraph("Cliente / responsável", TEXT), Paragraph("Helvi Distribuidora", TEXT)],
        ], colWidths=[78 * mm, 78 * mm], hAlign="CENTER")
        tabela.setStyle(TableStyle([
            ("LINEABOVE", (0, 1), (0, 1), 0.5, helvi_colors.GRAY_700),
            ("LINEABOVE", (1, 1), (1, 1), 0.5, helvi_colors.GRAY_700),
            ("ALIGN", (0, 1), (-1, 1), "CENTER"),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ]))
        self.pdf.story.append(KeepTogether(tabela))
