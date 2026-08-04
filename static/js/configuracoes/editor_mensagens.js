document.addEventListener("DOMContentLoaded", () => {
    const editores = Array.from(
        document.querySelectorAll("[data-mensagem-editor]")
    );
    const botoes = document.querySelectorAll("[data-mensagem-variavel]");
    const contextoNode = document.getElementById("contexto-exemplo-mensagem");

    if (!editores.length || !contextoNode) {
        return;
    }

    const contexto = JSON.parse(contextoNode.textContent);
    let editorAtivo = editores[0];

    function renderizar(modelo) {
        return modelo.replace(/\{([A-Z_]+)\}/g, (trecho, nome) => (
            Object.hasOwn(contexto, nome) ? contexto[nome] : trecho
        ));
    }

    function atualizar(editor) {
        const campo = editor.closest(".mensagem-editor-campo");
        const previa = campo?.querySelector("[data-mensagem-previa]");
        const status = campo?.querySelector(".mensagem-editor-status");
        const quantidade = editor.value.length;

        if (previa) {
            previa.textContent = editor.value
                ? renderizar(editor.value)
                : "O modelo original do sistema será utilizado.";
        }
        if (status) {
            status.textContent = `${quantidade} caractere${quantidade === 1 ? "" : "s"}`;
        }
    }

    function ativar(editor) {
        editorAtivo = editor;
        editores.forEach((item) => {
            item.closest(".mensagem-editor-campo")?.classList.toggle(
                "is-active",
                item === editor
            );
        });
    }

    function inserirVariavel(nome) {
        const token = `{${nome}}`;
        const inicio = editorAtivo.selectionStart ?? editorAtivo.value.length;
        const fim = editorAtivo.selectionEnd ?? inicio;

        editorAtivo.setRangeText(token, inicio, fim, "end");
        editorAtivo.dispatchEvent(new Event("input", { bubbles: true }));
        editorAtivo.focus();
    }

    editores.forEach((editor) => {
        editor.addEventListener("focus", () => ativar(editor));
        editor.addEventListener("click", () => ativar(editor));
        editor.addEventListener("input", () => atualizar(editor));
        atualizar(editor);
    });

    botoes.forEach((botao) => {
        botao.addEventListener("click", () => {
            inserirVariavel(botao.dataset.mensagemVariavel);
        });
    });

    ativar(editorAtivo);
});
