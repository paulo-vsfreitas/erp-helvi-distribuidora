# Formatadores do Framework Helvi

Atualizado em 04/08/2026.

## Fonte oficial

Python:

```python
from core.formatters import formatar_moeda_br

formatar_moeda_br(2338.8)  # R$ 2.338,80
```

Template:

```django
{% load moeda %}
{{ valor|moeda }}
```

Arquivos:

- `core/formatters.py`;
- `core/templatetags/moeda.py`.

## Regras

- valores monetários usam `Decimal`;
- `None` resulta em zero quando apropriado ao componente;
- não depender do `locale` do sistema operacional;
- formato oficial: `R$ 10.925,10`;
- services podem retornar `Decimal` e deixar a apresentação para template;
- não criar novo `moeda()` ou `formatar_moeda()` local.

## Estado de migração

O formatador oficial e o filtro já estão em uso. Ainda existem wrappers e
implementações anteriores em alguns services financeiros, indicadores e no PDF
de orçamento. Eles produzem formato compatível, mas são dívida técnica.

Migração segura:

1. acrescentar testes do contexto/saída;
2. substituir a implementação local por import do `core`;
3. remover o helper somente quando não houver referências;
4. revisar templates que ainda usam `R$ {{ valor|floatformat:2 }}`;
5. homologar PDFs e telas afetadas.
