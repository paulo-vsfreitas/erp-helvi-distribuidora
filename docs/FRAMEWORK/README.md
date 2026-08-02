# Framework Helvi

O Framework Helvi é a camada transversal já utilizada pelo ERP para padronizar arquitetura, interface, documentos e recursos reutilizáveis.

## Princípio

Nenhum módulo deve reinventar algo que já exista no Framework.

## Escopo

O Framework pode fornecer:

- layout e identidade visual;
- componentes estruturais;
- KPIs, cards, tabelas e estados vazios;
- fichas e resumos;
- mensagens e modais;
- formatação e template tags;
- helpers JavaScript;
- Framework PDF;
- contratos e nomenclatura.

Não deve absorver regras específicas de Compras, Vendas, Estoque, Comercial ou Financeiro.

## Estado atual

Já aplicado em diferentes níveis:

- arquitetura em camadas;
- base autenticada e base pública;
- fichas;
- cards;
- tabelas;
- forms;
- sidebar/topbar;
- permissões;
- autocompletes;
- resumos sticky;
- PDF;
- services e helpers compartilhados.

## Consolidação atual

A prioridade é consolidar o que já existe, eliminar duplicações e registrar contratos oficiais antes de criar novas abstrações.
