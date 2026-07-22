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

            if (!this.inputBusca || !this.inputId || !this.resultados) {
                return;
            }

            this.registrarEventos();
        }

        registrarEventos() {
            this.inputBusca.addEventListener("input", () => {
                this.limparSelecao(false);

                window.clearTimeout(this.timeoutBusca);

                const termo = this.inputBusca.value.trim();

                if (termo.length < 2) {
                    this.ocultarResultados();
                    return;
                }

                this.timeoutBusca = window.setTimeout(
                    () => this.buscarProdutos(termo),
                    300
                );
            });

            this.inputBusca.addEventListener("keydown", (event) => {
                if (event.key === "Escape") {
                    this.ocultarResultados();
                }

                if (
                    event.key === "Enter"
                    && !this.resultados.classList.contains("d-none")
                ) {
                    event.preventDefault();

                    const primeiroResultado =
                        this.resultados.querySelector(".autocomplete-item");

                    primeiroResultado?.click();
                }
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

        async buscarProdutos(termo) {
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
                    throw new Error("Não foi possível buscar os produtos.");
                }

                const dados = await resposta.json();

                this.renderizarResultados(dados.resultados || []);
            } catch (erro) {
                if (erro.name !== "AbortError") {
                    console.error(erro);
                    this.renderizarErro();
                }
            }
        }

        renderizarResultados(produtos) {
            this.resultados.innerHTML = "";

            if (!produtos.length) {
                this.resultados.innerHTML = `
                    <div class="autocomplete-empty">
                        Nenhum produto encontrado.
                    </div>
                `;

                this.exibirResultados();
                return;
            }

            produtos.forEach((produto) => {
                const item = document.createElement("button");

                item.type = "button";
                item.className = "autocomplete-item";

                const codigo = this.escaparHtml(produto.codigo || "");
                const modelo = this.escaparHtml(produto.modelo || "");
                const marca = this.escaparHtml(produto.marca || "");
                const estoque = Number(produto.estoque_atual || 0);
                const preco = this.formatarMoeda(produto.preco_venda || 0);

                item.innerHTML = `
                    <div class="autocomplete-item-header">
                        <strong>${codigo} — ${modelo}</strong>
                        <strong>${preco}</strong>
                    </div>

                    <span>
                        ${marca || "Marca não informada"}
                        • Estoque: ${estoque}
                    </span>
                `;

                item.addEventListener("click", () => {
                    this.selecionarProduto(produto);
                });

                this.resultados.appendChild(item);
            });

            this.exibirResultados();
        }

        selecionarProduto(produto) {
            this.produtoSelecionado = produto;
            this.inputId.value = produto.id;

            const codigo = produto.codigo || "";
            const modelo = produto.modelo || "";

            this.inputBusca.value = `${codigo} - ${modelo}`.trim();

            this.ocultarResultados();

            this.inputBusca.dispatchEvent(
                new CustomEvent("produto:selecionado", {
                    bubbles: true,
                    detail: produto,
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
            this.resultados.innerHTML = `
                <div class="autocomplete-empty">
                    Não foi possível realizar a busca.
                </div>
            `;

            this.exibirResultados();
        }

        exibirResultados() {
            this.resultados.classList.remove("d-none");
        }

        ocultarResultados() {
            this.resultados.classList.add("d-none");
        }

        formatarMoeda(valor) {
            return Number(valor || 0).toLocaleString("pt-BR", {
                style: "currency",
                currency: "BRL",
            });
        }

        escaparHtml(valor) {
            const elemento = document.createElement("div");
            elemento.textContent = valor ?? "";
            return elemento.innerHTML;
        }
    }

    document.addEventListener("DOMContentLoaded", () => {
        window.HelviComercial = window.HelviComercial || {};
        window.HelviComercial.produtoAutocomplete =
            new ProdutoAutocomplete();
    });
})();