from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from comercial.models import Orcamento
from core.pdf.documents.orcamento import OrcamentoPDF


def obter_orcamento_pdf(numero):
    return get_object_or_404(
        Orcamento.objects
        .select_related(
            "cliente",
            "vendedor",
        )
        .prefetch_related(
            "itens__produto",
            "itens__produto__marca",
        ),
        numero=numero,
    )


@login_required
def gerar_pdf_orcamento(request, numero):
    orcamento = obter_orcamento_pdf(numero)
    pdf = OrcamentoPDF(orcamento)

    response = HttpResponse(
        pdf.build(),
        content_type="application/pdf",
    )

    response["Content-Disposition"] = (
        f'inline; filename="{orcamento.codigo.lower()}.pdf"'
    )
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response["Pragma"] = "no-cache"

    return response


@login_required
def baixar_pdf_orcamento(request, numero):
    orcamento = obter_orcamento_pdf(numero)
    pdf = OrcamentoPDF(orcamento)

    response = HttpResponse(
        pdf.build(),
        content_type="application/pdf",
    )

    response["Content-Disposition"] = (
        f'attachment; filename="{orcamento.codigo.lower()}.pdf"'
    )
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response["Pragma"] = "no-cache"

    return response
