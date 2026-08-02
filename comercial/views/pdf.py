from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from comercial.models import Orcamento
from core.pdf.documents.orcamento import OrcamentoPDF


@login_required
def gerar_pdf_orcamento(request, numero):
    orcamento = get_object_or_404(
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

    pdf = OrcamentoPDF(orcamento)

    response = HttpResponse(
        pdf.build(),
        content_type="application/pdf",
    )

    response["Content-Disposition"] = (
        f'inline; filename="{orcamento.codigo.lower()}.pdf"'
    )

    return response