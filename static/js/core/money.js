window.Helvi = window.Helvi || {};

window.Helvi.money = {

    parse(valor) {
        if (valor === null || valor === undefined) {
            return 0;
        }

        if (typeof valor === "number") {
            return Number.isFinite(valor)
                ? valor
                : 0;
        }

        let texto = String(valor)
            .trim()
            .replace(/\s/g, "")
            .replace(/^R\$\s?/, "");

        if (!texto) {
            return 0;
        }

        const possuiVirgula = texto.includes(",");
        const possuiPonto = texto.includes(".");

        /*
        * Formato brasileiro com milhar:
        * 1.250,90 -> 1250.90
        */
        if (possuiVirgula && possuiPonto) {
            texto = texto
                .replace(/\./g, "")
                .replace(",", ".");
        }

        /*
        * Formato brasileiro sem milhar:
        * 35,90 -> 35.90
        */
        else if (possuiVirgula) {
            texto = texto.replace(",", ".");
        }

        /*
        * Formato decimal padrão:
        * 35.90 -> 35.90
        *
        * Não removemos o ponto.
        */
        const numero = Number(texto);

        return Number.isFinite(numero)
            ? numero
            : 0;
    },

    decimal(valor, casas = 2) {

        return this.parse(valor).toFixed(casas);

    },

    currency(valor) {

        return this.parse(valor).toLocaleString(
            "pt-BR",
            {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
            }
        );

    },

    integer(valor) {

        return Math.round(
            this.parse(valor)
        );

    },

};