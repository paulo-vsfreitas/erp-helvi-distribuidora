from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, Spacer

from ..styles import LABEL, TEXT


def linha(label, valor):
    return Paragraph(
        f"<b>{label}:</b> {valor or '-'}",
        TEXT,
    )


def build_purchase_info(compra):

    elementos = []

    elementos.append(
        linha(
            "Fornecedor",
            compra.fornecedor_nome,
        )
    )

    elementos.append(
        linha(
            "Documento",
            compra.fornecedor_documento,
        )
    )

    elementos.append(
        linha(
            "Telefone",
            compra.fornecedor_telefone,
        )
    )

    elementos.append(
        linha(
            "Data da compra",
            compra.data_compra.strftime("%d/%m/%Y"),
        )
    )

    elementos.append(
        linha(
            "Previsão de entrega",
            (
                compra.previsao_entrega.strftime("%d/%m/%Y")
                if compra.previsao_entrega
                else "-"
            ),
        )
    )

    elementos.append(
        linha(
            "Status da compra",
            compra.get_status_display(),
        )
    )

    elementos.append(
        linha(
            "Status do pagamento",
            compra.get_status_pagamento_display(),
        )
    )

    elementos.append(
        Spacer(
            1,
            6 * mm,
        )
    )

    return elementos