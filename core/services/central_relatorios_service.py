from django.urls import NoReverseMatch, reverse


STATUS_DISPONIVEL = "disponivel"
STATUS_DESENVOLVIMENTO = "desenvolvimento"
STATUS_PLANEJADO = "planejado"


def _resolver_url(nome_url):
    """
    Tenta resolver uma rota do ERP.

    Caso a rota ainda não exista, retorna None para que a Central continue
    funcionando sem gerar erro.
    """
    if not nome_url:
        return None

    try:
        return reverse(nome_url)
    except NoReverseMatch:
        return None


def _criar_relatorio(
    titulo,
    descricao,
    icone,
    nome_url=None,
    status=STATUS_DESENVOLVIMENTO,
):
    url = _resolver_url(nome_url)

    if url:
        status = STATUS_DISPONIVEL

    return {
        "titulo": titulo,
        "descricao": descricao,
        "icone": icone,
        "url": url,
        "status": status,
        "disponivel": bool(url),
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
                ),
                _criar_relatorio(
                    titulo="Relatório de Produtos",
                    descricao=(
                        "Produtos mais vendidos e desempenho por marca, "
                        "coleção e categoria."
                    ),
                    icone="bi-eyeglasses",
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
                ),
                _criar_relatorio(
                    titulo="Contas a Receber",
                    descricao=(
                        "Valores recebidos, pendentes, vencidos "
                        "e próximos vencimentos."
                    ),
                    icone="bi-arrow-down-circle",
                ),
                _criar_relatorio(
                    titulo="Contas a Pagar",
                    descricao=(
                        "Pagamentos realizados, obrigações pendentes "
                        "e vencimentos."
                    ),
                    icone="bi-arrow-up-circle",
                ),
                _criar_relatorio(
                    titulo="Fluxo de Caixa",
                    descricao=(
                        "Entradas, saídas e evolução financeira "
                        "da empresa."
                    ),
                    icone="bi-activity",
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
                ),
                _criar_relatorio(
                    titulo="Movimentações de Estoque",
                    descricao=(
                        "Entradas, saídas, ajustes, compras "
                        "e vendas no período."
                    ),
                    icone="bi-arrow-left-right",
                ),
                _criar_relatorio(
                    titulo="Giro de Produtos",
                    descricao=(
                        "Produtos com maior giro, baixo giro "
                        "ou sem movimentação."
                    ),
                    icone="bi-arrow-repeat",
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
                ),
                _criar_relatorio(
                    titulo="Desempenho de Fornecedores",
                    descricao=(
                        "Volume de compras, recorrência "
                        "e relacionamento com fornecedores."
                    ),
                    icone="bi-building",
                ),
                _criar_relatorio(
                    titulo="Evolução de Custos",
                    descricao=(
                        "Custos de aquisição e variações "
                        "nos preços dos produtos."
                    ),
                    icone="bi-graph-up",
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

    total_disponiveis = sum(
        1
        for secao in secoes
        for relatorio in secao["relatorios"]
        if relatorio["disponivel"]
    )

    total_desenvolvimento = sum(
        1
        for secao in secoes
        for relatorio in secao["relatorios"]
        if relatorio["status"] == STATUS_DESENVOLVIMENTO
    )

    return {
        "secoes": secoes,
        "indicadores": {
            "total_modulos": len(secoes),
            "total_relatorios": total_relatorios,
            "total_disponiveis": total_disponiveis,
            "total_desenvolvimento": total_desenvolvimento,
        },
    }