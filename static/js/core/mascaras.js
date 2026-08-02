window.Helvi = window.Helvi || {};

window.Helvi.initMasks = function () {
    const somenteNumeros = (valor) => {
        return (valor || "").replace(/\D/g, "");
    };

    const formatarTelefone = (valor) => {
        const numeros = somenteNumeros(valor).slice(0, 11);

        if (numeros.length <= 2) {
            return numeros
                ? `(${numeros}`
                : "";
        }

        if (numeros.length <= 6) {
            return `(${numeros.slice(0, 2)}) ${numeros.slice(2)}`;
        }

        if (numeros.length <= 10) {
            return (
                `(${numeros.slice(0, 2)}) ` +
                `${numeros.slice(2, 6)}-` +
                `${numeros.slice(6)}`
            );
        }

        return (
            `(${numeros.slice(0, 2)}) ` +
            `${numeros.slice(2, 7)}-` +
            `${numeros.slice(7)}`
        );
    };

    const formatarCpf = (valor) => {
        const numeros = somenteNumeros(valor).slice(0, 11);

        return numeros
            .replace(/^(\d{3})(\d)/, "$1.$2")
            .replace(/^(\d{3})\.(\d{3})(\d)/, "$1.$2.$3")
            .replace(/\.(\d{3})(\d)/, ".$1-$2");
    };

    const formatarCnpj = (valor) => {
        const numeros = somenteNumeros(valor).slice(0, 14);

        return numeros
            .replace(/^(\d{2})(\d)/, "$1.$2")
            .replace(/^(\d{2})\.(\d{3})(\d)/, "$1.$2.$3")
            .replace(/\.(\d{3})(\d)/, ".$1/$2")
            .replace(/(\d{4})(\d)/, "$1-$2");
    };

    const formatarCpfCnpj = (valor) => {
        const numeros = somenteNumeros(valor);

        if (numeros.length <= 11) {
            return formatarCpf(numeros);
        }

        return formatarCnpj(numeros);
    };

    const formatarCep = (valor) => {
        const numeros = somenteNumeros(valor).slice(0, 8);

        return numeros.replace(
            /^(\d{5})(\d)/,
            "$1-$2"
        );
    };

    const formatadores = {
        telefone: formatarTelefone,
        whatsapp: formatarTelefone,
        cpf: formatarCpf,
        cnpj: formatarCnpj,
        "cpf-cnpj": formatarCpfCnpj,
        cep: formatarCep,
    };

    document
        .querySelectorAll("[data-mask]")
        .forEach((campo) => {
            if (campo.dataset.maskInitialized === "true") {
                return;
            }

            const tipo = campo.dataset.mask;
            const formatador = formatadores[tipo];

            if (!formatador) {
                return;
            }

            campo.dataset.maskInitialized = "true";

            const aplicarMascara = () => {
                const posicaoAnterior = campo.selectionStart;
                const valorAnterior = campo.value;

                campo.value = formatador(campo.value);

                if (
                    document.activeElement === campo
                    && posicaoAnterior !== null
                    && campo.value.length >= valorAnterior.length
                ) {
                    campo.setSelectionRange(
                        campo.value.length,
                        campo.value.length
                    );
                }
            };

            campo.addEventListener(
                "input",
                aplicarMascara
            );

            campo.addEventListener(
                "blur",
                aplicarMascara
            );

            aplicarMascara();
        });
};