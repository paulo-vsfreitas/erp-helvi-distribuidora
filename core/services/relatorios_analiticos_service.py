from decimal import Decimal

from django.db.models import Count, DecimalField, Q, Sum, Value
from django.db.models.functions import Coalesce
from django.urls import reverse

from clientes.models import Cliente
from compras.models import Compra, ItemCompra
from estoque.models import MovimentacaoEstoque
from financeiro.models import ContaPagar, ContaReceber, MovimentacaoFinanceira
from fornecedores.models import Fornecedor
from produtos.models import Produto

from core.formatters import formatar_moeda_br
from core.services.indicadores import criar_indicador


ZERO = Value(Decimal("0.00"), output_field=DecimalField(max_digits=14, decimal_places=2))


def _moeda(valor):
    return formatar_moeda_br(valor or 0)


def _data(valor):
    return valor.strftime("%d/%m/%Y") if valor else "—"


def _periodo(qs, filtros, campo):
    if filtros.get("data_inicial"):
        qs = qs.filter(**{f"{campo}__gte": filtros["data_inicial"]})
    if filtros.get("data_final"):
        qs = qs.filter(**{f"{campo}__lte": filtros["data_final"]})
    return qs


def _resultado(titulo, subtitulo, colunas, linhas, kpis, status_choices=()):
    return {"titulo": titulo, "subtitulo": subtitulo, "colunas": colunas, "linhas": linhas, "kpis": kpis, "status_choices": status_choices}


def _kpi(titulo, valor, icone, subtitulo):
    return criar_indicador(titulo, valor, icone, subtitulo)


def clientes(f):
    qs = Cliente.objects.annotate(qtd=Count("vendas", distinct=True), volume=Coalesce(Sum("vendas__total"), ZERO))
    if f.get("busca"):
        qs = qs.filter(Q(nome_fantasia__icontains=f["busca"]) | Q(razao_social__icontains=f["busca"]))
    qs = _periodo(qs, f, "data_cadastro__date").order_by("-volume", "nome_fantasia")
    volume = qs.aggregate(v=Coalesce(Sum("volume"), ZERO))["v"]
    linhas = [{"url": reverse("editar_cliente", args=[x.pk]), "valores": [x.nome_fantasia, x.cidade or "—", x.estado or "—", x.qtd, _moeda(x.volume), _data(x.data_cadastro)]} for x in qs]
    return _resultado("Relatório de clientes", "Recorrência, faturamento e distribuição da carteira.", ["Cliente", "Cidade", "UF", "Vendas", "Volume comprado", "Cadastro"], linhas, [_kpi("Clientes", qs.count(), "bi-people", "Carteira filtrada"), _kpi("Com compras", qs.filter(qtd__gt=0).count(), "bi-person-check", "Clientes recorrentes"), _kpi("Volume comprado", _moeda(volume), "bi-cash-stack", "Somatório histórico")])


def produtos(f, giro=False):
    qs = Produto.objects.select_related("marca").annotate(vendidas=Coalesce(Sum("itens_venda__quantidade"), Value(0)), faturamento=Coalesce(Sum("itens_venda__total"), ZERO), movimentos=Count("movimentacoes_estoque", distinct=True))
    if f.get("busca"):
        qs = qs.filter(Q(codigo__icontains=f["busca"]) | Q(modelo__icontains=f["busca"]) | Q(marca__nome__icontains=f["busca"]))
    qs = _periodo(qs, f, "data_cadastro__date").order_by("-vendidas" if giro else "-faturamento", "codigo")
    custo = sum((x.preco_custo * x.estoque_atual for x in qs), Decimal("0"))
    linhas = [{"url": reverse("produtos:ficha_produto", args=[x.pk]), "valores": [x.codigo, x.modelo, str(x.marca or "—"), x.vendidas, x.movimentos, x.estoque_atual, _moeda(x.faturamento)]} for x in qs]
    return _resultado("Giro de produtos" if giro else "Relatório de produtos", "Giro, vendas, movimentações e disponibilidade por produto.", ["Código", "Produto", "Marca", "Vendidas", "Movimentos", "Estoque", "Faturamento"], linhas, [_kpi("Produtos", qs.count(), "bi-eyeglasses", "Itens filtrados"), _kpi("Peças vendidas", sum(x.vendidas for x in qs), "bi-box-seam", "Giro acumulado"), _kpi("Custo em estoque", _moeda(custo), "bi-boxes", "Posição a custo")])


