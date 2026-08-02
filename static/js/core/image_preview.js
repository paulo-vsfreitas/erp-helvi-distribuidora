window.Helvi = window.Helvi || {};

window.Helvi.initImagePreview = function () {

    document
        .querySelectorAll("[data-image-preview]")
        .forEach((input) => {

            if (input.dataset.previewInitialized === "true") {
                return;
            }

            input.dataset.previewInitialized = "true";

            const preview = document.querySelector(
                input.dataset.previewTarget
            );

            const placeholder = document.querySelector(
                input.dataset.placeholderTarget
            );

            if (!preview) {
                return;
            }

            input.addEventListener("change", () => {

                const arquivo = input.files?.[0];

                if (!arquivo) {

                    if (preview.src === "") {
                        preview.classList.add("d-none");

                        if (placeholder) {
                            placeholder.classList.remove("d-none");
                        }
                    }

                    return;
                }

                if (!arquivo) {
                    return;
                }

                if (!arquivo.type.startsWith("image/")) {
                    return;
                }

                const reader = new FileReader();

                reader.onload = (evento) => {

                    preview.src = evento.target.result;

                    preview.classList.remove("d-none");

                    if (placeholder) {
                        placeholder.classList.add("d-none");
                    }

                };

                reader.readAsDataURL(arquivo);

            });

        });

};