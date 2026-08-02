window.Helvi = window.Helvi || {};

document.addEventListener(
    "DOMContentLoaded",
    () => {
        window.Helvi.initMasks?.();
        window.Helvi.initCep?.();
        window.Helvi.initMoney?.();
        window.Helvi.initImagePreview?.();
        window.Helvi.initAutocomplete?.();
    }
);