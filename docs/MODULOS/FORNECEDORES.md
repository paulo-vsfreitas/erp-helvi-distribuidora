# Módulo Fornecedores

Atualizado em 04/08/2026.

## Responsabilidade

Manter os dados dos fornecedores e apresentar seu relacionamento operacional
com as compras.

## Implementado

- dashboard;
- listagem limpa e padronizada;
- pesquisa por dados relevantes;
- filtros de situação e relacionamento;
- cadastro e edição;
- ficha;
- inativação/reativação conforme as ações do módulo;
- identificação fiscal e contatos;
- indicadores de compras;
- componentes de listagem próprios reutilizáveis;
- integração com Compras e Contas a Pagar;
- testes de dashboard e listagem.

## Regras

- fornecedor com histórico não deve ser excluído;
- nome e documento devem permanecer disponíveis para rastreabilidade;
- compras preservam o vínculo e os dados apresentados;
- listagens não devem executar agregações repetitivas por linha.

## Arquivos principais

- models: `fornecedores/models.py`;
- forms: `fornecedores/forms/`;
- services: `fornecedores/services/`;
- views: `fornecedores/views/`;
- templates: `fornecedores/templates/fornecedores/`;
- testes: `fornecedores/tests.py`.

## Evoluções não bloqueantes

- avaliação de fornecedor;
- prazos médios e desempenho de entrega;
- anexos e documentos;
- relatório analítico de compras e custos.
