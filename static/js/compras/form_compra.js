document.addEventListener("DOMContentLoaded", () => {
    const campoDocumento = document.getElementById("id_fornecedor_documento");
    const campoTelefone = document.getElementById("id_fornecedor_telefone");

    function somenteNumeros(valor) {
        return String(valor || "").replace(/\D/g, "");
    }

    function formatarTelefone(valor) {
        const numeros = somenteNumeros(valor).slice(0, 11);

        if (numeros.length <= 2) return numeros;
        if (numeros.length <= 6) return `(${numeros.slice(0, 2)}) ${numeros.slice(2)}`;
        if (numeros.length <= 10) return `(${numeros.slice(0, 2)}) ${numeros.slice(2, 6)}-${numeros.slice(6)}`;

        return `(${numeros.slice(0, 2)}) ${numeros.slice(2, 7)}-${numeros.slice(7)}`;
    }

    if (campoDocumento) {
        campoDocumento.addEventListener("input", () => {
            campoDocumento.value = somenteNumeros(campoDocumento.value).slice(0, 14);
        });

        campoDocumento.addEventListener("paste", () => {
            setTimeout(() => {
                campoDocumento.value = somenteNumeros(campoDocumento.value).slice(0, 14);
            }, 10);
        });
    }

    if (campoTelefone) {
        campoTelefone.addEventListener("input", () => {
            campoTelefone.value = formatarTelefone(campoTelefone.value);
        });

        campoTelefone.addEventListener("paste", () => {
            setTimeout(() => {
                campoTelefone.value = formatarTelefone(campoTelefone.value);
            }, 10);
        });
    }
});