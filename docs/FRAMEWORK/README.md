# Framework Helvi

O Framework Helvi é a camada transversal do ERP. Ele padroniza interface,
formatação, comunicação, PDFs e contratos de desenvolvimento sem absorver
regras específicas de negócio.

## Componentes atuais

```text
core/
├── communication/          e-mail e preparação de canais
├── pdf/                    geração de documentos ReportLab
├── templates/
│   ├── components/         componentes compartilhados e compatibilidade
│   └── helvi_ui/           componentes canônicos recentes
├── templatetags/moeda.py   filtro oficial de moeda
├── formatters.py           formatação Python oficial
└── management/commands/    auditoria e conciliação

static/helvi_ui/
└── helvi-ui.css            tokens e estruturas visuais
```

## Princípios

- reutilizar antes de criar;
- manter regra de negócio no módulo;
- extrair abstrações somente após contrato estável;
- não duplicar formatação ou componente visual;
- preservar compatibilidade e migrar legados com testes;
- documentar o componente canônico.

## Estado

O Framework está aplicado nas 19 telas principais e nos fluxos públicos. Existem
aliases e componentes históricos em `core/templates/components/`; eles não
devem ser copiados nem ampliados sem confirmar qual versão é usada. Novos
trabalhos devem preferir `core/templates/helvi_ui/` e os componentes canônicos
citados em `COMPONENTES.md`.

Também existem formatadores locais legados em alguns services e um formatador
interno no PDF de orçamento. Eles funcionam, mas devem convergir gradualmente
para `core.formatters.formatar_moeda_br`.

## O que não pertence ao Framework

- cálculo de orçamento ou venda;
- recebimento de compra;
- baixa de estoque;
- criação de contas e parcelas;
- cancelamentos e transições de domínio.

Essas regras permanecem nos services de cada aplicação.
