# Framework PDF — ERP Helvi

## Objetivo

Centralizar identidade visual e recursos ReportLab para documentos do ERP.

## Estrutura

```text
core/pdf/
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

## Contrato

- usar `HelviPDF`;
- cores e estilos ficam em seus módulos compartilhados;
- elementos reutilizáveis ficam em `elements/`;
- documents organizam o conteúdo do domínio;
- o retorno de `build()` é o documento em bytes/estrutura definida pela base;
- dinheiro deve convergir para o formatador oficial;
- nenhum PDF deve buscar dados adicionais dentro do template de apresentação.

## Estado atual

- `CompraPDF`: implementado e exposto pelo módulo Compras;
- `OrcamentoPDF`: implementado, usado em download e e-mail;
- arquivos `venda.py`, `recibo.py`, `etiqueta.py` e `relatorio.py`: scaffolds
  vazios, sem documento funcional; não considerar implementados.

O PDF de orçamento ainda possui um formatador monetário local compatível. A
migração para `core.formatters.formatar_moeda_br` está no backlog técnico.

## Como adicionar um documento

1. confirmar requisito e rota;
2. criar testes de conteúdo essencial;
3. reutilizar header, footer, estilos e elementos;
4. gerar o documento no service/view apropriado;
5. validar visualmente várias quantidades de itens e quebra de página;
6. registrar o documento neste arquivo e no changelog.
