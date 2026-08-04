# Componentes do Framework Helvi

## Layout

- base autenticada: `core/templates/core/base.html`;
- base pública: `core/templates/public/base_public.html`;
- sidebar/topbar: componentes carregados pela base;
- cabeçalho canônico de módulo:
  `core/templates/components/layout/page_header.html`;
- componentes Helvi UI: `core/templates/helvi_ui/`.

## Componentes Helvi UI

- `helvi_ui/page_header.html`;
- `helvi_ui/section_card.html`;
- `helvi_ui/empty_state.html`;
- `helvi_ui/action_bar.html`.

## Componentes compartilhados úteis

- cards: `components/cards/`;
- filtros: `components/filters/filter_card.html`;
- ficha: `components/ficha/`;
- tabelas: `components/tables/`;
- estados: `components/states/`;
- confirmações: `components/states/confirmation_page.html`;
- modais: `components/modals/`;
- paginação: `components/tables/pagination.html`.

## Contratos visuais

### Página de módulo

```html
<div class="hui-module-page hui-module-page--modulo">
    {% include "components/layout/page_header.html" with titulo=titulo subtitulo=subtitulo %}
    ...
</div>
```

Não envolver com contêiner de largura máxima local.

### Ficha

Uma ficha pode reunir:

- cabeçalho e ações;
- indicadores;
- dados gerais;
- itens/parcelas;
- resumo lateral;
- histórico e movimentações;
- observações.

### Listagem

- cabeçalho com ação primária;
- filtros dentro de card;
- resumo do resultado;
- tabela responsiva;
- estado vazio;
- ações por linha consistentes.

### Confirmação

A tela de confirmação mostra objeto, consequência e botões. A alteração real é
feita por POST. Motivo é obrigatório em cancelamentos/estornos que exigem
rastreabilidade.

## Componentes legados

Há arquivos de nomes semelhantes em `components/`, `components/ui/` e
`components/cards/`. Eles permanecem por compatibilidade. Antes de removê-los:

1. localizar todos os `{% include %}`;
2. escolher um contrato canônico;
3. migrar módulo por módulo;
4. homologar as 19 telas;
5. remover somente arquivos sem uso comprovado.

Não criar uma quarta variante.
