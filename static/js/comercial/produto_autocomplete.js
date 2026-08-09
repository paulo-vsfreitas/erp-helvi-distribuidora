(() => {
    "use strict";

    class ProdutoAutocomplete {
        constructor() {
            this.inputBusca = document.getElementById("produto-search");
            this.inputId = document.getElementById("produto-id");
            this.resultados = document.getElementById("produto-resultados");

            this.produtoSelecionado = null;
            this.timeoutBusca = null;
            this.controladorBusca = null;

            this.produtosAtuais = [];
            this.indiceAtivo = -1;

            if (!this.inputBusca || !this.inputId || !this.resultados) {
                return;
            }

            this.configurarAcessibilidade();
            this.registrarEventos();
        }

        configurarAcessibilidade() {
            this.inputBusca.setAttribute("role", "combobox");
            this.inputBusca.setAttribute("aria-autocomplete", "list");
            this.inputBusca.setAttribute("aria-expanded", "false");
            this.inputBusca.setAttribute(
                "aria-controls",
                "produto-resultados"
            );

            this.resultados.setAttribute("role", "listbox");
        }

        registrarEventos() {
            this.inputBusca.addEventListener("focus", () => {
                const termo = this.inputBusca.value.trim();

                if (!this.produtoSelecionado) {
                    this.buscarProdutos(termo);
                }
            });

            this.inputBusca.addEventListener("click", () => {
                if (!this.resultados.classList.contains("d-none")) {
                    return;
                }

                const termo = this.inputBusca.value.trim();

                if (!this.produtoSelecionado) {
                    this.buscarProdutos(termo);
                }
            });

            this.inputBusca.addEventListener("input", () => {
                this.limparSelecao(false);

                window.clearTimeout(this.timeoutBusca);

                const termo = this.inputBusca.value.trim();

                if (termo.length === 1) {
                    this.produtosAtuais = [];
                    this.indiceAtivo = -1;
                    this.ocultarResultados();
                    return;
                }

                this.timeoutBusca = window.setTimeout(
                    () => this.buscarProdutos(termo),
                    250
                );
            });

            this.inputBusca.addEventListener("keydown", (event) => {
                this.tratarTeclado(event);
            });

            document.addEventListener("click", (event) => {
                if (
                    !this.inputBusca.contains(event.target)
                    && !this.resultados.contains(event.target)
                ) {
                    this.ocultarResultados();
                }
            });
        }

        tratarTeclado(event) {
            const resultadosVisiveis =
                !this.resultados.classList.contains("d-none");

            if (event.key === "Escape") {
                this.ocultarResultados();
                return;
            }

            if (event.key === "ArrowDown") {
                event.preventDefault();

                if (!resultadosVisiveis) {
                    this.buscarProdutos(
                        this.inputBusca.value.trim()
                    );
                    return;
                }

                this.moverSelecao(1);
                return;
            }

            if (event.key === "ArrowUp") {
                event.preventDefault();

                if (!resultadosVisiveis) {
                    return;
                }

                this.moverSelecao(-1);
                return;
            }

            if (
                event.key === "Enter"
                && resultadosVisiveis
                && this.indiceAtivo >= 0
            ) {
                event.preventDefault();

                const produto =
                    this.produtosAtuais[this.indiceAtivo];

                if (produto) {
                    const existente =
                        window.HelviComercial
                            ?.itensOrcamento
                            ?.obterItem(produto.id);

                    if (existente) {
                        window.HelviComercial
                            ?.itensOrcamento
                            ?.destacarProdutoExistente(produto.id);

                        return;
                    }

                    this.selecionarProduto(produto);
                }
            }
        }

        moverSelecao(direcao) {
            if (!this.produtosAtuais.length) {
                return;
            }

            this.indiceAtivo += direcao;

            if (this.indiceAtivo >= this.produtosAtuais.length) {
                this.indiceAtivo = 0;
            }

            if (this.indiceAtivo < 0) {
                this.indiceAtivo =
                    this.produtosAtuais.length - 1;
            }

            this.atualizarDestaque();
        }

        atualizarDestaque() {
            const itens = this.resultados.querySelectorAll(
                ".autocomplete-item"
            );

            itens.forEach((item, indice) => {
                const ativo = indice === this.indiceAtivo;

                item.classList.toggle(
                    "autocomplete-item-active",
                    ativo
                );

                item.setAttribute(
                    "aria-selected",
                    ativo ? "true" : "false"
                );

                if (ativo) {
                    this.inputBusca.setAttribute(
                        "aria-activedescendant",
                        item.id
                    );

                    item.scrollIntoView({
                        block: "nearest",
                    });
                }
            });
        }

        async buscarProdutos(termo = "") {
            if (this.controladorBusca) {
                this.controladorBusca.abort();
            }

            this.controladorBusca = new AbortController();

            try {
                const url = new URL(
                    "/comercial/api/produtos/",
                    window.location.origin
                );

                url.searchParams.set("q", termo);

                const resposta = await fetch(url, {
                    method: "GET",
                    headers: {
                        Accept: "application/json",
                    },
                    signal: this.controladorBusca.signal,
                });

                if (!resposta.ok) {
                    throw new Error(
                        "Não foi possível buscar os produtos."
                    );
                }

                const dados = await resposta.json();

                this.renderizarResultados(
                    dados.resultados || []
                );
            } catch (erro) {
                if (erro.name !== "AbortError") {
                    console.error(erro);
                    this.renderizarErro();
                }
            }
        }

        renderizarResultados(produtos) {
            this.resultados.innerHTML = "";
            this.produtosAtuais = produtos;
            this.indiceAtivo = -1;

            if (!produtos.length) {
                this.resultados.innerHTML = `
                    <div class="autocomplete-empty">
                        <i class="bi bi-search"></i>

                        <span>
                            Nenhum produto ativo encontrado.
                        </span>
                    </div>
                `;

                this.exibirResultados();
                return;
            }

            produtos.forEach((produto, indice) => {
                const item = document.createElement("div");

                const gerenciadorItens =
                    window.HelviComercial?.itensOrcamento;

                item.id = `produto-opcao-${indice}`;
                item.className = "autocomplete-item";
                item.setAttribute("role", "option");
                item.setAttribute("aria-selected", "false");

                /*
                 * O código ERP pode estar vazio.
                 * Nesse caso, usamos o código do fornecedor
                 * como identificação principal do produto.
                 */
                const codigoErp = this.escaparHtml(
                    produto.codigo || ""
                );

                const codigoFornecedor = this.escaparHtml(
                    produto.codigo_fornecedor || ""
                );

                const codigoPrincipal =
                    codigoErp || codigoFornecedor;

                const modelo = this.escaparHtml(
                    produto.modelo || ""
                );

                const identificacao =
                    [
                        codigoPrincipal,
                        modelo,
                    ]
                    .filter(Boolean)
                    .join(" — ");

                const marca = this.escaparHtml(
                    produto.marca || "Marca não informada"
                );

                const colecao = this.escaparHtml(
                    produto.colecao || ""
                );

                const estoque = Number(
                    produto.estoque_atual || 0
                );

                const preco = this.formatarMoeda(
                    produto.preco_venda || 0
                );

                const variacoes = produto.variacoes || [];

                item.innerHTML = `
                    <div class="cliente-resultado-icon">
                        <i class="bi bi-box-seam"></i>
                    </div>

                    <div class="cliente-resultado-conteudo">

                        <div class="autocomplete-item-header">

                            <strong>
                                ${identificacao || "Produto sem identificação"}
                            </strong>

                            <div class="produto-resultado-direita">
                                <strong>
                                    ${preco}
                                </strong>
                            </div>

                        </div>

                        ${
                            codigoFornecedor
                                ? `
                                    <div class="produto-resultado-codigo-fornecedor">
                                        <i class="bi bi-upc-scan"></i>
                                        <span>
                                            Cód. fornecedor:
                                            <strong>${codigoFornecedor}</strong>
                                        </span>
                                    </div>
                                `
                                : ""
                        }

                        <div class="cliente-resultado-dados">

                            <span>
                                <i class="bi bi-tag"></i>
                                ${marca}
                            </span>

                            ${
                                colecao
                                    ? `
                                        <span>
                                            <i class="bi bi-collection"></i>
                                            ${colecao}
                                        </span>
                                    `
                                    : ""
                            }

                            <span>
                                <i class="bi bi-boxes"></i>
                                Estoque: ${estoque}
                            </span>

                        </div>

                        <div
                            class="produto-resultado-cores d-flex flex-wrap gap-2 mt-2"
                        ></div>

                    </div>
                `;

                const cores = item.querySelector(
                    ".produto-resultado-cores"
                );

                const opcoes = variacoes.length
                    ? variacoes
                    : [
                        {
                            id: null,
                            nome: "Sem variação",
                            codigo: "",
                            estoque,
                        },
                    ];

                opcoes.forEach((cor) => {
                    const existente =
                        gerenciadorItens?.obterItem(
                            produto.id,
                            cor.id
                        );

                    const botao =
                        document.createElement("button");

                    botao.type = "button";

                    botao.className = existente
                        ? "btn btn-sm btn-outline-secondary"
                        : "btn btn-sm btn-outline-primary";

                    botao.disabled = Boolean(existente);

                    botao.textContent =
                        `${cor.nome}`
                        + `${cor.codigo ? ` (${cor.codigo})` : ""}`
                        + ` · estoque ${cor.estoque}`;

                    botao.title = existente
                        ? "Esta cor já foi adicionada"
                        : "Adicionar esta opção";

                    botao.addEventListener("click", () => {
                        if (existente) {
                            return;
                        }

                        this.selecionarProduto(
                            produto,
                            cor.id
                        );

                        document
                            .getElementById(
                                "btn-adicionar-produto"
                            )
                            ?.click();
                    });

                    cores.appendChild(botao);
                });

                item.addEventListener("mouseenter", () => {
                    this.indiceAtivo = indice;
                    this.atualizarDestaque();
                });

                this.resultados.appendChild(item);
            });

            this.exibirResultados();
        }

        selecionarProduto(produto, variacaoCorId = null) {
            this.produtoSelecionado = {
                ...produto,
                variacao_cor_id:
                    Number(variacaoCorId || 0) || null,
            };

            this.inputId.value = produto.id;

            /*
             * Mantém a mesma identificação utilizada
             * na lista de resultados.
             */
            const codigoPrincipal =
                produto.codigo
                || produto.codigo_fornecedor
                || "";

            const modelo =
                produto.modelo || "";

            this.inputBusca.value =
                [
                    codigoPrincipal,
                    modelo,
                ]
                .filter(Boolean)
                .join(" — ");

            this.ocultarResultados();

            this.inputBusca.dispatchEvent(
                new CustomEvent("produto:selecionado", {
                    bubbles: true,
                    detail: this.produtoSelecionado,
                })
            );
        }

        obterProdutoSelecionado() {
            return this.produtoSelecionado;
        }

        limparSelecao(limparBusca = true) {
            this.produtoSelecionado = null;
            this.inputId.value = "";

            if (limparBusca) {
                this.inputBusca.value = "";
            }

            this.ocultarResultados();
        }

        focar() {
            this.inputBusca.focus();
        }

        renderizarErro() {
            this.produtosAtuais = [];
            this.indiceAtivo = -1;

            this.resultados.innerHTML = `
                <div class="autocomplete-empty">
                    <i class="bi bi-exclamation-circle"></i>

                    <span>
                        Não foi possível realizar a busca.
                    </span>
                </div>
            `;

            this.exibirResultados();
        }

        exibirResultados() {
            this.resultados.classList.remove("d-none");

            this.inputBusca.setAttribute(
                "aria-expanded",
                "true"
            );
        }

        ocultarResultados() {
            this.resultados.classList.add("d-none");

            this.inputBusca.setAttribute(
                "aria-expanded",
                "false"
            );

            this.inputBusca.removeAttribute(
                "aria-activedescendant"
            );

            this.indiceAtivo = -1;
        }

        formatarMoeda(valor) {
            return Number(valor || 0).toLocaleString(
                "pt-BR",
                {
                    style: "currency",
                    currency: "BRL",
                }
            );
        }

        escaparHtml(valor) {
            const elemento =
                document.createElement("div");

            elemento.textContent =
                valor ?? "";

            return elemento.innerHTML;
        }
    }

    document.addEventListener(
        "DOMContentLoaded",
        () => {
            window.HelviComercial =
                window.HelviComercial || {};

            window.HelviComercial.produtoAutocomplete =
                new ProdutoAutocomplete();
        }
    );
})();