# Módulo Vendas

Atualizado em 05/08/2026.

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
- cancelamento por POST com motivo e credenciais de Administrador;
- devolução de estoque e reversão/cancelamento financeiro;
- relatório de vendas;
- constraints monetárias;
- testes de finalização, pagamento, integração e cancelamento.
- modalidade e endereço de entrega, com frete somente para envio;
- variação de cor por item e baixa do estoque específico;
- resumo do pedido em PDF também para vendas em aberto;
- PDF institucional com logo configurada, dados completos da empresa e do
  cliente, vendedor, entrega, pagamento, itens, fechamento financeiro,
  observações, assinaturas, paginação e rodapé;
- resumo quantitativo no PDF com produtos distintos, itens/variações e peças;
- contatos e redes sociais do cabeçalho usam grade compartilhada de duas
  colunas, preservando identificadores longos sem cortes;
- edição completa de vendas em aberto pela ficha, incluindo cliente, entrega,
  itens, variação de cor, quantidades, preços, descontos e frete.
- seleção da cor diretamente no card de resultado do produto, permitindo repetir
  o mesmo produto quando a variação for diferente;
- alteração do vendedor pela listagem para administradores e gerentes, sem
  reprocessar as integrações da venda.
- correção do vendedor pela ficha, inclusive após conclusão, autorizada pela
  senha de Administrador, Gerente ou Financeiro;
- compartilhamento do PDF pelo recurso nativo do dispositivo, com fallback de
  download e abertura do WhatsApp.

## Regras críticas

- finalização é atômica e idempotente;
- produto insuficiente impede conclusão;
- o total persistido deve corresponder aos itens e ajustes;
- venda paga não pode manter saldo financeiro pendente;
- venda originada de orçamento mantém o vínculo;
- cancelamento não apaga a venda;
- cancelamento registra responsável, data e motivo;
- qualquer perfil pode solicitar o cancelamento, mas a execução exige usuário
  e senha válidos de Administrador e registra solicitante e autorizador;
- venda cancelada não pode provocar novo estorno.
- somente vendas em aberto, ainda sem baixa de estoque ou geração financeira,
  podem ser editadas.
- a troca isolada do vendedor é permitida aos perfis Administrador, Gerente e
  Financeiro mediante confirmação da própria senha, inclusive em vendas finalizadas.

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
- a ficha diferencia produto, código ERP e variação de cor, inclusive quando o
  produto não possui código ou não trabalha com cores;
- o resumo da ficha separa produtos distintos, itens/variações e peças;
