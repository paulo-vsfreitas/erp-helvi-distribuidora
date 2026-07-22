(() => {
    "use strict";

    class ItensOrcamento {
        constructor() {
            this.corpoTabela = document.getElementById("orcamento-itens");
            this.inputJson = document.getElementById("itens-json");

            this.itens = [];

            if (!this.corpoTabela || !this.inputJson) {
                return;
            }

            this.carregarItensIniciais();
            this.renderizar();
        }

        carregarItensIniciais() {
            try {
                const dados = JSON.parse(this.inputJson.value || "[]");

                if (!Array.isArray(dados)) {
                    return;
                }

                this.itens = dados.map((item) => ({
                    produto_id: Number(
                        item.produto_id
                        || item.produto
                        || item.id
                    ),
                    codigo: item.codigo || "",
                    descricao:
                        item.descricao
                        || item.modelo
                        || item.produto_nome
                        || "",
                    marca: item.marca || "",
                    quantidade: this.normalizarQuantidade(item.quantidade),
                    valor_unitario: this.normalizarDecimal(
                        item.valor_unitario
                        || item.preco_venda
                    ),
                    desconto: this.normalizarDecimal(item.desconto),
                }));
            } catch (erro) {
                console.error("Itens iniciais inválidos.", erro);
                this.itens = [];
            }
        }

        adicionarProduto(produto) {
            const produtoId = Number(produto.id);

            if (!produtoId) {
                return {
                    sucesso: false,
                    mensagem: "Produto inválido.",
                };
            }

            const existente = this.itens.find(
                (item) => item.produto_id === produtoId
            );

            if (existente) {
                existente.quantidade += 1;
                this.atualizar();

                return {
                    sucesso: true,
                    mensagem: "Quantidade do produto atualizada.",
                };
            }

            this.itens.push({
                produto_id: produtoId,
                codigo: produto.codigo || "",
                descricao: this.montarDescricao(produto),
                marca: produto.marca || "",
                quantidade: 1,
                valor_unitario: this.normalizarDecimal(produto.preco_venda),
                desconto: 0,
            });

            this.atualizar();

            return {
                sucesso: true,
                mensagem: "Produto adicionado.",
            };
        }

        montarDescricao(produto) {
            const partes = [
                produto.modelo,
                produto.marca,
                produto.cores_disponiveis,
            ].filter(Boolean);

            return partes.join(" • ");
        }

        atualizarQuantidade(produtoId, valor) {
            const item = this.obterItem(produtoId);

            if (!item) {
                return;
            }

            item.quantidade = this.normalizarQuantidade(valor);
            this.atualizar();
        }

        atualizarValorUnitario(produtoId, valor) {
            const item = this.obterItem(produtoId);

            if (!item) {
                return;
            }

            item.valor_unitario = this.normalizarDecimal(valor);
            this.atualizar();
        }

        atualizarDesconto(produtoId, valor) {
            const item = this.obterItem(produtoId);

            if (!item) {
                return;
            }

            item.desconto = Math.max(
                0,
                this.normalizarDecimal(valor)
            );

            const bruto = item.quantidade * item.valor_unitario;

            if (item.desconto > bruto) {
                item.desconto = bruto;
            }

            this.atualizar();
        }

        removerProduto(produtoId) {
            this.itens = this.itens.filter(
                (item) => item.produto_id !== Number(produtoId)
            );

            this.atualizar();
        }

        obterItem(produtoId) {
            return this.itens.find(
                (item) => item.produto_id === Number(produtoId)
            );
        }

        obterItens() {
            return this.itens.map((item) => ({
                ...item,
                total: this.calcularTotalItem(item),
            }));
        }

        calcularTotalItem(item) {
            const bruto = item.quantidade * item.valor_unitario;
            return Math.max(0, bruto - item.desconto);
        }

        atualizar() {
            this.renderizar();
            this.sincronizarJson();
            this.emitirAlteracao();
        }

        renderizar() {
            this.corpoTabela.innerHTML = "";

            if (!this.itens.length) {
                this.corpoTabela.innerHTML = `
                    <tr id="estado-vazio">
                        <td
                            colspan="7"
                            class="text-center text-muted py-4"
                        >
                            Nenhum produto adicionado.
                        </td>
                    </tr>
                `;

                this.sincronizarJson();
                return;
            }

            this.itens.forEach((item) => {
                const linha = document.createElement("tr");
                const totalItem = this.calcularTotalItem(item);

                linha.dataset.produtoId = item.produto_id;

                linha.innerHTML = `
                    <td>
                        <strong>${this.escaparHtml(item.codigo)}</strong>
                    </td>

                    <td>
                        <div class="item-produto-descricao">
                            <strong>${this.escaparHtml(item.descricao)}</strong>

                            ${
                                item.marca
                                    ? `<span>${this.escaparHtml(item.marca)}</span>`
                                    : ""
                            }
                        </div>
                    </td>

                    <td>
                        <input
                            type="number"
                            class="form-control form-control-sm item-quantidade"
                            min="1"
                            step="1"
                            value="${item.quantidade}"
                        >
                    </td>

                    <td>
                        <input
                            type="text"
                            class="form-control form-control-sm item-valor-unitario"
                            inputmode="decimal"
                            value="${this.formatarDecimalInput(item.valor_unitario)}"
                        >
                    </td>

                    <td>
                        <input
                            type="text"
                            class="form-control form-control-sm item-desconto"
                            inputmode="decimal"
                            value="${this.formatarDecimalInput(item.desconto)}"
                        >
                    </td>

                    <td>
                        <strong class="item-total">
                            ${this.formatarMoeda(totalItem)}
                        </strong>
                    </td>

                    <td class="text-end">
                        <button
                            type="button"
                            class="btn btn-sm btn-outline-danger item-remover"
                            title="Remover produto"
                        >
                            <i class="bi bi-trash"></i>
                        </button>
                    </td>
                `;

                this.registrarEventosLinha(linha, item.produto_id);
                this.corpoTabela.appendChild(linha);
            });

            this.sincronizarJson();
        }

        registrarEventosLinha(linha, produtoId) {
            const quantidade = linha.querySelector(".item-quantidade");
            const valorUnitario = linha.querySelector(
                ".item-valor-unitario"
            );
            const desconto = linha.querySelector(".item-desconto");
            const remover = linha.querySelector(".item-remover");

            quantidade.addEventListener("change", () => {
                this.atualizarQuantidade(produtoId, quantidade.value);
            });

            valorUnitario.addEventListener("change", () => {
                this.atualizarValorUnitario(
                    produtoId,
                    valorUnitario.value
                );
            });

            desconto.addEventListener("change", () => {
                this.atualizarDesconto(produtoId, desconto.value);
            });

            remover.addEventListener("click", () => {
                this.removerProduto(produtoId);
            });
        }

        sincronizarJson() {
            const itensParaEnvio = this.itens.map((item) => ({
                produto_id: item.produto_id,
                quantidade: item.quantidade,
                valor_unitario: this.formatarDecimalEnvio(
                    item.valor_unitario
                ),
                desconto: this.formatarDecimalEnvio(item.desconto),
            }));

            this.inputJson.value = JSON.stringify(itensParaEnvio);
        }

        emitirAlteracao() {
            document.dispatchEvent(
                new CustomEvent("orcamento:itens-alterados", {
                    detail: {
                        itens: this.obterItens(),
                    },
                })
            );
        }

        normalizarQuantidade(valor) {
            const quantidade = Number.parseInt(valor, 10);

            if (!Number.isFinite(quantidade) || quantidade < 1) {
                return 1;
            }

            return quantidade;
        }

        normalizarDecimal(valor) {
            if (typeof valor === "number") {
                return Number.isFinite(valor) ? valor : 0;
            }

            let texto = String(valor ?? "").trim();

            if (!texto) {
                return 0;
            }

            texto = texto.replace(/[R$\s]/g, "");

            if (texto.includes(",") && texto.includes(".")) {
                texto = texto.replace(/\./g, "").replace(",", ".");
            } else if (texto.includes(",")) {
                texto = texto.replace(",", ".");
            }

            const numero = Number.parseFloat(texto);

            return Number.isFinite(numero) ? numero : 0;
        }

        formatarDecimalInput(valor) {
            return Number(valor || 0).toLocaleString("pt-BR", {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
            });
        }

        formatarDecimalEnvio(valor) {
            return Number(valor || 0).toFixed(2);
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
        window.HelviComercial.itensOrcamento =
            new ItensOrcamento();
    });
})();