document.addEventListener("DOMContentLoaded", () => {
    const campoBusca = document.getElementById("busca-produto-inline");
    const resultados = document.getElementById("resultado-produtos-inline");
    const estadoVazio = document.getElementById("itens-vazio");
    const wrapperTabela = document.getElementById("tabela-itens-wrapper");
    const corpoTabela = document.getElementById("tabela-itens-body");

    const resumoSubtotal = document.getElementById("resumo-subtotal");
    const resumoDesconto = document.getElementById("resumo-desconto");
    const resumoFrete = document.getElementById("resumo-frete");
    const resumoTotal = document.getElementById("resumo-total");
    const campoFrete = document.getElementById("id_frete");

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
        return Number(String(valor || "0").replace(",", ".")) || 0;
    }

    function moeda(valor) {
        return valor.toLocaleString("pt-BR", {
            style: "currency",
            currency: "BRL",
        });
    }

    function atualizarEstadoTabela() {
        if (corpoTabela.children.length === 0) {
            wrapperTabela.classList.add("d-none");
            estadoVazio.classList.remove("d-none");
        } else {
            wrapperTabela.classList.remove("d-none");
            estadoVazio.classList.add("d-none");
        }
    }

    function recalcularResumo() {
        let subtotal = 0;
        let descontoTotal = 0;

        corpoTabela.querySelectorAll("tr").forEach((linha) => {
            const quantidade = numero(linha.querySelector(".quantidade").value);
            const custo = numero(linha.querySelector(".custo").value);
            const desconto = numero(linha.querySelector(".desconto").value);

            const totalItem = Math.max((quantidade * custo) - desconto, 0);

            linha.querySelector(".total-item").textContent = moeda(totalItem);

            subtotal += quantidade * custo;
            descontoTotal += desconto;
        });

        const frete = numero(campoFrete ? campoFrete.value : 0);
        const total = subtotal - descontoTotal + frete;

        resumoSubtotal.textContent = moeda(subtotal);
        resumoDesconto.textContent = moeda(descontoTotal);
        resumoFrete.textContent = moeda(frete);
        resumoTotal.textContent = moeda(total);
    }

    function adicionarProduto(produto) {
        const produtoJaExiste = corpoTabela.querySelector(
            `input[name="produto_id[]"][value="${produto.id}"]`
        );

        if (produtoJaExiste) {
            const linha = produtoJaExiste.closest("tr");
            const campoQuantidade = linha.querySelector(".quantidade");

            campoQuantidade.value = numero(campoQuantidade.value) + 1;

            campoBusca.value = "";
            resultados.innerHTML = "";

            recalcularResumo();
            return;
        }

        const linha = document.createElement("tr");

        linha.innerHTML = `
            <td>
                <input type="hidden" name="produto_id[]" value="${produto.id}">
                <strong>${produto.codigo}</strong><br>
                <span class="text-muted">${produto.modelo}</span>
            </td>

            <td>
                <input type="number" name="quantidade[]" class="form-control quantidade" value="1" min="1">
            </td>

            <td>
                <input type="number" name="custo_unitario[]" class="form-control custo" value="${produto.preco_custo || 0}" step="0.01" min="0">
            </td>

            <td>
                <input type="number" name="desconto_item[]" class="form-control desconto" value="0.00" step="0.01" min="0">
            </td>

            <td class="fw-bold total-item">
                R$ 0,00
            </td>

            <td class="text-center">
                <button type="button" class="btn btn-sm btn-outline-danger remover-item">
                    <i class="bi bi-trash"></i>
                </button>
            </td>
        `;

        corpoTabela.appendChild(linha);

        campoBusca.value = "";
        resultados.innerHTML = "";

        atualizarEstadoTabela();
        recalcularResumo();
    }

    campoBusca.addEventListener("input", async () => {
        const termo = campoBusca.value.trim();
        resultados.innerHTML = "";

        if (termo.length < 2) return;

        const response = await fetch(`/compras/api/produtos/?q=${encodeURIComponent(termo)}`);
        const data = await response.json();

        if (!data.resultados.length) {
            resultados.innerHTML = `<div class="produto-resultado-vazio">Nenhum produto encontrado.</div>`;
            return;
        }

        data.resultados.forEach((produto) => {
            const item = document.createElement("button");
            item.type = "button";
            item.className = "produto-resultado-item";

            item.innerHTML = `
                <strong>${produto.codigo}</strong>
                <span>${produto.modelo}</span>
            `;

            item.addEventListener("click", () => {
                adicionarProduto(produto);
            });

            resultados.appendChild(item);
        });
    });

    corpoTabela.addEventListener("input", (event) => {
        if (
            event.target.classList.contains("quantidade") ||
            event.target.classList.contains("custo") ||
            event.target.classList.contains("desconto")
        ) {
            recalcularResumo();
        }
    });

    corpoTabela.addEventListener("click", (event) => {
        const botao = event.target.closest(".remover-item");

        if (!botao) return;

        botao.closest("tr").remove();

        atualizarEstadoTabela();
        recalcularResumo();
    });

    if (campoFrete) {
        campoFrete.addEventListener("input", recalcularResumo);
    }

    atualizarEstadoTabela();
    recalcularResumo();
});