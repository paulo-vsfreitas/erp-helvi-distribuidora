from reportlab.platypus import (
    Paragraph,
    Spacer,
)

from reportlab.lib.units import mm

from ..styles import TITLE


def build_title(texto):
    """
    Retorna um bloco de título padronizado
    para qualquer documento do ERP.
    """

    return [
        Paragraph(
            texto,
            TITLE,
        ),
        Spacer(
            1,
            5 * mm,
        ),
    ]