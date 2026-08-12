(function () {
    const root = document.querySelector('.catalog-review');
    if (!root) return;

    const cards = Array.from(root.querySelectorAll('.catalog-product-card'));
    const selectedCounter = document.getElementById('selected-count');
    const visibleCounter = document.getElementById('visible-count');
    const search = document.getElementById('catalog-search');
    const previewForm = document.getElementById('preview-form');
    const confirmButton = document.getElementById('confirm-import-button');
    let currentFilter = 'todos';


    function markDirty() {
        if (!confirmButton) return;
        confirmButton.disabled = true;
        confirmButton.title = 'Salve as alterações da conferência antes de confirmar a importação.';
        confirmButton.innerHTML = '<i class="bi bi-lock"></i> Salve antes de confirmar';
    }

    function activeVariationRows(card) {
        return Array.from(card.querySelectorAll('.var-row')).filter((row) => {
            const del = row.querySelector('input[type="hidden"][name$="-delete"]');
            return row.style.display !== 'none' && (!del || del.value !== '1');
        });
    }

    function refreshCardState(card) {
        const checkbox = card.querySelector('.include-item');
        card.classList.toggle('is-excluded', checkbox && !checkbox.checked);
        card.dataset.included = checkbox && checkbox.checked ? '1' : '0';
        card.dataset.noVariation = activeVariationRows(card).length ? '0' : '1';
        const alert = card.querySelector('.no-vars');
        if (alert) alert.hidden = card.dataset.noVariation !== '1';
    }

    function matchesFilter(card) {
        if (currentFilter === 'sem-cor') return card.dataset.noVariation === '1';
        if (currentFilter === 'duplicidades') return card.dataset.duplicate !== 'nenhuma';
        if (currentFilter === 'prontos') return card.dataset.noVariation === '0' && card.dataset.duplicate === 'nenhuma';
        if (currentFilter === 'selecionados') return card.dataset.included === '1';
        return true;
    }

    function applyFilters() {
        const term = (search?.value || '').trim().toLowerCase();
        let visible = 0;
        let selected = 0;
        cards.forEach((card) => {
            refreshCardState(card);
            if (card.dataset.included === '1') selected += 1;
            const text = card.dataset.search || '';
            const show = matchesFilter(card) && (!term || text.includes(term));
            card.classList.toggle('is-hidden', !show);
            if (show) visible += 1;
        });
        if (visibleCounter) visibleCounter.textContent = visible;
        if (selectedCounter) selectedCounter.textContent = selected;
    }

    function createVariation(item, index) {
        const container = document.getElementById(`variacoes-${item}`);
        const template = document.getElementById('nova-var-template');
        const clone = template.content.cloneNode(true);
        clone.querySelector('.nova-nome').name = `nova-${item}-nome`;
        const code = clone.querySelector('.nova-codigo');
        code.name = `nova-${item}-codigo`;
        code.value = `C${index}`;
        const chip = clone.querySelector('.catalog-code-chip');
        if (chip) chip.textContent = code.value;
        clone.querySelector('.nova-estoque').name = `nova-${item}-estoque`;
        const empty = container.querySelector('.no-vars');
        if (empty) empty.hidden = true;
        container.appendChild(clone);
        refreshCardState(container.closest('.catalog-product-card'));
    }

    document.querySelectorAll('.add-var').forEach((button) => {
        button.addEventListener('click', () => {
            const card = button.closest('.catalog-product-card');
            createVariation(button.dataset.item, activeVariationRows(card).length + 1);
            markDirty();
            applyFilters();
        });
    });

    document.querySelectorAll('.generate-vars').forEach((button) => {
        button.addEventListener('click', () => {
            const item = button.dataset.item;
            const card = button.closest('.catalog-product-card');
            const input = card.querySelector('.generate-count');
            const desiredTotal = Math.min(30, Math.max(1, parseInt(input.value || '1', 10)));
            const currentTotal = activeVariationRows(card).length;
            for (let next = currentTotal + 1; next <= desiredTotal; next += 1) createVariation(item, next);
            input.value = '';
            markDirty();
            applyFilters();
        });
    });

    document.addEventListener('click', (event) => {
        const existing = event.target.closest('.remove-existing');
        if (existing) {
            const row = existing.closest('.var-row');
            row.querySelector('input[type="hidden"]').value = '1';
            row.style.display = 'none';
            markDirty();
            applyFilters();
        }
        const novo = event.target.closest('.remove-new');
        if (novo) {
            novo.closest('.var-row').remove();
            markDirty();
            applyFilters();
        }
        const preview = event.target.closest('.catalog-thumb img');
        if (preview) {
            const card = preview.closest('.catalog-product-card');
            const main = card.querySelector('.catalog-main-image');
            if (main) main.src = preview.src;
        }
    });

    document.querySelectorAll('.include-item').forEach((checkbox) => checkbox.addEventListener('change', () => { markDirty(); applyFilters(); }));
    document.querySelectorAll('.primary-image-radio').forEach((radio) => {
        radio.addEventListener('change', () => {
            markDirty();
            const card = radio.closest('.catalog-product-card');
            card.querySelectorAll('.catalog-thumb').forEach((thumb) => thumb.classList.remove('is-primary'));
            radio.closest('.catalog-thumb').classList.add('is-primary');
            const img = radio.closest('.catalog-thumb').querySelector('img');
            const main = card.querySelector('.catalog-main-image');
            if (img && main) main.src = img.src;
        });
    });

    document.querySelectorAll('[data-filter]').forEach((button) => {
        button.addEventListener('click', () => {
            currentFilter = button.dataset.filter;
            document.querySelectorAll('[data-filter]').forEach((b) => b.classList.remove('active'));
            button.classList.add('active');
            applyFilters();
        });
    });
    if (search) search.addEventListener('input', applyFilters);
    if (previewForm) {
        previewForm.addEventListener('input', (event) => {
            if (!event.target.matches('#catalog-search')) markDirty();
        });
        previewForm.addEventListener('change', (event) => {
            if (!event.target.matches('#catalog-search')) markDirty();
        });
    }
    document.querySelectorAll('.catalog-main-image').forEach((image) => {
        image.addEventListener('click', () => window.open(image.src, '_blank', 'noopener'));
    });

    cards.forEach(refreshCardState);
    applyFilters();
})();

