# Módulo Financeiro

Atualizado em 04/08/2026.

## Escopo

- categorias financeiras;
- contas financeiras;
- Contas a Pagar e parcelas;
- Contas a Receber e parcelas;
- baixas e recebimentos;
- estornos;
- movimentações e fluxo de caixa;
- dashboard e históricos;
- integrações com Compras e Vendas.

## Implementado

- cadastros e listagens com filtros;
- fichas de contas e movimentos;
- lançamentos manuais;
- geração automática por compra/venda;
- pagamento parcial ou total;
- recebimento parcial ou total;
- juros, multa e desconto;
- estorno de baixa a pagar;
- estorno de recebimento;
- movimento inverso no caixa;
- recálculo de parcela e conta;
- motivo, usuário, data e histórico;
- prevenção de estorno duplicado;
- dashboard e próximos vencimentos;
- fluxo de caixa com entradas, saídas e estornos.
- fluxo de caixa com período mensal padrão e saldo anterior sem duplicar os
  movimentos exibidos;
- análise de lucro e margem por período e por venda finalizada;
- receita dos produtos, custo histórico das mercadorias, lucro bruto, margem,
  quantidade vendida e frete discriminado.

## Regras críticas

- valores principais são positivos;
- juros, multa e desconto não são negativos;
- valor pago/recebido não supera o original;
- conta cancelada não recebe nova baixa;
- conta financeira inativa não recebe movimento;
- estorno preserva a operação original;
- saldo considera o sinal do tipo da movimentação;
- operações compostas são transacionais.

## Arquivos principais

- models: `financeiro/models.py`;
- services: `financeiro/services/`;
- views: `financeiro/views/`;
- templates: `financeiro/templates/financeiro/`;
- testes de estorno: `financeiro/tests.py`.

## Relatórios

O dashboard e as listas fornecem a visão operacional da versão 1.0. A página
**Financeiro → Lucro e Margem** apresenta a rentabilidade comercial com o custo
unitário preservado na finalização da venda. Esse indicador é lucro bruto; uma
apuração líquida contábil depende do lançamento completo de impostos, taxas,
despesas operacionais e custos logísticos.

## Manutenção

Não corrija valores diretamente no banco quando existir baixa, recebimento,
estorno ou integração de origem. Use services e execute a auditoria ao final.
