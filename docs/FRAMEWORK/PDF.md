# Framework PDF — ERP Helvi

## Objetivo

Centralizar a geração de documentos, garantindo identidade visual, reutilização e manutenção única.

## Estrutura

```text
core/pdf/
├── assets/
├── documents/
├── elements/
├── colors.py
├── document.py
├── footer.py
├── header.py
├── styles.py
├── tables.py
└── utils.py
```

## Regras

- documentos usam `HelviPDF`;
- não criar `SimpleDocTemplate` diretamente quando a base atende;
- cores ficam em `colors.py`;
- estilos ficam em `styles.py`;
- blocos reutilizáveis ficam em `elements`;
- tabelas reutilizáveis ficam em `tables.py`;
- documentos apenas organizam componentes;
- formatação monetária deve reutilizar o formatador oficial do Framework.

## Documentos atuais

- PDF de Compra;
- PDF de Orçamento.

## Evoluções

- PDF de Venda;
- recibo;
- comprovante/cupom;
- etiquetas;
- relatórios.

## Status

Framework em uso e homologado nos documentos já validados, com pendência de consolidar formatadores duplicados.
