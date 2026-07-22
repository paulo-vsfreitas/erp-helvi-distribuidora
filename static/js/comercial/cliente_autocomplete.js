(() => {
    "use strict";

    class ClienteAutocomplete {
        constructor() {
            this.inputBusca = document.getElementById("cliente-search");
            this.inputId = document.getElementById("cliente-id");
            this.resultados = document.getElementById("cliente-resultados");

            this.timeoutBusca = null;
            this.controladorBusca = null;

            if (!this.inputBusca || !this.inputId || !this.resultados) {
                return;
            }

            this.registrarEventos();
        }

        registrarEventos() {
            this.inputBusca.addEventListener("input", () => {
                this.inputId.value = "";

                window.clearTimeout(this.timeoutBusca);

                const termo = this.inputBusca.value.trim();

                if (termo.length < 2) {
                    this.ocultarResultados();
                    return;
                }

                this.timeoutBusca = window.setTimeout(
                    () => this.buscarClientes(termo),
                    300
                );
            });

            this.inputBusca.addEventListener("keydown", (event) => {
                if (event.key === "Escape") {
                    this.ocultarResultados();
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

        async buscarClientes(termo) {
            if (this.controladorBusca) {
                this.controladorBusca.abort();
            }

            this.controladorBusca = new AbortController();

            try {
                const url = new URL(
                    "/comercial/api/clientes/",
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
                    throw new Error("Não foi possível buscar os clientes.");
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

        renderizarResultados(clientes) {
            this.resultados.innerHTML = "";

            if (!clientes.length) {
                this.resultados.innerHTML = `
                    <div class="autocomplete-empty">
                        Nenhum cliente encontrado.
                    </div>
                `;

                this.exibirResultados();
                return;
            }

            clientes.forEach((cliente) => {
                const item = document.createElement("button");

                item.type = "button";
                item.className = "autocomplete-item";

                const nome = this.escaparHtml(
                    cliente.nome_fantasia
                    || cliente.razao_social
                    || "Cliente sem nome"
                );

                const documento = this.escaparHtml(cliente.cnpj || "");
                const cidade = this.escaparHtml(cliente.cidade || "");
                const estado = this.escaparHtml(cliente.estado || "");

                const localizacao = [cidade, estado]
                    .filter(Boolean)
                    .join(" - ");

                item.innerHTML = `
                    <strong>${nome}</strong>

                    <span>
                        ${documento || "Documento não informado"}
                        ${localizacao ? ` • ${localizacao}` : ""}
                    </span>
                `;

                item.addEventListener("click", () => {
                    this.selecionarCliente(cliente);
                });

                this.resultados.appendChild(item);
            });

            this.exibirResultados();
        }

        selecionarCliente(cliente) {
            const nome = (
                cliente.nome_fantasia
                || cliente.razao_social
                || ""
            ).trim();

            this.inputBusca.value = nome;
            this.inputId.value = cliente.id;

            const documento = document.getElementById("id_cliente_documento");
            const telefone = document.getElementById("id_cliente_telefone");
            const email = document.getElementById("id_cliente_email");

            if (documento) {
                documento.value = cliente.cnpj || "";
            }

            if (telefone) {
                telefone.value = cliente.whatsapp || cliente.telefone || "";
            }

            if (email) {
                email.value = cliente.email || "";
            }

            this.ocultarResultados();

            this.inputBusca.dispatchEvent(
                new CustomEvent("cliente:selecionado", {
                    bubbles: true,
                    detail: cliente,
                })
            );
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

        escaparHtml(valor) {
            const elemento = document.createElement("div");
            elemento.textContent = valor ?? "";
            return elemento.innerHTML;
        }
    }

    document.addEventListener("DOMContentLoaded", () => {
        window.HelviComercial = window.HelviComercial || {};
        window.HelviComercial.clienteAutocomplete =
            new ClienteAutocomplete();
    });
})();