(() => {
    "use strict";

    class NovoOrcamento {
        constructor() {
            this.form = document.getElementById("form-orcamento");

            this.botaoAdicionar = document.getElementById(
                "btn-adicionar-produto"
            );

            this.inputClienteId = document.getElementById(
                "cliente-id"
            );

            this.inputClienteBusca = document.getElementById(
                "cliente-search"
            );

            if (!this.form || !this.botaoAdicionar) {
                return;
            }

            this.registrarEventos();
        }

        registrarEventos() {
            this.botaoAdicionar.addEventListener("click", () => {
                this.adicionarProdutoSelecionado();
            });

            document
                .getElementById("produto-search")
                ?.addEventListener("keydown", (event) => {
                    if (event.key !== "Enter") {
                        return;
                    }

                    const autocomplete =
                        window.HelviComercial?.produtoAutocomplete;

                    if (autocomplete?.obterProdutoSelecionado()) {
                        event.preventDefault();
                        this.adicionarProdutoSelecionado();
                    }
                });

            this.form.addEventListener("submit", (event) => {
                if (!this.validarFormulario()) {
                    event.preventDefault();
                }
            });
        }

        adicionarProdutoSelecionado() {
            const autocomplete =
                window.HelviComercial?.produtoAutocomplete;

            const gerenciadorItens =
                window.HelviComercial?.itensOrcamento;

            const produto =
                autocomplete?.obterProdutoSelecionado();

            this.limparMensagemProdutos();

            if (!produto) {
                this.exibirMensagemProdutos(
                    "Selecione um produto nos resultados da busca.",
                    "warning"
                );

                autocomplete?.focar();
                return;
            }

            if (!gerenciadorItens) {
                this.exibirMensagemProdutos(
                    "Não foi possível carregar a lista de produtos.",
                    "danger"
                );

                return;
            }

            const resultado =
                gerenciadorItens.adicionarProduto(produto);

            if (!resultado?.sucesso) {
                this.exibirMensagemProdutos(
                    resultado?.mensagem
                        || "Não foi possível adicionar o produto.",
                    "danger"
                );

                return;
            }

            autocomplete?.limparSelecao();
            autocomplete?.focar();
        }

        validarFormulario() {
            let valido = true;

            this.limparErros();
            this.limparMensagemProdutos();

            if (!this.inputClienteBusca?.value.trim()) {
                this.marcarInvalido(
                    this.inputClienteBusca,
                    "Informe o nome do cliente ou interessado."
                );

                valido = false;
            }

            const itens =
                window.HelviComercial
                    ?.itensOrcamento
                    ?.obterItens()
                || [];

            if (!itens.length) {
                this.exibirMensagemProdutos(
                    "Adicione pelo menos um produto ao orçamento.",
                    "warning"
                );

                valido = false;
            }

            if (!valido) {
                const primeiroInvalido =
                    this.form.querySelector(".is-invalid");

                if (primeiroInvalido) {
                    primeiroInvalido.scrollIntoView({
                        behavior: "smooth",
                        block: "center",
                    });

                    primeiroInvalido.focus();
                }
            }

            return valido;
        }

        marcarInvalido(campo, mensagem) {
            if (!campo) {
                return;
            }

            campo.classList.add("is-invalid");

            const feedback = document.createElement("div");

            feedback.className = "invalid-feedback";
            feedback.dataset.erroFrontend = "true";
            feedback.textContent = mensagem;

            campo.insertAdjacentElement(
                "afterend",
                feedback
            );
        }

        limparErros() {
            this.form
                .querySelectorAll(".is-invalid")
                .forEach((campo) => {
                    campo.classList.remove("is-invalid");
                });

            this.form
                .querySelectorAll(
                    '[data-erro-frontend="true"]'
                )
                .forEach((elemento) => {
                    elemento.remove();
                });
        }

        exibirMensagemProdutos(
            mensagem,
            tipo = "warning"
        ) {
            const container = document.getElementById(
                "mensagem-produtos"
            );

            if (!container) {
                this.exibirMensagem(mensagem, tipo);
                return;
            }

            container.classList.remove("d-none");

            container.innerHTML = `
                <div
                    class="alert alert-${tipo} alert-dismissible fade show"
                    role="alert"
                >
                    <i class="bi bi-x-octagon-fill me-2"></i>

                    ${this.escaparHtml(mensagem)}

                    <button
                        type="button"
                        class="btn-close"
                        data-bs-dismiss="alert"
                        aria-label="Fechar"
                    ></button>
                </div>
            `;

            container.scrollIntoView({
                behavior: "smooth",
                block: "nearest",
            });
        }

        limparMensagemProdutos() {
            const container = document.getElementById(
                "mensagem-produtos"
            );

            if (!container) {
                return;
            }

            container.innerHTML = "";
            container.classList.add("d-none");
        }

        exibirMensagem(mensagem, tipo = "info") {
            const existente = document.getElementById(
                "mensagem-orcamento-js"
            );

            existente?.remove();

            const alerta = document.createElement("div");

            alerta.id = "mensagem-orcamento-js";

            alerta.className =
                `alert alert-${tipo} alert-dismissible fade show mb-4`;

            alerta.setAttribute("role", "alert");

            alerta.innerHTML = `
                ${this.escaparHtml(mensagem)}

                <button
                    type="button"
                    class="btn-close"
                    data-bs-dismiss="alert"
                    aria-label="Fechar"
                ></button>
            `;

            this.form.prepend(alerta);
        }

        escaparHtml(valor) {
            const elemento = document.createElement("div");

            elemento.textContent = valor ?? "";

            return elemento.innerHTML;
        }
    }

    document.addEventListener(
        "DOMContentLoaded",
        () => {
            window.HelviComercial =
                window.HelviComercial || {};

            window.HelviComercial.novoOrcamento =
                new NovoOrcamento();
        }
    );
})();