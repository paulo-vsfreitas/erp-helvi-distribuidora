from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate
from .header import build_header
from .elements.title import build_title
from .footer import draw_footer


class HelviPDF:
    """
    Classe base do Framework de PDFs do ERP Helvi.

    Responsabilidades:

    • criar o documento
    • armazenar os elementos
    • gerar o PDF em memória

    Nas próximas etapas ela também será responsável por:

    • cabeçalho
    • rodapé
    • estilos
    • tabelas
    • paginação
    """

    def __init__(
        self,
        title="Documento",
        pagesize=A4,
    ):
        self.title = title
        self.pagesize = pagesize

        self.buffer = BytesIO()

        self.story = []

    def build(self):
        doc = SimpleDocTemplate(
            self.buffer,
            pagesize=self.pagesize,
            leftMargin=40,
            rightMargin=40,
            topMargin=45,
            bottomMargin=55,
            title=self.title,
        )

        doc.build(
            self.story,
            onFirstPage=draw_footer,
            onLaterPages=draw_footer,
        )

        pdf = self.buffer.getvalue()

        self.buffer.close()

        return pdf

    def _draw_footer(
            self,
            canvas,
            doc,
        ):
        doc.build(
            self.story,
            onFirstPage=self._draw_footer,
            onLaterPages=self._draw_footer,
            
        )

        pdf = self.buffer.getvalue()

        self.buffer.close()

        return pdf
    
    def add_header(self):
        build_header(self.story)

    def add_title(self, texto):
        self.story.extend(
            build_title(texto)
        )
    
