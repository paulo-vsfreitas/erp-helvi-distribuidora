document.addEventListener("DOMContentLoaded", () => {
    const cepInput = document.querySelector('[data-cep-autocomplete="true"]');

    if (!cepInput) {
        return;
    }

    const fields = {
        logradouro: document.getElementById(cepInput.dataset.logradouroTarget),
        bairro: document.getElementById(cepInput.dataset.bairroTarget),
        cidade: document.getElementById(cepInput.dataset.cidadeTarget),
        estado: document.getElementById(cepInput.dataset.estadoTarget),
        complemento: document.getElementById(
            cepInput.dataset.complementoTarget
        ),
    };

    const somenteNumeros = (valor) => valor.replace(/\D/g, "");

    const preencherCampo = (campo, valor, sobrescrever = true) => {
        if (!campo || !valor) {
            return;
        }

        if (sobrescrever || !campo.value.trim()) {
            campo.value = valor;
            campo.dispatchEvent(new Event("change", { bubbles: true }));
        }
    };

    const limparEstadoVisual = () => {
        cepInput.classList.remove("is-invalid", "is-valid");
    };

    const marcarInvalido = (mensagem) => {
        cepInput.classList.remove("is-valid");
        cepInput.classList.add("is-invalid");

        let feedback = cepInput.parentElement.querySelector(
            ".cep-autocomplete-feedback"
        );

        if (!feedback) {
            feedback = document.createElement("div");
            feedback.className =
                "invalid-feedback cep-autocomplete-feedback";
            cepInput.parentElement.appendChild(feedback);
        }

        feedback.textContent = mensagem;
    };

    const marcarValido = () => {
        cepInput.classList.remove("is-invalid");
        cepInput.classList.add("is-valid");

        const feedback = cepInput.parentElement.querySelector(
            ".cep-autocomplete-feedback"
        );

        if (feedback) {
            feedback.remove();
        }
    };

    const buscarCep = async () => {
        const cep = somenteNumeros(cepInput.value);

        limparEstadoVisual();

        if (!cep) {
            return;
        }

        if (cep.length !== 8) {
            marcarInvalido("Informe um CEP válido com 8 números.");
            return;
        }

        cepInput.disabled = true;

        try {
            const response = await fetch(
                `https://viacep.com.br/ws/${cep}/json/`
            );

            if (!response.ok) {
                throw new Error("Falha na consulta do CEP.");
            }

            const endereco = await response.json();

            if (endereco.erro) {
                marcarInvalido("CEP não encontrado.");
                return;
            }

            preencherCampo(fields.logradouro, endereco.logradouro);
            preencherCampo(fields.bairro, endereco.bairro);
            preencherCampo(fields.cidade, endereco.localidade);
            preencherCampo(fields.estado, endereco.uf);
            preencherCampo(
                fields.complemento,
                endereco.complemento,
                false
            );

            marcarValido();

            if (fields.logradouro) {
                fields.logradouro.focus();
            }
        } catch (error) {
            marcarInvalido(
                "Não foi possível consultar o CEP agora. " +
                "Preencha o endereço manualmente."
            );
        } finally {
            cepInput.disabled = false;
        }
    };

    cepInput.addEventListener("blur", buscarCep);

    cepInput.addEventListener("input", () => {
        limparEstadoVisual();

        const cep = somenteNumeros(cepInput.value);

        if (cep.length === 8) {
            buscarCep();
        }
    });
});