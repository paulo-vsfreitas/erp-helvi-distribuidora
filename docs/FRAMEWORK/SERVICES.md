# Services do Framework Helvi

## Regra

Services de negócio permanecem em seus módulos:

```text
comercial/services/
vendas/services/
compras/services/
estoque/services/
financeiro/services/
fornecedores/services/
```

O `core` fornece recursos genéricos ou composições globais claramente
identificadas.

## Contrato

Um service:

- recebe argumentos explícitos;
- não recebe `request`;
- não renderiza template;
- não retorna `HttpResponse`;
- valida estados e invariantes;
- retorna entidade ou resultado estruturado;
- usa `transaction.atomic` quando há múltiplas gravações;
- usa bloqueio quando concorrência pode duplicar número ou efeito;
- registra histórico quando a operação exige rastreabilidade;
- é idempotente quando pode ser repetido por interface ou integração.

## Erros

- use `ValidationError` para regra que a view deve apresentar ao usuário;
- não capture `Exception` silenciosamente;
- quando um canal externo falhar, registre o resultado e preserve a exceção ou
  retorne contrato explícito;
- a view converte o erro em mensagem e redirecionamento/renderização.

## Integrações

Uma operação como finalizar venda ou receber compra deve ter um service
orquestrador. Evite signals implícitos para efeitos financeiros ou de estoque,
pois dificultam idempotência, ordem e testes.

## Testes

Teste services diretamente para regras e use o client Django para método HTTP,
permissão, mensagens e redirecionamento.
