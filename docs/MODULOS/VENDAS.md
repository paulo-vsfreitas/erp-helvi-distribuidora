# Módulo Vendas

## Fluxo

```text
Venda direta ou originada de orçamento
→ Cliente opcional
→ Produtos
→ Pagamento
→ Finalização
→ Baixa de estoque
→ Conta a receber
→ Movimentação financeira
→ Histórico
```

## Implementado

- nova venda;
- listagem;
- ficha;
- numeração comercial;
- origem por orçamento;
- finalização;
- baixa de estoque;
- financeiro;
- pagamentos;
- relatórios iniciais.

## Regras

- venda pode ocorrer sem cliente cadastrado;
- conversão de orçamento preserva vínculo;
- finalização deve ser idempotente;
- venda sem número não pode quebrar listagens.

## Pendências

- homologação integral;
- cancelamento com estorno;
- comprovante/cupom;
- revisão da venda avulsa;
- rankings;
- comparação de períodos;
- exportações.