def financeiro(f, fluxo=False):
    qs = MovimentacaoFinanceira.objects.filter(
        operacao=f.get("operacao", "distribuidora")
    ).select_related("conta_financeira", "categoria")
    qs = _periodo(qs, f, "data_movimentacao")
    if f.get("busca"):
        qs = qs.filter(Q(descricao__icontains=f["busca"]) | Q(origem__icontains=f["busca"]))
    entradas = qs.filter(tipo__in=["entrada", "estorno_saida"]).aggregate(v=Coalesce(Sum("valor"), ZERO))["v"]
    saidas = qs.filter(tipo__in=["saida", "estorno_entrada"]).aggregate(v=Coalesce(Sum("valor"), ZERO))["v"]
    linhas = [{"valores": [_data(x.data_movimentacao), x.get_tipo_display(), x.descricao, str(x.conta_financeira), str(x.categoria or "—"), _moeda(x.valor)]} for x in qs.order_by("-data_movimentacao", "-pk")]
    return _resultado("Fluxo de caixa" if fluxo else "Visão financeira", "Entradas, saídas e resultado consolidado no período.", ["Data", "Tipo", "Descrição", "Conta", "Categoria", "Valor"], linhas, [_kpi("Entradas", _moeda(entradas), "bi-arrow-down-circle", "Créditos no período"), _kpi("Saídas", _moeda(saidas), "bi-arrow-up-circle", "Débitos no período"), _kpi("Resultado", _moeda(entradas - saidas), "bi-pie-chart", "Entradas menos saídas")])


def contas(f, receber):
    model = ContaReceber if receber else ContaPagar
    qs = model.objects.filter(
        operacao=f.get("operacao", "distribuidora")
    ).select_related("cliente" if receber else "fornecedor", "categoria")
    qs = _periodo(qs, f, "data_emissao")
    if f.get("busca"):
        qs = qs.filter(Q(descricao__icontains=f["busca"]) | Q(numero__icontains=f["busca"]))
    if f.get("status"):
        qs = qs.filter(status=f["status"])
    realizado_campo = "valor_recebido" if receber else "valor_pago"
    total = qs.aggregate(v=Coalesce(Sum("valor_total"), ZERO))["v"]
    realizado = qs.aggregate(v=Coalesce(Sum(realizado_campo), ZERO))["v"]
    linhas = []
    for x in qs.order_by("-data_emissao", "-numero"):
        pessoa = (x.nome_devedor or x.cliente) if receber else x.fornecedor
        rota = "financeiro:ficha_conta_receber" if receber else "financeiro:ficha_conta_pagar"
        linhas.append({"url": reverse(rota, args=[x.pk]), "valores": [x.numero, _data(x.data_emissao), str(pessoa or "—"), x.descricao, x.get_status_display(), _moeda(x.valor_total), _moeda(getattr(x, realizado_campo)), _moeda(x.saldo)]})
    titulo = "Contas a receber" if receber else "Contas a pagar"
    return _resultado(titulo, "Valores, liquidações e saldos por documento.", ["Número", "Emissão", "Pessoa", "Descrição", "Status", "Total", "Realizado", "Saldo"], linhas, [_kpi("Total", _moeda(total), "bi-cash-stack", "Valor lançado"), _kpi("Realizado", _moeda(realizado), "bi-check-circle", "Valor liquidado"), _kpi("Saldo", _moeda(total - realizado), "bi-hourglass-split", "Valor pendente")], model.STATUS_CHOICES)


