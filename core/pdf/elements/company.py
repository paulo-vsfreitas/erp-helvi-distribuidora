from reportlab.platypus import (
    Image,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from reportlab.lib.units import mm

from configuracoes.services.empresa_service import obter_empresa

from .. import colors
from ..styles import LABEL, TEXT


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
            logo = Image(
                empresa.logo.path,
                width=36 * mm,
                height=36 * mm,
            )
        except Exception:
            logo = Spacer(36 * mm, 36 * mm)
    else:
        logo = Spacer(36 * mm, 36 * mm)

    linhas = [
        Paragraph(
            empresa.nome_fantasia,
            LABEL,
        )
    ]

    if empresa.razao_social:
        linhas.append(
            Paragraph(
                empresa.razao_social,
                TEXT,
            )
        )

    if empresa.cnpj:
        linhas.append(
            Paragraph(
                f"CNPJ: {empresa.cnpj}",
                TEXT,
            )
        )

    if empresa.telefone:
        linhas.append(
            Paragraph(
                f"Telefone: {empresa.telefone}",
                TEXT,
            )
        )

    if empresa.email:
        linhas.append(
            Paragraph(
                empresa.email,
                TEXT,
            )
        )

    if empresa.endereco_completo:
        linhas.append(
            Paragraph(
                empresa.endereco_completo,
                TEXT,
            )
        )

    tabela = Table(
        [
            [
                logo,
                linhas,
            ]
        ],
        colWidths=[
            45 * mm,
            140 * mm,
        ],
    )

    tabela.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
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