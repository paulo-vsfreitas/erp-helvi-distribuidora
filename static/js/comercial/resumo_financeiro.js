(() => {
    "use strict";

    class ResumoFinanceiro {
        constructor() {
            this.elementoSubtotal = document.getElementById("subtotal");
            this.elementoDesconto = document.getElementById("desconto");
            this.elementoFrete = document.getElementById("frete");
            this.elementoTotal = document.getElementById("total-geral");

            this.inputDesconto = document.getElementById("id_desconto");
            this.inputFrete = document.getElementById("id_frete");

            this.itens = [];

            if (
                !this.elementoSubtotal
                || !this.elementoDesconto
                || !this.elementoFrete
                || !this.elementoTotal
            ) {
                return;
            }

            this.registrarEventos();
            this.recalcular();
        }

        registrarEventos() {
            document.addEventListener(
                "orcamento:itens-alterados",
                (event) => {
                    this.itens = event.detail?.itens || [];
                    this.recalcular();
                }
            );

            this.inputDesconto?.addEventListener(
                "input",
                () => this.recalcular()
            );

            this.inputFrete?.addEventListener(
                "input",
                () => this.recalcular()
            );
        }

        recalcular() {
            const subtotalBruto = this.itens.reduce(
                (acumulado, item) => {
                    return acumulado
                        + (
                            Number(item.quantidade || 0)
                            * Number(item.valor_unitario || 0)
                        );
                },
                0
            );

            const descontosItens = this.itens.reduce(
                (acumulado, item) => {
                    return acumulado + Number(item.desconto || 0);
                },
                0
            );

            const descontoGeral = this.normalizarDecimal(
                this.inputDesconto?.value
            );

            const frete = this.normalizarDecimal(
                this.inputFrete?.value
            );

            const descontoTotal = descontosItens + descontoGeral;

            const total = Math.max(
                0,
                subtotalBruto - descontoTotal + frete
            );

            this.elementoSubtotal.textContent =
                this.formatarMoeda(subtotalBruto);

            this.elementoDesconto.textContent =
                this.formatarMoeda(descontoTotal);

            this.elementoFrete.textContent =
                this.formatarMoeda(frete);

            this.elementoTotal.textContent =
                this.formatarMoeda(total);
        }

        normalizarDecimal(valor) {
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

        formatarMoeda(valor) {
            return Number(valor || 0).toLocaleString("pt-BR", {
                style: "currency",
                currency: "BRL",
            });
        }
    }

    document.addEventListener("DOMContentLoaded", () => {
        window.HelviComercial = window.HelviComercial || {};
        window.HelviComercial.resumoFinanceiro =
            new ResumoFinanceiro();

        document.dispatchEvent(
            new CustomEvent("orcamento:itens-alterados", {
                detail: {
                    itens:
                        window.HelviComercial.itensOrcamento
                            ?.obterItens() || [],
                },
            })
        );
    });
})();