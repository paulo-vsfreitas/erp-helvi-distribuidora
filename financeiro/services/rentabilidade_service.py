from decimal import Decimal

from django.db.models import Q
from django.utils import timezone

from financeiro.forms.rentabilidade import RentabilidadeFiltroForm
from core.formatters import formatar_moeda_br
from vendas.models import Venda


ZERO = Decimal("0.00")


def _percentual(valor, base):
    return (valor / base * Decimal("100")) if base else ZERO


def obter_rentabilidade(parametros):
    hoje = timezone.localdate()
    if not parametros:
        parametros = {
            "data_inicial": hoje.replace(day=1).isoformat(),
            "data_final": hoje.isoformat(),
        }

    form = RentabilidadeFiltroForm(parametros)
    vendas = (
        Venda.objects.filter(status=Venda.STATUS_FINALIZADA)
        .select_related("cliente", "criada_por")
        .prefetch_related("itens", "itens__produto")
        .order_by("-data_venda", "-pk")
    )

    if form.is_valid():
        data_inicial = form.cleaned_data.get("data_inicial")
        data_final = form.cleaned_data.get("data_final")
        busca = form.cleaned_data.get("busca")
        if data_inicial:
            vendas = vendas.filter(data_venda__date__gte=data_inicial)
        if data_final:
            vendas = vendas.filter(data_venda__date__lte=data_final)
        if busca:
            filtro = (
                Q(cliente__nome__icontains=busca)
                | Q(cliente__razao_social__icontains=busca)
                | Q(criada_por__first_name__icontains=busca)
                | Q(criada_por__last_name__icontains=busca)
                | Q(criada_por__username__icontains=busca)
                | Q(itens__produto__codigo__icontains=busca)
                | Q(itens__produto__codigo_fornecedor__icontains=busca)
                | Q(itens__produto__modelo__icontains=busca)
                | Q(itens__produto__observacoes__icontains=busca)
            )
            if busca.isdigit():
                filtro |= Q(numero=int(busca))
            vendas = vendas.filter(filtro).distinct()

    linhas = []
    receita_produtos = custo_total = frete_total = ZERO
    quantidade_pecas = 0

    for venda in vendas:
        itens = list(venda.itens.all())
        receita = max(venda.total - venda.frete, ZERO)
        custo = sum((item.custo_unitario * item.quantidade for item in itens), ZERO)
        lucro = receita - custo
        pecas = sum(item.quantidade for item in itens)
        vendedor = venda.criada_por
        linhas.append({
            "venda": venda,
            "cliente": venda.cliente or "Consumidor final",
            "vendedor": (vendedor.get_full_name() or vendedor.username) if vendedor else "Não informado",
            "receita": receita,
            "custo": custo,
            "lucro": lucro,
            "margem": _percentual(lucro, receita),
            "pecas": pecas,
        })
        receita_produtos += receita
        custo_total += custo
        frete_total += venda.frete
        quantidade_pecas += pecas

    lucro_bruto = receita_produtos - custo_total
    return {
        "form": form,
        "linhas": linhas,
        "quantidade_vendas": len(linhas),
        "quantidade_pecas": quantidade_pecas,
        "receita_produtos": receita_produtos,
        "receita_produtos_formatada": formatar_moeda_br(receita_produtos),
        "custo_total": custo_total,
        "custo_total_formatado": formatar_moeda_br(custo_total),
        "lucro_bruto": lucro_bruto,
        "lucro_bruto_formatado": formatar_moeda_br(lucro_bruto),
        "margem_bruta": _percentual(lucro_bruto, receita_produtos),
        "frete_total": frete_total,
        "frete_total_formatado": formatar_moeda_br(frete_total),
    }