def posicao_estoque(f):
    qs = Produto.objects.select_related("marca")
    if f.get("busca"):
        qs = qs.filter(Q(codigo__icontains=f["busca"]) | Q(modelo__icontains=f["busca"]))
    qs = _periodo(qs, f, "data_cadastro__date").order_by("estoque_atual", "codigo")
    custo = sum((x.preco_custo * x.estoque_atual for x in qs), Decimal("0"))
    venda = sum((x.preco_venda * x.estoque_atual for x in qs), Decimal("0"))
    linhas = [{"url": reverse("produtos:ficha_produto", args=[x.pk]), "valores": [x.codigo, x.modelo, str(x.marca or "—"), x.estoque_atual, x.estoque_minimo, "Sim" if x.estoque_atual <= x.estoque_minimo else "Não", _moeda(x.preco_custo * x.estoque_atual), _moeda(x.preco_venda * x.estoque_atual)]} for x in qs]
    return _resultado("Posição de estoque", "Saldos, mínimos e valor armazenado por produto.", ["Código", "Produto", "Marca", "Estoque", "Mínimo", "Reposição", "Valor a custo", "Valor de venda"], linhas, [_kpi("Unidades", sum(x.estoque_atual for x in qs), "bi-boxes", "Saldo físico"), _kpi("Custo armazenado", _moeda(custo), "bi-cash", "Capital em estoque"), _kpi("Potencial de venda", _moeda(venda), "bi-graph-up", "Valor a preço de venda")])


def movimentos_estoque(f):
    qs = MovimentacaoEstoque.objects.select_related("produto", "usuario")
    qs = _periodo(qs, f, "data_movimentacao__date")
    if f.get("busca"):
        qs = qs.filter(Q(produto__codigo__icontains=f["busca"]) | Q(produto__modelo__icontains=f["busca"]) | Q(origem__icontains=f["busca"]))
    if f.get("status"):
        qs = qs.filter(tipo=f["status"])
    entradas = sum(max(x.quantidade, 0) for x in qs)
    saidas = abs(sum(min(x.quantidade, 0) for x in qs))
    linhas = [{"url": reverse("produtos:ficha_produto", args=[x.produto_id]), "valores": [_data(x.data_movimentacao), x.produto.codigo, x.produto.modelo, x.get_tipo_display(), x.quantidade, x.saldo_anterior, x.saldo_atual, x.origem or "—"]} for x in qs.order_by("-data_movimentacao")]
    return _resultado("Movimentações de estoque", "Entradas, saídas, ajustes e origens no período.", ["Data", "Código", "Produto", "Tipo", "Quantidade", "Saldo anterior", "Saldo atual", "Origem"], linhas, [_kpi("Movimentações", qs.count(), "bi-arrow-left-right", "Registros filtrados"), _kpi("Entradas", entradas, "bi-box-arrow-in-down", "Quantidade positiva"), _kpi("Saídas", saidas, "bi-box-arrow-up", "Quantidade negativa")], MovimentacaoEstoque.TIPO_CHOICES)


def compras(f):
    qs = Compra.objects.select_related("fornecedor").annotate(pecas=Coalesce(Sum("itens__quantidade"), Value(0)))
    qs = _periodo(qs, f, "data_compra")
    if f.get("busca"):
        qs = qs.filter(Q(fornecedor_nome__icontains=f["busca"]) | Q(numero__icontains=f["busca"]))
    if f.get("status"):
        qs = qs.filter(status=f["status"])
    total = qs.aggregate(v=Coalesce(Sum("total"), ZERO))["v"]
    pago = qs.aggregate(v=Coalesce(Sum("valor_pago"), ZERO))["v"]
    linhas = [{"url": reverse("compras:ficha", args=[x.pk]), "valores": [x.numero, _data(x.data_compra), x.fornecedor_nome, x.get_status_display(), x.get_status_pagamento_display(), x.pecas, _moeda(x.total), _moeda(x.saldo_a_pagar)]} for x in qs.order_by("-data_compra", "-numero")]
    return _resultado("Relatório de compras", "Volume comprado, entregas, pagamentos e saldos.", ["Número", "Data", "Fornecedor", "Entrega", "Pagamento", "Peças", "Total", "Saldo"], linhas, [_kpi("Compras", qs.count(), "bi-bag-check", "Documentos filtrados"), _kpi("Volume comprado", _moeda(total), "bi-cash-stack", "Valor total"), _kpi("Saldo a pagar", _moeda(total - pago), "bi-hourglass-split", "Obrigações pendentes")], Compra.STATUS_CHOICES)


