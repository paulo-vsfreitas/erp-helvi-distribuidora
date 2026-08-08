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

    modelo = (
        linha.get("modelo")
        or ""
    ).strip().upper()

    return (
        "modelo",
        modelo,
    )


def simular_importacao_produtos(linhas):
    produtos = {}
    erros = []

    total_variacoes = 0
    total_acessorios = 0

    for linha in linhas:
        chave = _chave_produto(
            linha
        )

        if not chave[1]:
            continue

        produto = produtos.setdefault(
            chave,
            {
                "chave": chave,
                "categoria_comercial": (
                    linha["categoria_comercial"]
                ),
                "codigo_fornecedor": (
                    linha["codigo_fornecedor"]
                ),
                "codigo": linha["codigo"],
                "modelo": linha["modelo"],
                "linhas": [],
                "variacoes": [],
            },
        )

        produto["linhas"].append(
            linha["linha"]
        )

        if (
            produto["categoria_comercial"]
            != linha["categoria_comercial"]
        ):
            erros.append(
                f"Linha {linha['linha']}: o mesmo produto "
                "aparece com categorias comerciais diferentes."
            )

        if (
            linha["categoria_comercial"]
            == "acessorio"
        ):
            continue

        if linha["sem_variacao"]:
            continue

        codigo_variacao = (
            linha["codigo_variacao"]
            or ""
        ).strip().upper()

        codigos_existentes = {
            item["codigo"]
            for item in produto["variacoes"]
        }

        if codigo_variacao in codigos_existentes:
            erros.append(
                f"Linha {linha['linha']}: Código da "
                f"Variação {codigo_variacao!r} duplicado "
                "dentro do mesmo produto."
            )
            continue

        produto["variacoes"].append(
            {
                "linha": linha["linha"],
                "nome": linha["cor_variacao"],
                "codigo": codigo_variacao,
                "estoque": linha["estoque"],
            }
        )

        total_variacoes += 1

    for produto in produtos.values():
        if (
            produto["categoria_comercial"]
            == "acessorio"
        ):
            total_acessorios += 1

    return {
        "total_linhas": len(linhas),
        "total_produtos": len(produtos),
        "total_variacoes": total_variacoes,
        "total_acessorios": total_acessorios,
        "produtos": list(
            produtos.values()
        ),
        "erros": erros,
    }