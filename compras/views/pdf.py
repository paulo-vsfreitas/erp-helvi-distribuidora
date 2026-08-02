from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from compras.models import Compra
from core.pdf.documents.compra import CompraPDF


@login_required
def gerar_pdf_compra(request, pk):
    compra = get_object_or_404(
        Compra.objects.prefetch_related("itens__produto"),
        pk=pk,
    )

    pdf = CompraPDF(compra)

    response = HttpResponse(
        pdf.build(),
        content_type="application/pdf",
    )

    response["Content-Disposition"] = (
        f'inline; filename="compra_{compra.numero}.pdf"'
    )

    return response