def fornecedores(f):
    qs = Fornecedor.objects.annotate(qtd=Count("compras", distinct=True), volume=Coalesce(Sum("compras__total"), ZERO))
    if f.get("busca"):
        qs = qs.filter(Q(razao_social__icontains=f["busca"]) | Q(nome_fantasia__icontains=f["busca"]) | Q(codigo__icontains=f["busca"]))
    qs = _periodo(qs, f, "criado_em__date").order_by("-volume", "razao_social")
    total = qs.aggregate(v=Coalesce(Sum("volume"), ZERO))["v"]
    linhas = [{"url": reverse("fornecedores:ficha", args=[x.pk]), "valores": [x.codigo or "—", x.nome_fantasia or x.razao_social, x.cidade or "—", x.estado or "—", x.prazo_medio_entrega or "—", x.qtd, _moeda(x.volume)]} for x in qs]
    return _resultado("Desempenho de fornecedores", "Volume, recorrência e prazo informado por fornecedor.", ["Código", "Fornecedor", "Cidade", "UF", "Prazo médio", "Compras", "Volume"], linhas, [_kpi("Fornecedores", qs.count(), "bi-building", "Base filtrada"), _kpi("Com compras", qs.filter(qtd__gt=0).count(), "bi-bag-check", "Relacionamentos ativos"), _kpi("Volume comprado", _moeda(total), "bi-cash-stack", "Somatório histórico")])


def custos(f):
    qs = ItemCompra.objects.select_related("compra", "produto", "produto__marca")
    qs = _periodo(qs, f, "compra__data_compra")
    if f.get("busca"):
        qs = qs.filter(Q(produto__codigo__icontains=f["busca"]) | Q(produto__modelo__icontains=f["busca"]) | Q(compra__fornecedor_nome__icontains=f["busca"]))
    qs = qs.order_by("-compra__data_compra", "produto__codigo")
    total = qs.aggregate(v=Coalesce(Sum("total"), ZERO))["v"]
    linhas = [{"url": reverse("compras:ficha", args=[x.compra_id]), "valores": [_data(x.compra.data_compra), x.produto.codigo, x.produto.modelo, x.compra.fornecedor_nome, x.quantidade, _moeda(x.custo_unitario), _moeda(x.produto.preco_custo), _moeda(x.total)]} for x in qs]
    return _resultado("Evolução de custos", "Histórico de aquisição comparado ao custo atual.", ["Data", "Código", "Produto", "Fornecedor", "Qtd.", "Custo adquirido", "Custo atual", "Total"], linhas, [_kpi("Aquisições", qs.count(), "bi-receipt", "Linhas de compra"), _kpi("Produtos", qs.values("produto_id").distinct().count(), "bi-eyeglasses", "Produtos distintos"), _kpi("Valor adquirido", _moeda(total), "bi-graph-up", "Custo total filtrado")])


RELATORIOS = {
    "clientes": clientes, "produtos": produtos,
    "visao-financeira": financeiro, "contas-receber": lambda f: contas(f, True),
    "contas-pagar": lambda f: contas(f, False), "fluxo-caixa": lambda f: financeiro(f, True),
    "posicao-estoque": posicao_estoque, "movimentacoes-estoque": movimentos_estoque,
    "giro-produtos": lambda f: produtos(f, True), "compras": compras,
    "fornecedores": fornecedores, "evolucao-custos": custos,
}


STATUS = {"contas-receber": ContaReceber.STATUS_CHOICES, "contas-pagar": ContaPagar.STATUS_CHOICES, "movimentacoes-estoque": MovimentacaoEstoque.TIPO_CHOICES, "compras": Compra.STATUS_CHOICES}


def obter_relatorio_analitico(slug, filtros):
    return RELATORIOS[slug](filtros)


def obter_status_relatorio(slug):
    return STATUS.get(slug, ())
