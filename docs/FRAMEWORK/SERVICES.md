# Services do Framework Helvi

## Regra

Services de negócio permanecem em seus módulos:

```text
comercial/services/
vendas/services/
compras/services/
estoque/services/
financeiro/services/
```

O `core` fornece apenas recursos genéricos, sem regra específica de domínio.

## Contrato

Um service:

- não recebe `request`;
- não renderiza template;
- não retorna `HttpResponse`;
- recebe argumentos explícitos;
- retorna entidades ou resultados estruturados;
- usa `transaction.atomic` em operações compostas;
- valida duplicidade e idempotência quando necessário.

## Dependências

Permitido:

```text
modulo -> core
```

Evitar:

```text
core -> modulo
```

Integrações entre módulos devem ser explícitas e testáveis.
