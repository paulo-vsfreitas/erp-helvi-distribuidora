window.Helvi = window.Helvi || {};

window.Helvi.initCep = function () {
    const cepInputs = document.querySelectorAll(
        '[data-cep-autocomplete="true"]'
    );

    cepInputs.forEach((cepInput) => {
        if (cepInput.dataset.cepInitialized === "true") {
            return;
        }

        cepInput.dataset.cepInitialized = "true";

        const fields = {
            logradouro: document.getElementById(
                cepInput.dataset.logradouroTarget
            ),
            bairro: document.getElementById(
                cepInput.dataset.bairroTarget
            ),
            cidade: document.getElementById(
                cepInput.dataset.cidadeTarget
            ),
            estado: document.getElementById(
                cepInput.dataset.estadoTarget
            ),
            complemento: document.getElementById(
                cepInput.dataset.complementoTarget
            ),
            numero: document.getElementById(
                cepInput.dataset.numeroTarget || "id_numero"
            ),
        };

        const somenteNumeros = (valor) => {
            return (valor || "").replace(/\D/g, "");
        };

        const preencherCampo = (
            campo,
            valor,
            sobrescrever = true
        ) => {
            if (!campo || !valor) {
                return;
            }

            if (sobrescrever || !campo.value.trim()) {
                campo.value = valor;

                campo.dispatchEvent(
                    new Event("input", {
                        bubbles: true,
                    })
                );

                campo.dispatchEvent(
                    new Event("change", {
                        bubbles: true,
                    })
                );
            }
        };

        const obterContainerFeedback = () => {
            return (
                cepInput.closest(".configuracoes-field")
                || cepInput.closest(".form-group")
                || cepInput.parentElement
            );
        };

        const removerFeedback = () => {
            const container = obterContainerFeedback();

            const feedback = container?.querySelector(
                ".cep-autocomplete-feedback"
            );

            if (feedback) {
                feedback.remove();
            }
        };

        const limparEstadoVisual = () => {
            cepInput.classList.remove(
                "is-invalid",
                "is-valid"
            );

            removerFeedback();
        };

        const marcarInvalido = (mensagem) => {
            cepInput.classList.remove("is-valid");
            cepInput.classList.add("is-invalid");

            removerFeedback();

            const feedback = document.createElement("div");

            feedback.className =
                "configuracoes-error cep-autocomplete-feedback";

            feedback.textContent = mensagem;

            obterContainerFeedback()?.appendChild(feedback);
        };

        const marcarValido = () => {
            cepInput.classList.remove("is-invalid");
            cepInput.classList.add("is-valid");

            removerFeedback();
        };

        const buscarCep = async () => {
            const cep = somenteNumeros(cepInput.value);

            limparEstadoVisual();

            if (!cep) {
                return;
            }

            if (cep.length !== 8) {
                marcarInvalido(
                    "Informe um CEP válido com 8 números."
                );
                return;
            }

            cepInput.readOnly = true;
            cepInput.setAttribute("aria-busy", "true");

            try {
                const response = await fetch(
                    `https://viacep.com.br/ws/${cep}/json/`
                );

                if (!response.ok) {
                    throw new Error(
                        "Falha na consulta do CEP."
                    );
                }

                const endereco = await response.json();

                if (endereco.erro) {
                    marcarInvalido(
                        "CEP não encontrado."
                    );
                    return;
                }

                preencherCampo(
                    fields.logradouro,
                    endereco.logradouro
                );

                preencherCampo(
                    fields.bairro,
                    endereco.bairro
                );

                preencherCampo(
                    fields.cidade,
                    endereco.localidade
                );

                preencherCampo(
                    fields.estado,
                    endereco.uf
                );

                preencherCampo(
                    fields.complemento,
                    endereco.complemento,
                    false
                );

                marcarValido();

                if (fields.numero) {
                    fields.numero.focus();
                } else if (fields.logradouro) {
                    fields.logradouro.focus();
                }
            } catch (error) {
                marcarInvalido(
                    "Não foi possível consultar o CEP agora. " +
                    "Preencha o endereço manualmente."
                );
            } finally {
                cepInput.readOnly = false;
                cepInput.removeAttribute("aria-busy");
            }
        };

        cepInput.addEventListener(
            "blur",
            buscarCep
        );

        cepInput.addEventListener(
            "input",
            () => {
                limparEstadoVisual();

                const cep = somenteNumeros(
                    cepInput.value
                );

                if (cep.length === 8) {
                    buscarCep();
                }
            }
        );
    });
};