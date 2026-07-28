# Services do Framework Helvi

Services de negócio permanecem dentro de seus módulos.

```text
vendas/services/
compras/services/
estoque/services/
financeiro/services/
```

O `core` pode fornecer apenas recursos genéricos.

Dependência permitida:

```text
vendas -> core
financeiro -> core
estoque -> core
```

Dependência que deve ser evitada:

```text
core -> vendas
core -> financeiro
core -> estoque
```
