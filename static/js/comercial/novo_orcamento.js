(() => {
    "use strict";

    class NovoOrcamento {
        constructor() {
            this.form = document.getElementById("form-orcamento");
            this.botaoAdicionar = document.getElementById(
                "btn-adicionar-produto"
            );

            this.inputClienteId = document.getElementById("cliente-id");
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

            const produto = autocomplete?.obterProdutoSelecionado();

            if (!produto) {
                this.exibirMensagem(
                    "Selecione um produto nos resultados da busca.",
                    "warning"
                );

                autocomplete?.focar();
                return;
            }

            const resultado = gerenciadorItens?.adicionarProduto(produto);

            if (!resultado?.sucesso) {
                this.exibirMensagem(
                    resultado?.mensagem || "Não foi possível adicionar.",
                    "danger"
                );

                return;
            }

            autocomplete.limparSelecao();
            autocomplete.focar();
        }

        validarFormulario() {
            let valido = true;

            this.limparErros();

            if (!this.inputClienteBusca?.value.trim()) {
                this.marcarInvalido(
                    this.inputClienteBusca,
                    "Informe o nome do cliente ou interessado."
                );

                valido = false;
            }

            const itens =
                window.HelviComercial?.itensOrcamento?.obterItens() || [];

            if (!itens.length) {
                this.exibirMensagem(
                    "Adicione pelo menos um produto ao orçamento.",
                    "warning"
                );

                valido = false;
            }

            if (!valido) {
                window.scrollTo({
                    top: 0,
                    behavior: "smooth",
                });
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

            campo.insertAdjacentElement("afterend", feedback);
        }

        limparErros() {
            this.form
                .querySelectorAll(".is-invalid")
                .forEach((campo) => campo.classList.remove("is-invalid"));

            this.form
                .querySelectorAll('[data-erro-frontend="true"]')
                .forEach((elemento) => elemento.remove());
        }

        exibirMensagem(mensagem, tipo = "info") {
            const existente = document.getElementById(
                "mensagem-orcamento-js"
            );

            existente?.remove();

            const alerta = document.createElement("div");

            alerta.id = "mensagem-orcamento-js";
            alerta.className = `alert alert-${tipo} alert-dismissible fade show`;
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

    document.addEventListener("DOMContentLoaded", () => {
        window.HelviComercial = window.HelviComercial || {};
        window.HelviComercial.novoOrcamento =
            new NovoOrcamento();
    });
})();