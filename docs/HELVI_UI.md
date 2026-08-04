# Helvi UI

Atualizado em 04/08/2026.

O Helvi UI complementa o Bootstrap e é carregado pelo template-base em todas as
páginas autenticadas.

## Fontes

- tokens e componentes: `static/helvi_ui/helvi-ui.css`;
- base interna: `core/templates/core/base.html`;
- componentes compartilhados: `core/templates/components/`;
- cabeçalho oficial: `core/templates/components/layout/page_header.html`;
- CSS estrutural legado/compatível: `static/css/`.

## Princípios

- Bootstrap cuida de grade, modal e interações básicas;
- Helvi UI cuida de identidade, espaçamento, cards e estruturas;
- CSS de módulo trata apenas comportamento específico;
- não redefinir Bootstrap globalmente sem homologação ampla;
- não criar variação nova de card/cabeçalho se já existir contrato;
- acessibilidade e texto permanecem compreensíveis sem depender só de cor.

## Estruturas

- `.hui-module-page`: página interna fluida;
- `.hui-form-page` e `.hui-form-section`: formulários;
- `.hui-detail-page`, `.hui-detail-hero` e `.hui-detail-section`: fichas;
- `.hui-entity-kpis`, `.hui-entity-filters`, `.hui-entity-panel`: listagens;
- `.hui-confirmation-page`: confirmações;
- `.hui-report-page`: relatórios;
- `.hui-form-actions`: ações finais consistentes.

## Regra de largura e zoom

`.hui-module-page` não recebe `max-width` local. O conteúdo acompanha a largura
útil do navegador. Em 04/08/2026, telas representativas ocuparam cerca de 96%
da área principal a 1920 px e não produziram overflow global a 768 px.

Ao encontrar uma tela estreita no centro, procure:

- `.container` ou `max-width` envolvendo a página;
- largura fixa em template de módulo;
- transform/zoom aplicado no conteúdo;
- padding duplicado entre base e página.

## Padrão de uma nova tela

1. herdar `core/base.html`;
2. abrir `.hui-module-page`;
3. usar cabeçalho oficial;
4. organizar conteúdo em cards/sections existentes;
5. garantir tabela responsiva;
6. validar desktop, tela ampla e 768 px;
7. conferir console e navegação por teclado nas ações principais.

## Compatibilidade

Há componentes históricos equivalentes em `core/templates/components/`. Eles
permanecem para não quebrar telas antigas. Não remova por nome: localize includes
reais e migre com testes.
