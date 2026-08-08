from django.core.exceptions import ValidationError
from django.db import transaction

from catalogo.models import (
    Colecao,
    Genero,
    Marca,
    TipoArmacao,
)
from estoque.services import registrar_entrada_estoque
from produtos.models import Produto, VariacaoCor

from .simulacao import simular_importacao_produtos


class ErroImportacaoProdutos(ValidationError):
    pass


def _buscar_ou_criar_referencia(modelo, nome):
    nome = (nome or "").strip()

    if not nome:
        return None

    existente = modelo.objects.filter(
        nome__iexact=nome
    ).first()

    if existente:
        return existente

    return modelo.objects.create(
        nome=nome,
    )


def _chave_produto(linha):
    codigo_fornecedor = (
        linha.get("codigo_fornecedor")
        or ""
    ).strip().upper()

    if codigo_fornecedor:
        return (
            "codigo_fornecedor",
            codigo_fornecedor,
        )

    codigo = (
        linha.get("codigo")
        or ""
    ).strip().upper()

    if codigo:
        return (
            "codigo",
            codigo,
        )

    return (
        "modelo",
        (linha.get("modelo") or "")
        .strip()
        .upper(),
    )


def _agrupar_linhas(linhas):
    grupos = {}

    for linha in linhas:
        chave = _chave_produto(linha)

        grupos.setdefault(
            chave,
            [],
        ).append(linha)

    return grupos


def _validar_produto_existente(linha):
    codigo = (
        linha.get("codigo")
        or ""
    ).strip()

    codigo_fornecedor = (
        linha.get("codigo_fornecedor")
        or ""
    ).strip()

    if (
        codigo
        and Produto.objects.filter(
            codigo__iexact=codigo
        ).exists()
    ):
        raise ErroImportacaoProdutos(
            f"O Código ERP {codigo!r} já está cadastrado."
        )

    if (
        codigo_fornecedor
        and Produto.objects.filter(
            codigo_fornecedor__iexact=codigo_fornecedor
        ).exists()
    ):
        raise ErroImportacaoProdutos(
            "O Código do fornecedor "
            f"{codigo_fornecedor!r} já está cadastrado."
        )


def _validar_consistencia_grupo(linhas):
    primeira = linhas[0]

    campos = (
        "categoria_comercial",
        "codigo",
        "codigo_fornecedor",
        "modelo",
        "marca",
        "colecao",
        "genero",
        "tipo_armacao",
        "custo",
        "venda",
        "estoque_minimo",
    )

    for linha in linhas[1:]:
        for campo in campos:
            if linha.get(campo) != primeira.get(campo):
                raise ErroImportacaoProdutos(
                    f"Linhas {primeira['linha']} e "
                    f"{linha['linha']}: o mesmo produto "
                    f"possui valores diferentes em "
                    f"{campo!r}."
                )


def _criar_produto_base(linha):
    categoria = linha["categoria_comercial"]

    marca = _buscar_ou_criar_referencia(
        Marca,
        linha.get("marca"),
    )

    colecao = _buscar_ou_criar_referencia(
        Colecao,
        linha.get("colecao"),
    )

    genero = None
    tipo_armacao = None

    if categoria == "armacao":
        genero = _buscar_ou_criar_referencia(
            Genero,
            linha.get("genero"),
        )

        tipo_armacao = _buscar_ou_criar_referencia(
            TipoArmacao,
            linha.get("tipo_armacao"),
        )

    produto = Produto.objects.create(
        categoria_comercial=categoria,
        codigo=linha.get("codigo") or None,
        codigo_fornecedor=(
            linha.get("codigo_fornecedor")
            or None
        ),
        modelo=linha.get("modelo") or "",
        marca=marca,
        colecao=colecao,
        genero=genero,
        tipo_armacao=tipo_armacao,
        preco_custo=linha["custo"],
        preco_venda=linha["venda"],
        estoque_atual=0,
        estoque_minimo=linha["estoque_minimo"],
        observacoes=(
            linha.get("observacoes")
            or ""
        ),
        ativo=True,
    )

    return produto


def _criar_estoque_simples(
    *,
    produto,
    linha,
    usuario,
):
    quantidade = linha["estoque"]

    if quantidade <= 0:
        return

    registrar_entrada_estoque(
        produto=produto,
        quantidade=quantidade,
        usuario=usuario,
        origem="Importação Inicial",
        local="Estoque Principal",
        observacao=(
            "Estoque inicial cadastrado "
            "pela importação de produtos."
        ),
    )


def _criar_variacoes(
    *,
    produto,
    linhas,
    usuario,
):
    total = 0

    for linha in linhas:
        if linha["sem_variacao"]:
            continue

        variacao = VariacaoCor.objects.create(
            produto=produto,
            nome=linha["cor_variacao"],
            codigo=linha["codigo_variacao"],
            estoque=0,
        )

        quantidade = linha["estoque"]

        if quantidade > 0:
            registrar_entrada_estoque(
                produto=produto,
                variacao_cor=variacao,
                quantidade=quantidade,
                usuario=usuario,
                origem="Importação Inicial",
                local="Estoque Principal",
                observacao=(
                    "Estoque inicial da variação "
                    "cadastrado pela importação."
                ),
            )

        total += 1

    return total


@transaction.atomic
def importar_produtos(
    *,
    linhas,
    usuario=None,
):
    simulacao = simular_importacao_produtos(
        linhas
    )

    if simulacao["erros"]:
        raise ErroImportacaoProdutos(
            simulacao["erros"]
        )

    grupos = _agrupar_linhas(linhas)

    produtos_criados = 0
    variacoes_criadas = 0
    acessorios_criados = 0
    movimentacoes_iniciais = 0

    for linhas_produto in grupos.values():
        _validar_consistencia_grupo(
            linhas_produto
        )

        primeira = linhas_produto[0]

        _validar_produto_existente(
            primeira
        )

        produto = _criar_produto_base(
            primeira
        )

        produtos_criados += 1

        categoria = primeira[
            "categoria_comercial"
        ]

        if categoria == "acessorio":
            acessorios_criados += 1

            if primeira["estoque"] > 0:
                movimentacoes_iniciais += 1

            _criar_estoque_simples(
                produto=produto,
                linha=primeira,
                usuario=usuario,
            )

            continue

        if primeira["sem_variacao"]:
            if primeira["estoque"] > 0:
                movimentacoes_iniciais += 1

            _criar_estoque_simples(
                produto=produto,
                linha=primeira,
                usuario=usuario,
            )

            continue

        variacoes_criadas += (
            _criar_variacoes(
                produto=produto,
                linhas=linhas_produto,
                usuario=usuario,
            )
        )

        movimentacoes_iniciais += sum(
            1
            for linha in linhas_produto
            if linha["estoque"] > 0
        )

    return {
        "produtos_criados": produtos_criados,
        "variacoes_criadas": variacoes_criadas,
        "acessorios_criados": acessorios_criados,
        "movimentacoes_iniciais": (
            movimentacoes_iniciais
        ),
    }