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
                    variacoes: item.variacoes || [],
                    variacao_cor_id: Number(item.variacao_cor_id || 0) || null,
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
            const variacaoCorId = Number(produto.variacao_cor_id || 0) || null;

            if (!produtoId) {
                return {
                    sucesso: false,
                    mensagem: "Produto inválido.",
                };
            }

            if ((produto.variacoes || []).length && !variacaoCorId) {
                return {sucesso: false, mensagem: "Selecione uma cor disponível para este produto."};
            }

            const existente = this.obterItem(produtoId, variacaoCorId);

            if (existente) {
                this.destacarProdutoExistente(produtoId, variacaoCorId);

                return {
                    sucesso: false,
                    mensagem:
                        "Esta combinação de produto e cor já foi adicionada. " +
                        "Altere a quantidade diretamente na lista ou escolha outra cor.",
                };
            }

            this.itens.push({
                produto_id: produtoId,
                codigo: produto.codigo || "",
                descricao: this.montarDescricao(produto),
                marca: produto.marca || "",
                variacoes: produto.variacoes || [],
                variacao_cor_id: variacaoCorId,
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

        destacarProdutoExistente(produtoId, variacaoCorId = null) {
            const linha = this.corpoTabela.querySelector(
                `tr[data-chave-item="${produtoId}:${variacaoCorId || ""}"]`
            );

            if (!linha) {
                return;
            }

            linha.scrollIntoView({
                behavior: "smooth",
                block: "center",
            });

            linha.classList.add("item-produto-destacado");

            window.setTimeout(() => {
                linha.classList.remove("item-produto-destacado");
            }, 2200);

            const campoQuantidade = linha.querySelector(
                ".item-quantidade"
            );

            if (campoQuantidade) {
                window.setTimeout(() => {
                    campoQuantidade.focus();
                    campoQuantidade.select();
                }, 400);
            }
        }

        atualizarQuantidade(item, valor) {
            item.quantidade = this.normalizarQuantidade(valor);
            this.atualizar();
        }

        atualizarValorUnitario(item, valor) {
            item.valor_unitario = this.normalizarDecimal(valor);
            this.atualizar();
        }

        atualizarDesconto(item, valor) {
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

        removerProduto(itemRemovido) {
            this.itens = this.itens.filter(
                (item) => item !== itemRemovido
            );

            this.atualizar();
        }

        obterItem(produtoId, variacaoCorId = null) {
            return this.itens.find(
                (item) => item.produto_id === Number(produtoId)
                    && (item.variacao_cor_id || null) === (Number(variacaoCorId || 0) || null)
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
                            colspan="8"
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
                linha.dataset.chaveItem = `${item.produto_id}:${item.variacao_cor_id || ""}`;

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
                        <select class="form-select form-select-sm item-variacao-cor" ${item.variacoes.length ? "required" : "disabled"}>
                            <option value="">${item.variacoes.length ? "Selecione" : "Sem variação"}</option>
                            ${item.variacoes.map((cor) => `<option value="${cor.id}" ${Number(item.variacao_cor_id) === Number(cor.id) ? "selected" : ""}>${this.escaparHtml(cor.nome)} (${this.escaparHtml(cor.codigo)}) · estoque ${cor.estoque}</option>`).join("")}
                        </select>
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

                this.registrarEventosLinha(linha, item);
                this.corpoTabela.appendChild(linha);
            });

            this.sincronizarJson();
        }

        registrarEventosLinha(linha, item) {
            const quantidade = linha.querySelector(".item-quantidade");
            const valorUnitario = linha.querySelector(
                ".item-valor-unitario"
            );
            const desconto = linha.querySelector(".item-desconto");
            const variacao = linha.querySelector(".item-variacao-cor");
            const remover = linha.querySelector(".item-remover");

            quantidade.addEventListener("change", () => {
                this.atualizarQuantidade(item, quantidade.value);
            });

            valorUnitario.addEventListener("change", () => {
                this.atualizarValorUnitario(
                    item,
                    valorUnitario.value
                );
            });

            desconto.addEventListener("change", () => {
                this.atualizarDesconto(item, desconto.value);
            });

            variacao.addEventListener("change", () => {
                const novaVariacao = Number(variacao.value || 0) || null;
                const duplicado = this.itens.find((outro) =>
                    outro !== item
                    && outro.produto_id === item.produto_id
                    && (outro.variacao_cor_id || null) === novaVariacao
                );
                if (duplicado) {
                    variacao.value = item.variacao_cor_id || "";
                    window.alert("Esta combinação de produto e cor já foi adicionada.");
                    return;
                }
                item.variacao_cor_id = novaVariacao;
                this.sincronizarJson();
            });

            remover.addEventListener("click", () => {
                this.removerProduto(item);
            });
        }

        sincronizarJson() {
            const itensParaEnvio = this.itens.map((item) => ({
                produto_id: item.produto_id,
                variacao_cor_id: item.variacao_cor_id,
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
