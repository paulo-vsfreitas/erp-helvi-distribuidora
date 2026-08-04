document.addEventListener("DOMContentLoaded", () => {
    "use strict";

    const campoTelefone =
        document.getElementById("whatsappTelefone");

    const campoMensagem =
        document.getElementById("whatsappMensagem");

    const checkboxAbrirPdf =
        document.getElementById("abrirPdf");


    const botaoWhatsapp =
        document.getElementById("btnWhatsapp");

    const botaoCopiar =
        document.getElementById("btnCopiarMensagem");

    const botaoRestaurar =
        document.getElementById("btnRestaurarMensagem");

    const contadorMensagem =
        document.getElementById("contadorMensagem");

    if (!campoMensagem) {
        return;
    }

    const mensagemOriginal = campoMensagem.value;

    function normalizarTelefone(telefone) {
        let numeros = String(telefone || "")
            .replace(/\D/g, "");

        if (!numeros) {
            return "";
        }

        /*
         * Acrescenta o código do Brasil somente quando
         * o telefone ainda possui apenas DDD + número.
         */
        if (
            !numeros.startsWith("55")
            && (numeros.length === 10 || numeros.length === 11)
        ) {
            numeros = `55${numeros}`;
        }

        return numeros;
    }

    function atualizarContador() {
        if (!contadorMensagem) {
            return;
        }

        const quantidade = campoMensagem.value.length;

        contadorMensagem.textContent =
            `${quantidade} ${
                quantidade === 1
                    ? "caractere"
                    : "caracteres"
            }`;
    }

    async function copiarMensagem() {
        const mensagem = campoMensagem.value.trim();

        if (!mensagem) {
            window.alert(
                "Não existe uma mensagem para copiar."
            );
            return;
        }

        try {
            await navigator.clipboard.writeText(mensagem);

            if (!botaoCopiar) {
                return;
            }

            const htmlOriginal = botaoCopiar.innerHTML;

            botaoCopiar.innerHTML = `
                <i class="bi bi-check-lg"></i>
                Copiado!
            `;

            botaoCopiar.classList.remove(
                "btn-outline-secondary"
            );

            botaoCopiar.classList.add(
                "btn-success"
            );

            window.setTimeout(() => {
                botaoCopiar.innerHTML = htmlOriginal;

                botaoCopiar.classList.remove(
                    "btn-success"
                );

                botaoCopiar.classList.add(
                    "btn-outline-secondary"
                );
            }, 1800);
        } catch (erro) {
            console.error(
                "Erro ao copiar mensagem:",
                erro
            );

            window.alert(
                "Não foi possível copiar a mensagem."
            );
        }
    }

    function restaurarMensagem() {
        campoMensagem.value = mensagemOriginal;

        atualizarContador();
        campoMensagem.focus();
    }

    function abrirWhatsapp() {
        const telefone = normalizarTelefone(
            campoTelefone?.value
        );

        const mensagem = campoMensagem.value.trim();

        if (!telefone) {
            window.alert(
                "Informe o telefone do destinatário."
            );

            campoTelefone?.focus();
            return;
        }

        if (telefone.length < 12 || telefone.length > 13) {
            window.alert(
                "Informe um telefone válido com DDD."
            );

            campoTelefone?.focus();
            return;
        }

        if (!mensagem) {
            window.alert(
                "Informe a mensagem que será enviada."
            );

            campoMensagem.focus();
            return;
        }

        const urlWhatsapp =
            `https://wa.me/${telefone}` +
            `?text=${encodeURIComponent(mensagem)}`;

        /*
         * As duas janelas são abertas diretamente durante
         * o clique para reduzir o risco de bloqueio do navegador.
         */
        if (checkboxAbrirPdf?.checked) {
            const urlDownload =
                checkboxAbrirPdf.dataset.downloadUrl;

            if (urlDownload) {
                const linkDownload =
                    document.createElement("a");

                linkDownload.href = urlDownload;
                linkDownload.download = "";
                linkDownload.style.display = "none";

                document.body.appendChild(linkDownload);
                linkDownload.click();
                linkDownload.remove();
            }
        }

        window.open(
            urlWhatsapp,
            "_blank",
            "noopener,noreferrer"
        );
    }

    campoMensagem.addEventListener(
        "input",
        atualizarContador
    );

    botaoCopiar?.addEventListener(
        "click",
        copiarMensagem
    );

    botaoRestaurar?.addEventListener(
        "click",
        restaurarMensagem
    );

    botaoWhatsapp?.addEventListener(
        "click",
        abrirWhatsapp
    );

    atualizarContador();
});