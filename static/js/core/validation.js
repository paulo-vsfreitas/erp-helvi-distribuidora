document.addEventListener("DOMContentLoaded", function () {
    iniciarMascaras();
});


function iniciarMascaras() {
    const camposCnpj = document.querySelectorAll('[data-mask="cnpj"]');
    const camposCpf = document.querySelectorAll('[data-mask="cpf"]');
    const camposCpfCnpj = document.querySelectorAll('[data-mask="cpf-cnpj"]');
    const camposTelefone = document.querySelectorAll('[data-mask="telefone"]');

    camposCnpj.forEach(function (campo) {
        configurarMascara(campo, aplicarMascaraCnpj);
    });

    camposCpf.forEach(function (campo) {
        configurarMascara(campo, aplicarMascaraCpf);
    });

    camposCpfCnpj.forEach(function (campo) {
        configurarMascara(campo, aplicarMascaraCpfCnpj);
    });

    camposTelefone.forEach(function (campo) {
        configurarMascara(campo, aplicarMascaraTelefone);
    });
}


function configurarMascara(campo, funcaoMascara) {
    campo.value = funcaoMascara(campo.value);

    campo.addEventListener("input", function () {
        campo.value = funcaoMascara(campo.value);
    });
}


function somenteNumeros(valor) {
    return String(valor || "").replace(/\D/g, "");
}


function aplicarMascaraCnpj(valor) {
    const numeros = somenteNumeros(valor).slice(0, 14);

    if (numeros.length <= 2) {
        return numeros;
    }

    if (numeros.length <= 5) {
        return numeros.replace(
            /^(\d{2})(\d+)/,
            "$1.$2"
        );
    }

    if (numeros.length <= 8) {
        return numeros.replace(
            /^(\d{2})(\d{3})(\d+)/,
            "$1.$2.$3"
        );
    }

    if (numeros.length <= 12) {
        return numeros.replace(
            /^(\d{2})(\d{3})(\d{3})(\d+)/,
            "$1.$2.$3/$4"
        );
    }

    return numeros.replace(
        /^(\d{2})(\d{3})(\d{3})(\d{4})(\d+)/,
        "$1.$2.$3/$4-$5"
    );
}


function aplicarMascaraCpf(valor) {
    const numeros = somenteNumeros(valor).slice(0, 11);

    if (numeros.length <= 3) {
        return numeros;
    }

    if (numeros.length <= 6) {
        return numeros.replace(
            /^(\d{3})(\d+)/,
            "$1.$2"
        );
    }

    if (numeros.length <= 9) {
        return numeros.replace(
            /^(\d{3})(\d{3})(\d+)/,
            "$1.$2.$3"
        );
    }

    return numeros.replace(
        /^(\d{3})(\d{3})(\d{3})(\d+)/,
        "$1.$2.$3-$4"
    );
}


function aplicarMascaraCpfCnpj(valor) {
    const numeros = somenteNumeros(valor);

    if (numeros.length <= 11) {
        return aplicarMascaraCpf(numeros);
    }

    return aplicarMascaraCnpj(numeros);
}


function aplicarMascaraTelefone(valor) {
    const numeros = somenteNumeros(valor).slice(0, 11);

    if (!numeros) {
        return "";
    }

    if (numeros.length <= 2) {
        return `(${numeros}`;
    }

    const ddd = numeros.slice(0, 2);
    const numero = numeros.slice(2);

    if (numero.length <= 4) {
        return `(${ddd}) ${numero}`;
    }

    if (numeros.length <= 10) {
        return `(${ddd}) ${numero.slice(0, 4)}-${numero.slice(4)}`;
    }

    return `(${ddd}) ${numero.slice(0, 5)}-${numero.slice(5)}`;
}