from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from compras.forms import PagamentoCompraForm

from compras.models import Compra


def moeda(valor):
    return f"R$ {valor:.2f}".replace(".", ",")


@login_required
def ficha_compra(request, pk):
    compra = get_object_or_404(
        Compra.objects.prefetch_related("itens__produto"),
        pk=pk,
    )

    itens = compra.itens.all()

    quantidade_itens = itens.count()
    quantidade_pecas = sum(item.quantidade for item in itens)

    ficha_resumo = [
        {"label": "Status", "valor": compra.get_status_display()},
        {"label": "Pagamento", "valor": compra.get_status_pagamento_display()},
        {"label": "Itens", "valor": quantidade_itens},
        {"label": "Peças", "valor": quantidade_pecas},
        {"label": "Total", "valor": moeda(compra.total)},
    ]

    dados_gerais = [
        {"label": "Fornecedor", "valor": compra.fornecedor_nome},
        {"label": "Documento", "valor": compra.fornecedor_documento or "Não informado"},
        {"label": "Telefone", "valor": compra.fornecedor_telefone or "Não informado"},
        {"label": "Data da compra", "valor": compra.data_compra.strftime("%d/%m/%Y")},
        {
            "label": "Previsão de entrega",
            "valor": compra.previsao_entrega.strftime("%d/%m/%Y")
            if compra.previsao_entrega
            else "Não informada",
        },
        {
            "label": "Entrada no estoque",
            "valor": "Realizada" if compra.entrada_estoque_realizada else "Pendente",
        },
    ]

    resumo_financeiro = [
        {"label": "Subtotal", "valor": moeda(compra.subtotal)},
        {"label": "Desconto", "valor": moeda(compra.desconto)},
        {"label": "Frete", "valor": moeda(compra.frete)},
        {"label": "Total", "valor": moeda(compra.total)},
        {"label": "Valor pago", "valor": moeda(compra.valor_pago)},
        {"label": "Saldo a pagar", "valor": moeda(compra.saldo_a_pagar)},
        {"label": "Status do pagamento", "valor": compra.get_status_pagamento_display()},
    ]
    pagamentos = compra.pagamentos.select_related("registrado_por").all()
    pagamento_form = PagamentoCompraForm(compra=compra)

    context = {
        "compra": compra,
        "itens": itens,
        "quantidade_itens": quantidade_itens,
        "quantidade_pecas": quantidade_pecas,
        "ficha_titulo": f"Compra #{compra.numero}",
        "ficha_subtitulo": f"{compra.fornecedor_nome} • {compra.data_compra.strftime('%d/%m/%Y')}",
        "ficha_resumo": ficha_resumo,
        "dados_gerais": dados_gerais,
        "resumo_financeiro": resumo_financeiro,
        "pagamentos": pagamentos,
        "pagamento_form": pagamento_form,
    }

    return render(request, "compras/ficha_compra.html", context)