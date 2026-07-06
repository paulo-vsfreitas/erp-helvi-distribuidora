console.log("modal_busca.js v3 carregado");

window.HelviModalBusca = function (config) {
    console.log("HelviModalBusca v3 inicializado");

    const modal = document.querySelector(config.modal);
    const input = document.querySelector(config.input);
    const resultados = document.querySelector(config.resultados);
    const abrir = document.querySelector(config.abrir);

    const botoesFechar = modal.querySelectorAll("[data-modal-close]");

    function fecharModal() {
        modal.hidden = true;
        input.value = "";
        resultados.innerHTML = "";
    }

    function abrirModal() {
        modal.classList.remove("d-none");

        setTimeout(() => {
            input.focus();
        }, 100);
    }

    function abrirModal() {
        modal.hidden = false;

        setTimeout(() => {
            input.focus();
        }, 100);
    }

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            fecharModal();
        }
    });

    input.addEventListener("input", async () => {
        const termo = input.value.trim();

        resultados.innerHTML = "";

        if (termo.length < 2) {
            return;
        }

        const response = await fetch(
            `${config.url}?q=${encodeURIComponent(termo)}`
        );

        const data = await response.json();

        if (!data.resultados.length) {
            resultados.innerHTML = `<p class="text-muted">Nenhum resultado encontrado.</p>`;
            return;
        }

        data.resultados.forEach((item) => {
            const botao = document.createElement("button");

            botao.type = "button";
            botao.className = "produto-resultado-item";
            botao.innerHTML = config.render(item);

            botao.addEventListener("click", () => {
                config.onSelect(item);
                fecharModal();
            });

            resultados.appendChild(botao);
        });
    });
};