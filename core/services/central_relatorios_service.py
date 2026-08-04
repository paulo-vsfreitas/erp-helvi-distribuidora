from django.urls import reverse


def _criar_relatorio(
    titulo,
    descricao,
    icone,
    nome_url=None,
    slug=None,
    acao="Abrir relatório",
):
    return {
        "titulo": titulo,
        "descricao": descricao,
        "icone": icone,
        "url": (
            reverse(nome_url)
            if nome_url
            else reverse("relatorio_analitico", kwargs={"slug": slug})
        ),
        "acao": acao,
    }


def _montar_secoes():
    return [
        {
            "titulo": "Comercial",
            "descricao": (
                "Indicadores de vendas, clientes, produtos e desempenho "
                "da operação comercial."
            ),
            "icone": "bi-graph-up-arrow",
            "relatorios": [
                _criar_relatorio(
                    titulo="Relatório de Vendas",
                    descricao=(
                        "Faturamento, peças vendidas, recebimentos "
                        "e desempenho comercial."
                    ),
                    icone="bi-bar-chart-line",
                    nome_url="vendas:relatorio",
                ),
                _criar_relatorio(
                    titulo="Relatório de Clientes",
                    descricao=(
                        "Recorrência, volume comprado e desempenho "
                        "da carteira de clientes."
                    ),
                    icone="bi-people",
                    slug="clientes",
                    acao="Abrir relatório",
                ),
                _criar_relatorio(
                    titulo="Relatório de Produtos",
                    descricao=(
                        "Produtos mais vendidos e desempenho por marca, "
                        "coleção e categoria."
                    ),
                    icone="bi-eyeglasses",
                    slug="produtos",
                    acao="Abrir relatório",
                ),
            ],
        },
        {
            "titulo": "Financeiro",
            "descricao": (
                "Receitas, despesas, saldos, vencimentos "
                "e fluxo financeiro."
            ),
            "icone": "bi-cash-coin",
            "relatorios": [
                _criar_relatorio(
                    titulo="Visão Financeira",
                    descricao=(
                        "Resumo consolidado das receitas, despesas "
                        "e resultado do período."
                    ),
                    icone="bi-pie-chart",
                    slug="visao-financeira",
                    acao="Abrir relatório",
                ),
                _criar_relatorio(
                    titulo="Contas a Receber",
                    descricao=(
                        "Valores recebidos, pendentes, vencidos "
                        "e próximos vencimentos."
                    ),
                    icone="bi-arrow-down-circle",
                    slug="contas-receber",
                    acao="Abrir relatório",
                ),
                _criar_relatorio(
                    titulo="Contas a Pagar",
                    descricao=(
                        "Pagamentos realizados, obrigações pendentes "
                        "e vencimentos."
                    ),
                    icone="bi-arrow-up-circle",
                    slug="contas-pagar",
                    acao="Abrir relatório",
                ),
                _criar_relatorio(
                    titulo="Fluxo de Caixa",
                    descricao=(
                        "Entradas, saídas e evolução financeira "
                        "da empresa."
                    ),
                    icone="bi-activity",
                    slug="fluxo-caixa",
                    acao="Abrir relatório",
                ),
            ],
        },
        {
            "titulo": "Estoque",
            "descricao": (
                "Saldos, movimentações, custos e disponibilidade "
                "dos produtos."
            ),
            "icone": "bi-box-seam",
            "relatorios": [
                _criar_relatorio(
                    titulo="Posição de Estoque",
                    descricao=(
                        "Quantidade atual, estoque mínimo "
                        "e valor financeiro armazenado."
                    ),
                    icone="bi-boxes",
                    slug="posicao-estoque",
                    acao="Abrir relatório",
                ),
                _criar_relatorio(
                    titulo="Movimentações de Estoque",
                    descricao=(
                        "Entradas, saídas, ajustes, compras "
                        "e vendas no período."
                    ),
                    icone="bi-arrow-left-right",
                    slug="movimentacoes-estoque",
                    acao="Abrir relatório",
                ),
                _criar_relatorio(
                    titulo="Giro de Produtos",
                    descricao=(
                        "Produtos com maior giro, baixo giro "
                        "ou sem movimentação."
                    ),
                    icone="bi-arrow-repeat",
                    slug="giro-produtos",
                    acao="Abrir relatório",
                ),
            ],
        },
        {
            "titulo": "Compras",
            "descricao": (
                "Compras, fornecedores, recebimentos "
                "e evolução dos custos."
            ),
            "icone": "bi-cart-check",
            "relatorios": [
                _criar_relatorio(
                    titulo="Relatório de Compras",
                    descricao=(
                        "Volume comprado, valores, pagamentos "
                        "e situação das entregas."
                    ),
                    icone="bi-bag-check",
                    slug="compras",
                    acao="Abrir relatório",
                ),
                _criar_relatorio(
                    titulo="Desempenho de Fornecedores",
                    descricao=(
                        "Volume de compras, recorrência "
                        "e relacionamento com fornecedores."
                    ),
                    icone="bi-building",
                    slug="fornecedores",
                    acao="Abrir relatório",
                ),
                _criar_relatorio(
                    titulo="Evolução de Custos",
                    descricao=(
                        "Custos de aquisição e variações "
                        "nos preços dos produtos."
                    ),
                    icone="bi-graph-up",
                    slug="evolucao-custos",
                    acao="Abrir relatório",
                ),
            ],
        },
    ]


def montar_central_relatorios():
    """
    Monta a estrutura visual e os indicadores da Central de Relatórios.

    Nenhuma regra de negócio de vendas, financeiro, estoque ou compras
    deve ser calculada neste service.
    """
    secoes = _montar_secoes()

    total_relatorios = sum(
        len(secao["relatorios"])
        for secao in secoes
    )

    return {
        "secoes": secoes,
        "indicadores": {
            "total_modulos": len(secoes),
            "total_relatorios": total_relatorios,
        },
    }
