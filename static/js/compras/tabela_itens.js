document.addEventListener("DOMContentLoaded", () => {
    const campoBusca = document.getElementById(
        "busca-produto-inline"
    );
    const resultados = document.getElementById(
        "resultado-produtos-inline"
    );
    const estadoVazio = document.getElementById(
        "itens-vazio"
    );
    const wrapperTabela = document.getElementById(
        "tabela-itens-wrapper"
    );
    const corpoTabela = document.getElementById(
        "tabela-itens-body"
    );

    const resumoSubtotal = document.getElementById(
        "resumo-subtotal"
    );
    const resumoDesconto = document.getElementById(
        "resumo-desconto"
    );
    const resumoFrete = document.getElementById(
        "resumo-frete"
    );
    const resumoTotal = document.getElementById(
        "resumo-total"
    );
    const campoFrete = document.getElementById(
        "id_frete"
    );

    let controladorBusca = null;
    let temporizadorBusca = null;
    let ignorarProximoFoco = false;

    if (
        !campoBusca ||
        !resultados ||
        !estadoVazio ||
        !wrapperTabela ||
        !corpoTabela ||
        !resumoSubtotal ||
        !resumoDesconto ||
        !resumoFrete ||
        !resumoTotal
    ) {
        return;
    }

    function numero(valor) {
        const texto = String(
            valor ?? "0"
        ).trim();

        if (!texto) {
            return 0;
        }

        /*
         * Formato brasileiro:
         * 1.250,50 → 1250.50
         *
         * Formato padrão:
         * 1250.50 → 1250.50
         */
        if (texto.includes(",")) {
            return (
                Number(
                    texto
                        .replace(/\./g, "")
                        .replace(",", ".")
                ) || 0
            );
        }

        return Number(texto) || 0;
    }

    function valorDecimalParaInput(valor) {
        return numero(valor).toFixed(2);
    }

    function moeda(valor) {
        return numero(valor).toLocaleString(
            "pt-BR",
            {
                style: "currency",
                currency: "BRL",
            }
        );
    }

    function escaparHtml(valor) {
        const elemento = document.createElement(
            "div"
        );

        elemento.textContent = valor ?? "";

        return elemento.innerHTML;
    }

    function atualizarEstadoTabela() {
        if (corpoTabela.children.length === 0) {
            wrapperTabela.classList.add(
                "d-none"
            );
            estadoVazio.classList.remove(
                "d-none"
            );
        } else {
            wrapperTabela.classList.remove(
                "d-none"
            );
            estadoVazio.classList.add(
                "d-none"
            );
        }
    }

    function recalcularResumo() {
        let subtotal = 0;
        let descontoTotal = 0;

        corpoTabela
            .querySelectorAll("tr")
            .forEach((linha) => {
                const campoQuantidade =
                    linha.querySelector(
                        ".quantidade"
                    );
                const campoCusto =
                    linha.querySelector(
                        ".custo"
                    );
                const campoDesconto =
                    linha.querySelector(
                        ".desconto"
                    );
                const totalItemElemento =
                    linha.querySelector(
                        ".total-item"
                    );

                if (
                    !campoQuantidade ||
                    !campoCusto ||
                    !campoDesconto ||
                    !totalItemElemento
                ) {
                    return;
                }

                const quantidade = numero(
                    campoQuantidade.value
                );
                const custo = numero(
                    campoCusto.value
                );
                const desconto = numero(
                    campoDesconto.value
                );

                const valorBruto =
                    quantidade * custo;

                const totalItem = Math.max(
                    valorBruto - desconto,
                    0
                );

                totalItemElemento.textContent =
                    moeda(totalItem);

                subtotal += valorBruto;
                descontoTotal += desconto;
            });

        const frete = numero(
            campoFrete
                ? campoFrete.value
                : 0
        );

        const total = Math.max(
            subtotal - descontoTotal + frete,
            0
        );

        resumoSubtotal.textContent =
            moeda(subtotal);

        resumoDesconto.textContent =
            moeda(descontoTotal);

        resumoFrete.textContent =
            moeda(frete);

        resumoTotal.textContent =
            moeda(total);
    }

    function fecharResultados() {
        resultados.innerHTML = "";
    }

    function reposicionarNoCampoBusca() {
        ignorarProximoFoco = true;

        campoBusca.focus();

        window.setTimeout(() => {
            ignorarProximoFoco = false;
        }, 100);
    }

    function adicionarProduto(produto) {
        const produtoId = Number(
            produto.id
        );

        if (!produtoId) {
            return;
        }

        const produtoJaExiste =
            corpoTabela.querySelector(
                `input[name="produto_id[]"][value="${produtoId}"]`
            );

        if (produtoJaExiste) {
            const linha =
                produtoJaExiste.closest("tr");

            const campoQuantidade =
                linha.querySelector(
                    ".quantidade"
                );

            campoQuantidade.value =
                numero(
                    campoQuantidade.value
                ) + 1;

            campoBusca.value = "";
            fecharResultados();

            recalcularResumo();
            reposicionarNoCampoBusca();

            return;
        }

        const linha =
            document.createElement("tr");

        const codigo = escaparHtml(
            produto.codigo
        );

        const codigoFornecedor =
            escaparHtml(
                produto.codigo_fornecedor
            );

        const modelo = escaparHtml(
            produto.modelo
        );

        const custoInicial =
            valorDecimalParaInput(
                produto.preco_custo
            );

        linha.innerHTML = `
            <td>
                <input
                    type="hidden"
                    name="produto_id[]"
                    value="${produtoId}"
                >

                <strong>
                    ${codigo}
                </strong>

                ${
                    codigoFornecedor
                        ? `
                            <small
                                class="text-muted d-block"
                            >
                                Cód. fornecedor:
                                ${codigoFornecedor}
                            </small>
                        `
                        : ""
                }

                <span class="text-muted">
                    ${modelo}
                </span>
            </td>

            <td>
                <input
                    type="number"
                    name="quantidade[]"
                    class="form-control quantidade"
                    value="1"
                    min="1"
                >
            </td>

            <td>
                <input
                    type="number"
                    name="custo_unitario[]"
                    class="form-control custo"
                    value="${custoInicial}"
                    step="0.01"
                    min="0.01"
                >
            </td>

            <td>
                <input
                    type="number"
                    name="desconto_item[]"
                    class="form-control desconto"
                    value="0.00"
                    step="0.01"
                    min="0"
                >
            </td>

            <td class="fw-bold total-item">
                R$ 0,00
            </td>

            <td class="text-center">
                <button
                    type="button"
                    class="
                        btn
                        btn-sm
                        btn-outline-danger
                        remover-item
                    "
                    title="Remover produto"
                >
                    <i class="bi bi-trash"></i>
                </button>
            </td>
        `;

        corpoTabela.appendChild(linha);

        campoBusca.value = "";
        fecharResultados();

        atualizarEstadoTabela();
        recalcularResumo();
        reposicionarNoCampoBusca();
    }

    function renderizarProdutos(produtos) {
        fecharResultados();

        if (!produtos.length) {
            resultados.innerHTML = `
                <div class="produto-resultado-vazio">
                    Nenhum produto ativo encontrado.
                </div>
            `;

            return;
        }

        produtos.forEach((produto) => {
            const item =
                document.createElement(
                    "button"
                );

            item.type = "button";
            item.className =
                "produto-resultado-item";

            const codigo = escaparHtml(
                produto.codigo
            );

            const codigoFornecedor =
                escaparHtml(
                    produto.codigo_fornecedor
                );

            const modelo = escaparHtml(
                produto.modelo
            );

            const marca = escaparHtml(
                produto.marca
            );

            const colecao = escaparHtml(
                produto.colecao
            );

            const genero = escaparHtml(
                produto.genero
            );

            const tipoArmacao =
                escaparHtml(
                    produto.tipo_armacao
                );

            const cores = escaparHtml(
                produto.cores_disponiveis
            );

            const estoque = numero(
                produto.estoque_atual
            );

            const precoCusto = numero(
                produto.preco_custo
            );

            const ultimoCustoCompra =
                produto.ultimo_custo_compra
                    ? numero(
                        produto.ultimo_custo_compra
                    )
                    : null;

            item.innerHTML = `
                <div
                    class="
                        produto-resultado-item__principal
                        d-flex
                        justify-content-between
                        align-items-start
                        gap-3
                    "
                >
                    <div>
                        <div>
                            <strong>
                                ${codigo}
                            </strong>

                            ${
                                codigoFornecedor
                                    ? `
                                        <span
                                            class="text-muted"
                                        >
                                            • Cód. fornecedor:
                                            ${codigoFornecedor}
                                        </span>
                                    `
                                    : ""
                            }
                        </div>

                        <div>
                            <span>
                                ${modelo}
                            </span>

                            ${
                                marca
                                    ? `
                                        <span
                                            class="text-muted"
                                        >
                                            • ${marca}
                                        </span>
                                    `
                                    : ""
                            }

                            ${
                                colecao
                                    ? `
                                        <span
                                            class="text-muted"
                                        >
                                            • ${colecao}
                                        </span>
                                    `
                                    : ""
                            }
                        </div>

                        <small
                            class="text-muted d-block"
                        >
                            ${
                                genero
                                    ? `${genero}`
                                    : ""
                            }

                            ${
                                tipoArmacao
                                    ? `${genero ? " • " : ""}${tipoArmacao}`
                                    : ""
                            }

                            ${
                                cores
                                    ? `${
                                        genero ||
                                        tipoArmacao
                                            ? " • "
                                            : ""
                                    }Cores: ${cores}`
                                    : ""
                            }
                        </small>
                    </div>

                    <div
                        class="
                            text-end
                            flex-shrink-0
                        "
                    >
                        <div>
                            Estoque:
                            <strong>
                                ${estoque}
                            </strong>
                        </div>

                        <small class="text-muted">
                            Última compra:
                            ${
                                ultimoCustoCompra !== null
                                    ? moeda(ultimoCustoCompra)
                                    : "—"
                            }
                        </small>
                    </div>
                </div>
            `;

            item.addEventListener(
                "click",
                () => {
                    adicionarProduto(
                        produto
                    );
                }
            );

            resultados.appendChild(item);
        });
    }

    async function buscarProdutos() {
        const termo =
            campoBusca.value.trim();

        if (controladorBusca) {
            controladorBusca.abort();
        }

        controladorBusca =
            new AbortController();

        resultados.innerHTML = `
            <div class="produto-resultado-vazio">
                Carregando produtos...
            </div>
        `;

        try {
            const response = await fetch(
                `/compras/api/produtos/?q=${
                    encodeURIComponent(termo)
                }`,
                {
                    signal:
                        controladorBusca.signal,
                    headers: {
                        Accept:
                            "application/json",
                    },
                }
            );

            if (!response.ok) {
                throw new Error(
                    "Não foi possível carregar os produtos."
                );
            }

            const data =
                await response.json();

            renderizarProdutos(
                Array.isArray(
                    data.resultados
                )
                    ? data.resultados
                    : []
            );
        } catch (erro) {
            if (
                erro.name ===
                "AbortError"
            ) {
                return;
            }

            resultados.innerHTML = `
                <div class="produto-resultado-vazio">
                    Não foi possível carregar os
                    produtos agora.
                </div>
            `;

            console.error(
                "Erro ao buscar produtos:",
                erro
            );
        }
    }

    campoBusca.addEventListener(
        "focus",
        () => {
            if (ignorarProximoFoco) {
                return;
            }

            buscarProdutos();
        }
    );

    campoBusca.addEventListener(
        "click",
        () => {
            if (
                ignorarProximoFoco ||
                resultados.children.length > 0
            ) {
                return;
            }

            buscarProdutos();
        }
    );

    campoBusca.addEventListener(
        "input",
        () => {
            window.clearTimeout(
                temporizadorBusca
            );

            temporizadorBusca =
                window.setTimeout(
                    buscarProdutos,
                    250
                );
        }
    );

    campoBusca.addEventListener(
        "keydown",
        (event) => {
            if (event.key === "Escape") {
                fecharResultados();
                campoBusca.blur();
            }
        }
    );

    document.addEventListener(
        "click",
        (event) => {
            const clicouNaBusca =
                campoBusca.contains(
                    event.target
                ) ||
                resultados.contains(
                    event.target
                );

            if (!clicouNaBusca) {
                fecharResultados();
            }
        }
    );

    corpoTabela.addEventListener(
        "input",
        (event) => {
            if (
                event.target.classList.contains(
                    "quantidade"
                ) ||
                event.target.classList.contains(
                    "custo"
                ) ||
                event.target.classList.contains(
                    "desconto"
                )
            ) {
                recalcularResumo();
            }
        }
    );

    corpoTabela.addEventListener(
        "click",
        (event) => {
            const botao =
                event.target.closest(
                    ".remover-item"
                );

            if (!botao) {
                return;
            }

            const linha =
                botao.closest("tr");

            if (linha) {
                linha.remove();
            }

            atualizarEstadoTabela();
            recalcularResumo();
        }
    );

    if (campoFrete) {
        campoFrete.addEventListener(
            "input",
            recalcularResumo
        );
    }

    atualizarEstadoTabela();
    recalcularResumo();
});