/* Relação visual C1..Cn entre a galeria e a tabela de variações. */
(() => {
    function activeRows(card) {
        return [...card.querySelectorAll('.catalog-variation-row.var-row')].filter((row) => {
            const del = row.querySelector('input[type="hidden"][name$="-delete"]');
            return row.style.display !== 'none' && (!del || del.value !== '1');
        });
    }

    function syncRowCode(row) {
        const input = row.querySelector('.variation-code-input, input[name$="-codigo"], .nova-codigo');
        const chip = row.querySelector('.catalog-code-chip');
        const value = (input?.value || '').trim().toUpperCase();
        if (chip) chip.textContent = value || '—';
    }

    function syncCardCodes(card) {
        const rows = activeRows(card);
        rows.forEach(syncRowCode);
        card.querySelectorAll('.catalog-variation-tile').forEach((tile) => {
            const index = Number(tile.dataset.variationIndex);
            const row = rows[index - 1];
            const input = row?.querySelector('.variation-code-input, input[name$="-codigo"], .nova-codigo');
            const code = (input?.value || `C${index}`).trim().toUpperCase() || `C${index}`;
            const badge = tile.querySelector('.catalog-tile-code');
            if (badge) badge.textContent = code;
        });
    }

    function activateVariation(card, index, { scroll = false } = {}) {
        card.querySelectorAll('.catalog-variation-tile, .catalog-variation-row').forEach((el) => {
            el.classList.remove('is-active', 'is-marker-active');
        });
        const tile = card.querySelector(`.catalog-variation-tile[data-variation-index="${index}"]`);
        const row = activeRows(card)[index - 1];
        tile?.classList.add('is-active');
        row?.classList.add('is-active');
        if (scroll && row) row.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    document.addEventListener('click', (event) => {
        const tile = event.target.closest('.catalog-variation-tile');
        if (tile) {
            const card = tile.closest('.catalog-product-card');
            activateVariation(card, Number(tile.dataset.variationIndex), { scroll: true });
            return;
        }
        const row = event.target.closest('.catalog-variation-row');
        if (row && row.dataset.variationIndex) {
            const card = row.closest('.catalog-product-card');
            activateVariation(card, Number(row.dataset.variationIndex));
        }
    });

    document.addEventListener('input', (event) => {
        if (!event.target.matches('.variation-code-input, input[name$="-codigo"], .nova-codigo')) return;
        const card = event.target.closest('.catalog-product-card');
        if (card) syncCardCodes(card);
    });

    document.querySelectorAll('.catalog-product-card').forEach(syncCardCodes);
})();
