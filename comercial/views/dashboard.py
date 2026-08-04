from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.shortcuts import render
from django.utils.dateparse import parse_date

from comercial.models import Orcamento


@login_required
def dashboard(request):
    todos_orcamentos = (
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

    filtros = dict(Orcamento.Status.choices)
    titulos_status = {
        Orcamento.Status.RASCUNHO: "Rascunhos",
        Orcamento.Status.ENVIADO: "Enviados",
        Orcamento.Status.APROVADO: "Aprovados",
        Orcamento.Status.REJEITADO: "Rejeitados",
        Orcamento.Status.CANCELADO: "Cancelados",
        Orcamento.Status.CONVERTIDO: "Convertidos em venda",
    }
    filtro_status = request.GET.get("status", "")
    if filtro_status not in filtros:
        filtro_status = ""

    busca = request.GET.get("busca", "").strip()
    data_inicio_texto = request.GET.get("data_inicio", "")
    data_fim_texto = request.GET.get("data_fim", "")
    data_inicio = parse_date(data_inicio_texto)
    data_fim = parse_date(data_fim_texto)

    orcamentos = todos_orcamentos
    if filtro_status:
        orcamentos = orcamentos.filter(status=filtro_status)
    if busca:
        if busca.upper().startswith("ORC-"):
            busca_numero = busca[4:].lstrip("0") or "0"
        else:
            busca_numero = busca

        if busca_numero.isdigit():
            orcamentos = orcamentos.filter(numero=int(busca_numero))
        else:
            orcamentos = orcamentos.filter(cliente_nome__icontains=busca)
    if data_inicio:
        orcamentos = orcamentos.filter(data_emissao__gte=data_inicio)
    if data_fim:
        orcamentos = orcamentos.filter(data_emissao__lte=data_fim)

    filtros_ativos = any((
        filtro_status,
        busca,
        data_inicio,
        data_fim,
    ))

    contexto = {
        "titulo": "Comercial",
        "subtitulo": "Gestão de orçamentos e operações comerciais.",
        "orcamentos": orcamentos,
        "total_orcamentos": todos_orcamentos.count(),
        "total_rascunhos": todos_orcamentos.filter(
            status=Orcamento.Status.RASCUNHO,
        ).count(),
        "total_aprovados": todos_orcamentos.filter(
            status=Orcamento.Status.APROVADO,
        ).count(),
        "valor_total": (
            todos_orcamentos.filter(
                status__in=(
                    Orcamento.Status.RASCUNHO,
                    Orcamento.Status.ENVIADO,
                    Orcamento.Status.APROVADO,
                ),
            ).aggregate(
                total_geral=Sum("total"),
            )["total_geral"]
            or 0
        ),
        "filtro_status": filtro_status,
        "busca": busca,
        "data_inicio": data_inicio_texto if data_inicio else "",
        "data_fim": data_fim_texto if data_fim else "",
        "status_opcoes": Orcamento.Status.choices,
        "filtros_ativos": filtros_ativos,
        "titulo_lista": titulos_status.get(
            filtro_status,
            "Orçamentos filtrados" if filtros_ativos else "Orçamentos recentes",
        ),
    }

    return render(
        request,
        "comercial/dashboard.html",
        contexto,
    )
