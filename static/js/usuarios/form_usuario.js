document.addEventListener("DOMContentLoaded", function () {
    const alternadoresSenha = document.querySelectorAll(
        ".hui-password-toggle"
    );

    alternadoresSenha.forEach(function (botao) {
        botao.addEventListener("click", function () {
            const campo = document.getElementById(
                botao.dataset.passwordTarget
            );

            if (!campo) {
                return;
            }

            const exibindo = campo.type === "text";
            campo.type = exibindo ? "password" : "text";
            botao.setAttribute(
                "aria-label",
                exibindo ? "Mostrar senha" : "Ocultar senha"
            );

            const icone = botao.querySelector("i");
            if (icone) {
                icone.className = exibindo
                    ? "bi bi-eye"
                    : "bi bi-eye-slash";
            }
        });
    });

    const campoFoto = document.querySelector(
        ".hui-user-photo-input"
    );
    const previewFoto = document.querySelector(
        "[data-user-photo-preview]"
    );

    if (campoFoto && previewFoto) {
        campoFoto.addEventListener("change", function () {
            const arquivo = campoFoto.files && campoFoto.files[0];

            if (!arquivo) {
                return;
            }

            const imagem = document.createElement("img");
            imagem.alt = "Prévia da nova foto do usuário";
            imagem.src = URL.createObjectURL(arquivo);
            imagem.addEventListener("load", function () {
                URL.revokeObjectURL(imagem.src);
            });

            previewFoto.replaceChildren(imagem);
        });
    }

    const campoAtivo = document.querySelector(
        ".hui-user-switch-input"
    );
    const badgeAtivo = document.querySelector(
        "[data-user-status-badge]"
    );

    function atualizarSituacao() {
        if (!campoAtivo || !badgeAtivo) {
            return;
        }

        const ativo = campoAtivo.checked;
        const texto = badgeAtivo.querySelector("span");
        const icone = badgeAtivo.querySelector("i");

        badgeAtivo.classList.toggle("is-inactive", !ativo);

        if (texto) {
            texto.textContent = ativo ? "Conta ativa" : "Conta inativa";
        }

        if (icone) {
            icone.className = ativo
                ? "bi bi-check-circle"
                : "bi bi-dash-circle";
        }
    }

    if (campoAtivo) {
        campoAtivo.addEventListener("change", atualizarSituacao);
        atualizarSituacao();
    }

    const campoPerfil = document.getElementById("id_perfil");
    const descricaoPerfil = document.querySelector(
        "[data-profile-description]"
    );
    const descricoes = {
        ADM: "Acesso administrativo completo a todos os módulos do ERP.",
        GER: "Acesso gerencial aos módulos operacionais e aos relatórios.",
        VEN: "Acesso a vendas, orçamentos, clientes, produtos e estoque.",
        FIN: "Acesso ao financeiro, recebimentos, pagamentos e fluxo de caixa.",
    };

    function atualizarPerfil() {
        if (!campoPerfil || !descricaoPerfil) {
            return;
        }

        descricaoPerfil.textContent =
            descricoes[campoPerfil.value]
            || "Permissões de acesso definidas conforme o perfil selecionado.";
    }

    if (campoPerfil) {
        campoPerfil.addEventListener("change", atualizarPerfil);
        atualizarPerfil();
    }
});
