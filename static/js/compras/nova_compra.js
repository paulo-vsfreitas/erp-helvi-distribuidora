document.addEventListener("DOMContentLoaded", () => {
    HelviModalBusca({
        modal: "#modalBuscaProduto",
        input: "#campoBuscaProduto",
        resultados: "#resultadoBuscaProduto",
        abrir: "#btn-abrir-modal-produto",
        url: "/compras/api/produtos/",

        render(produto) {
            return `
                <strong>${produto.codigo}</strong>
                <span>${produto.modelo}</span>
            `;
        },

        onSelect(produto) {
            adicionarProdutoTabela(produto);
        },
    });
});