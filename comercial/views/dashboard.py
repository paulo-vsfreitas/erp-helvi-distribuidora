from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.shortcuts import render

from comercial.models import Orcamento


@login_required
def dashboard(request):
    orcamentos = (
        Orcamento.objects
        .select_related(
            "cliente",
            "vendedor",
        )
        .annotate(
            qtd_itens=Count(
                "itens",
                distinct=True,
            ),
            qtd_pecas=Sum(
                "itens__quantidade",
            ),
        )
        .order_by(
            "-data_emissao",
            "-numero",
        )
    )

    contexto = {
        "titulo": "Comercial",
        "subtitulo": "Gestão de orçamentos e operações comerciais.",
        "orcamentos": orcamentos,
        "total_orcamentos": orcamentos.count(),
        "total_rascunhos": orcamentos.filter(
            status=Orcamento.Status.RASCUNHO,
        ).count(),
        "total_aprovados": orcamentos.filter(
            status=Orcamento.Status.APROVADO,
        ).count(),
        "valor_total": (
            orcamentos.aggregate(
                total_geral=Sum("total"),
            )["total_geral"]
            or 0
        ),
    }

    return render(
        request,
        "comercial/dashboard.html",
        contexto,
    )