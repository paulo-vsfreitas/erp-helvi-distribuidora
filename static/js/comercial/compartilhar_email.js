document.addEventListener("DOMContentLoaded", () => {
    "use strict";

    const campoMensagem =
        document.getElementById("emailMensagem");

    const contador =
        document.getElementById("contadorMensagemEmail");

    const botaoCopiar =
        document.getElementById("btnCopiarMensagemEmail");

    const botaoRestaurar =
        document.getElementById("btnRestaurarMensagemEmail");

    const formulario =
        document.getElementById("formEnviarEmail");

    const botaoEnviar =
        document.getElementById("btnEnviarEmail");

    if (!campoMensagem) {
        return;
    }

    const mensagemOriginal = campoMensagem.value;

    function atualizarContador() {
        if (!contador) {
            return;
        }

        const quantidade = campoMensagem.value.length;

        contador.textContent =
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

    function bloquearEnvio() {
        if (!botaoEnviar) {
            return;
        }

        botaoEnviar.disabled = true;

        botaoEnviar.innerHTML = `
            <span
                class="spinner-border spinner-border-sm me-1"
                aria-hidden="true"
            ></span>
            Enviando...
        `;
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

    formulario?.addEventListener(
        "submit",
        bloquearEnvio
    );

    atualizarContador();
});