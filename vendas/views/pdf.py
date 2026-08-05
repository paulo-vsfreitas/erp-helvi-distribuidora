from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from core.pdf.documents.venda import VendaPDF
from vendas.models import Venda


@login_required
def pdf_resumo_venda(request, numero):
    venda = get_object_or_404(
        Venda.objects.select_related("cliente", "criada_por").prefetch_related(
            "itens__produto", "itens__variacao_cor"
        ),
        numero=numero,
    )
    response = HttpResponse(VendaPDF(venda).build(), content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="venda-{venda.numero:06d}.pdf"'
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response["Pragma"] = "no-cache"
    return response
