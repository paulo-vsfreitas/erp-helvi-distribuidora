# Integrações entre Módulos

## Princípio

Integrações são executadas por services explícitos e, quando possuem múltiplos
efeitos, dentro de `transaction.atomic`. Views apenas coordenam entrada,
mensagens e redirecionamento.

## Comercial → Vendas

```text
Orçamento aprovado/enviado
→ conversão validada
→ Venda e itens criados
→ vínculo venda_gerada preservado
→ orçamento marcado como convertido
```

Regras:

- não converter duas vezes;
- preservar cliente ou interessado e os itens;
- preservar descontos, frete e totais;
- a conversão não baixa estoque até a finalização da venda.

## Vendas → Estoque → Financeiro

```text
Venda em edição
→ validação de itens e pagamento
→ finalização
→ baixa de estoque
→ Conta a Receber e parcelas
→ recebimento/movimentação quando aplicável
```

Regras:

- finalização idempotente;
- estoque nunca pode ficar negativo;
- venda paga precisa estar financeiramente coerente;
- cancelamento devolve produtos ao estoque e cancela/reverte o financeiro;
- usuário, data e motivo ficam registrados.

## Compras → Estoque → Financeiro

```text
Compra aberta
→ itens e pagamentos
→ recebimento
→ entrada no estoque
→ atualização de custo
→ Conta a Pagar e parcelas
```

Regras:

- uma compra recebida gera no máximo uma entrada e uma Conta a Pagar;
- custo do produto é atualizado no recebimento;
- cancelamento valida se o estorno não produzir estoque negativo;
- compras históricas recebidas sem financeiro podem ser conciliadas pelo comando
  oficial documentado em `MANUTENCAO.md`.

## Financeiro

Baixa de Conta a Pagar:

```text
Parcela a pagar
→ BaixaPagar
→ MovimentacaoFinanceira de saída
→ atualização da parcela e da conta
```

Recebimento de Conta a Receber:

```text
Parcela a receber
→ RecebimentoConta
→ MovimentacaoFinanceira de entrada
→ atualização da parcela e da conta
```

Estorno manual:

```text
Operação original preservada
→ motivo obrigatório
→ movimento financeiro inverso
→ reabertura/recalculo da parcela
→ recálculo da conta
→ histórico do estorno
```

## Compartilhamento de orçamento

Antes de preparar cada canal, o Comercial carrega os modelos do singleton
`Empresa`, monta o contexto do orçamento e substitui apenas as variáveis
permitidas. Se o modelo correspondente estiver vazio, usa o texto original do
sistema. A camada `core/communication` não acessa configurações nem entidades de
negócio.

E-mail:

- gera o PDF em memória;
- envia por backend de e-mail configurado;
- registra sucesso ou falha e destinatário;
- pode marcar o orçamento como enviado.

WhatsApp:

- normaliza telefone e mensagem;
- prepara URL para abertura do WhatsApp;
- registra o compartilhamento como preparado;
- o envio final depende da confirmação do usuário fora do ERP.

## Auditoria

`python manage.py auditar_integracoes` verifica as invariantes essenciais sem
alterar dados. O comando deve ser executado antes e depois de manutenção em
orçamentos, vendas, compras, estoque, produtos ou financeiro.
