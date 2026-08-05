(() => {
    "use strict";

    class ClienteAutocomplete {
        constructor() {
            this.inputBusca = document.getElementById("cliente-search");
            this.inputId = document.getElementById("cliente-id");
            this.resultados = document.getElementById("cliente-resultados");
            this.resumo = document.getElementById("cliente-selecionado");

            this.timeoutBusca = null;
            this.controladorBusca = null;

            this.clientesAtuais = [];
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
                "cliente-resultados"
            );

            this.resultados.setAttribute("role", "listbox");
        }

        registrarEventos() {
            this.inputBusca.addEventListener("focus", () => {
                const termo = this.inputBusca.value.trim();

                this.buscarClientes(
                    this.inputId.value ? "" : termo
                );
            });

            this.inputBusca.addEventListener("click", () => {
                if (this.resultados.classList.contains("d-none")) {
                    const termo = this.inputBusca.value.trim();

                    this.buscarClientes(
                        this.inputId.value ? "" : termo
                    );
                }
            });

            this.inputBusca.addEventListener("input", () => {
                this.inputId.value = "";
                this.ocultarResumo();

                window.clearTimeout(this.timeoutBusca);

                const termo = this.inputBusca.value.trim();

                if (termo.length === 1) {
                    this.clientesAtuais = [];
                    this.indiceAtivo = -1;
                    this.ocultarResultados();
                    return;
                }

                this.timeoutBusca = window.setTimeout(
                    () => this.buscarClientes(termo),
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
                    this.buscarClientes(
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

                const cliente =
                    this.clientesAtuais[this.indiceAtivo];

                if (cliente) {
                    this.selecionarCliente(cliente);
                }
            }
        }

        moverSelecao(direcao) {
            if (!this.clientesAtuais.length) {
                return;
            }

            this.indiceAtivo += direcao;

            if (this.indiceAtivo >= this.clientesAtuais.length) {
                this.indiceAtivo = 0;
            }

            if (this.indiceAtivo < 0) {
                this.indiceAtivo =
                    this.clientesAtuais.length - 1;
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

        async buscarClientes(termo = "") {
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
                    throw new Error(
                        "Não foi possível buscar os clientes."
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

        renderizarResultados(clientes) {
            this.resultados.innerHTML = "";
            this.clientesAtuais = clientes;
            this.indiceAtivo = -1;

            if (!clientes.length) {
                this.resultados.innerHTML = `
                    <div class="autocomplete-empty">
                        <i class="bi bi-search"></i>

                        <span>
                            Nenhum cliente ativo encontrado.
                        </span>
                    </div>
                `;

                this.exibirResultados();
                return;
            }

            clientes.forEach((cliente, indice) => {
                const item = document.createElement("button");

                item.type = "button";
                item.id = `cliente-opcao-${indice}`;
                item.className = "autocomplete-item";
                item.setAttribute("role", "option");
                item.setAttribute("aria-selected", "false");

                const nome = this.escaparHtml(
                    this.nomeCliente(cliente)
                );

                const documento = this.escaparHtml(
                    cliente.cnpj || "Documento não informado"
                );

                const telefone = this.escaparHtml(
                    cliente.whatsapp
                    || cliente.telefone
                    || "Telefone não informado"
                );

                const localizacao = this.escaparHtml(
                    this.localizacaoCliente(cliente)
                    || "Localização não informada"
                );

                item.innerHTML = `
                    <div class="cliente-resultado-icon">
                        <i class="bi bi-building"></i>
                    </div>

                    <div class="cliente-resultado-conteudo">
                        <strong>${nome}</strong>

                        <div class="cliente-resultado-dados">
                            <span>
                                <i class="bi bi-card-text"></i>
                                ${documento}
                            </span>

                            <span>
                                <i class="bi bi-whatsapp"></i>
                                ${telefone}
                            </span>

                            <span>
                                <i class="bi bi-geo-alt"></i>
                                ${localizacao}
                            </span>
                        </div>
                    </div>
                `;

                item.addEventListener("mouseenter", () => {
                    this.indiceAtivo = indice;
                    this.atualizarDestaque();
                });

                item.addEventListener("click", () => {
                    this.selecionarCliente(cliente);
                });

                this.resultados.appendChild(item);
            });

            this.exibirResultados();
        }

        selecionarCliente(cliente) {
            const nome = this.nomeCliente(cliente);

            this.inputBusca.value = nome;
            this.inputId.value = cliente.id;

            this.preencherCamposRelacionados(cliente);
            this.mostrarResumo(cliente);
            this.ocultarResultados();

            this.inputBusca.dispatchEvent(
                new CustomEvent("cliente:selecionado", {
                    bubbles: true,
                    detail: cliente,
                })
            );
        }

        preencherCamposRelacionados(cliente) {
            const documento = document.getElementById(
                "id_cliente_documento"
            );

            const telefone = document.getElementById(
                "id_cliente_telefone"
            );

            const email = document.getElementById(
                "id_cliente_email"
            );

            if (documento) {
                documento.value = cliente.cnpj || "";
            }

            if (telefone) {
                telefone.value = (
                    cliente.whatsapp
                    || cliente.telefone
                    || ""
                );
            }

            if (email) {
                email.value = cliente.email || "";
            }

            const mapaEntrega = {
                id_entrega_cep: "cep",
                id_entrega_logradouro: "logradouro",
                id_entrega_numero: "numero",
                id_entrega_complemento: "complemento",
                id_entrega_bairro: "bairro",
                id_entrega_cidade: "cidade",
                id_entrega_estado: "estado",
            };
            Object.entries(mapaEntrega).forEach(([id, chave]) => {
                const campo = document.getElementById(id);
                if (campo && !campo.value) campo.value = cliente[chave] || "";
            });
        }

        mostrarResumo(cliente) {
            if (!this.resumo) {
                return;
            }

            const nome = this.escaparHtml(
                this.nomeCliente(cliente)
            );

            const documento = this.escaparHtml(
                cliente.cnpj || "Documento não informado"
            );

            const telefone = this.escaparHtml(
                cliente.whatsapp
                || cliente.telefone
                || "Telefone não informado"
            );

            const email = this.escaparHtml(
                cliente.email || "E-mail não informado"
            );

            const localizacao = this.escaparHtml(
                this.localizacaoCliente(cliente)
                || "Localização não informada"
            );

            this.resumo.innerHTML = `
                <div class="cliente-selecionado-icon">
                    <i class="bi bi-person-check-fill"></i>
                </div>

                <div class="cliente-selecionado-conteudo">
                    <span>Cliente selecionado</span>
                    <strong>${nome}</strong>

                    <p>
                        ${documento}
                        • ${telefone}
                        • ${email}
                        • ${localizacao}
                    </p>
                </div>
            `;

            this.resumo.classList.remove("d-none");
        }

        ocultarResumo() {
            if (!this.resumo) {
                return;
            }

            this.resumo.classList.add("d-none");
            this.resumo.innerHTML = "";
        }

        nomeCliente(cliente) {
            return (
                cliente.nome_fantasia
                || cliente.razao_social
                || "Cliente sem nome"
            ).trim();
        }

        localizacaoCliente(cliente) {
            return [
                cliente.cidade || "",
                cliente.estado || "",
            ]
                .filter(Boolean)
                .join(" - ");
        }

        renderizarErro() {
            this.clientesAtuais = [];
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

        escaparHtml(valor) {
            const elemento = document.createElement("div");

            elemento.textContent = valor ?? "";

            return elemento.innerHTML;
        }
    }

    document.addEventListener("DOMContentLoaded", () => {
        window.HelviComercial =
            window.HelviComercial || {};

        window.HelviComercial.clienteAutocomplete =
            new ClienteAutocomplete();
    });
})();
