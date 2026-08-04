# Módulo Vendas

Atualizado em 04/08/2026.

## Fluxo

```text
Venda direta ou orçamento convertido
→ cliente opcional
→ produtos
→ pagamento
→ finalização
→ baixa de estoque
→ Conta a Receber/recebimento
→ ficha e relatório
```

## Implementado

- nova venda com Helvi UI;
- venda para cliente cadastrado ou consumidor final;
- itens, quantidade, unitário, desconto, frete e totais;
- pagamento à vista e a prazo;
- troco e valor recebido;
- listagem com filtros;
- ficha;
- numeração comercial;
- vínculo com orçamento;
- finalização integrada;
- baixa de estoque;
- Conta a Receber e movimentação financeira;
- cancelamento por POST com motivo;
- devolução de estoque e reversão/cancelamento financeiro;
- relatório de vendas;
- constraints monetárias;
- testes de finalização, pagamento, integração e cancelamento.

## Regras críticas

- finalização é atômica e idempotente;
- produto insuficiente impede conclusão;
- o total persistido deve corresponder aos itens e ajustes;
- venda paga não pode manter saldo financeiro pendente;
- venda originada de orçamento mantém o vínculo;
- cancelamento não apaga a venda;
- cancelamento registra responsável, data e motivo;
- venda cancelada não pode provocar novo estorno.

## Arquivos principais

- models: `vendas/models.py`;
- services: `vendas/services/`;
- views: `vendas/views/`;
- templates: `vendas/templates/vendas/`;
- estilos: `static/css/vendas.css`;
- testes: `vendas/tests.py`.

## Manutenção

Qualquer alteração em total, pagamento ou status exige testes conjuntos de:

- criação direta;
- conversão de orçamento;
- estoque;
- Conta a Receber;
- recebimento à vista e a prazo;
- cancelamento;
- auditoria de integrações.

## Evoluções não bloqueantes

- comprovante/cupom dedicado;
- exportações adicionais;
- rankings e comparação de períodos;
- integrações fiscais, se definidas pela operação.
