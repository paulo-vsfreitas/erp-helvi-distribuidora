# Módulo Compras

Atualizado em 04/08/2026.

## Fluxo

```text
Compra
→ fornecedor
→ itens e condições
→ pagamentos previstos
→ recebimento
→ estoque e custo
→ Conta a Pagar
→ ficha/PDF/histórico
```

## Implementado

- nova compra e edição permitida pelos estados;
- fornecedor cadastrado;
- busca e inclusão de produtos;
- itens, frete, desconto, pagamentos e total;
- numeração comercial segura;
- listagem com busca, status e pagamento;
- cards de total, valor, recebidas e pendentes;
- ficha;
- recebimento;
- entrada idempotente no estoque;
- atualização do custo do produto;
- Conta a Pagar e parcelas;
- cancelamento com validação e estorno permitido;
- PDF;
- conciliação de compras históricas sem financeiro;
- testes de numeração, integração, recebimento e cancelamento.

## Regras críticas

- compra recebida gera no máximo uma entrada de estoque;
- compra recebida gera no máximo uma Conta a Pagar;
- recebimento atualiza custo e saldo na mesma operação;
- cancelamento não pode deixar estoque negativo;
- compra recebida não pode ser editada de forma a alterar o histórico;
- compras #1 e #3 foram conciliadas em 04/08/2026, total R$ 2.223,00;
- o comando de conciliação deve sempre ser executado primeiro sem `--aplicar`.

## Arquivos principais

- models: `compras/models.py`;
- services: `compras/services/`;
- views: `compras/views/`;
- templates: `compras/templates/compras/`;
- testes: `compras/tests.py`.

## Manutenção

Ao alterar itens, recebimento ou pagamento, execute:

- testes de Compras, Estoque e Financeiro;
- `auditar_integracoes`;
- `reconciliar_compras` em modo de leitura;
- conferência da ficha e do PDF.

## Evoluções não bloqueantes

- importação de XML/documento de fornecedor;
- aprovação de compra;
- análise avançada de custos;
- anexos e documentos adicionais.
