# Formatadores do Framework Helvi

## Estado encontrado

Existem múltiplas implementações de `moeda()` e `formatar_moeda()` em Compras, Core/PDF, Financeiro e Fornecedores. Muitos templates usam:

```django
R$ {{ valor|floatformat:2 }}
```

Isso não aplica separador de milhar brasileiro.

## Padrão alvo

Deve existir:

1. uma função Python pura e global para moeda;
2. um filtro de template que reutiliza essa função;
3. uso da mesma função no Framework PDF;
4. migração gradual das implementações locais.

Formato oficial:

```text
R$ 10.925,10
```

## Regras

- valores monetários usam `Decimal`;
- `None` deve resultar em zero quando apropriado;
- não usar `locale` global dependente do sistema operacional;
- não criar novos formatadores em módulos;
- não substituir tudo de uma vez sem testes;
- migrar módulo por módulo.

## Pendência imediata

Consolidar o formatador em `core/utils/formatters.py` e disponibilizar filtro em `core/templatetags/helvi_format.py`.
