# Componentes do Framework Helvi

## Componentes e padrões já utilizados

### Layout

- `core/base.html`;
- sidebar;
- topbar;
- menu do usuário;
- layout público independente.

### Fichas

Estrutura central para cadastros e documentos:

- cabeçalho;
- ações;
- indicadores;
- dados gerais;
- itens;
- resumo lateral;
- histórico;
- observações.

### Dashboard e KPIs

Já existem cards e componentes de indicadores, incluindo:

```text
core/templates/components/dashboard/kpi_cards.html
```

Contrato típico:

```python
{
    "titulo": "Faturamento",
    "valor": "R$ 15.800,00",
    "icone": "bi-cash-stack",
    "subtitulo": "Vendas finalizadas no período",
    "url": None,
}
```

### Tabelas e estados vazios

Padrões reutilizados para:

- cabeçalho;
- linhas;
- ações;
- responsividade;
- estado sem registros.

### Autocomplete

Aplicado em clientes e produtos, com busca assíncrona, resultados ativos, seleção e preenchimento de campos.

### Resumo sticky

Aplicado em formulários extensos para manter valores e ações principais visíveis.

### Modais e mensagens

Bootstrap é a base atual. A consolidação futura deve evitar implementações JS divergentes.

## Regra de extração

Componentes estruturais podem ser compartilhados desde cedo. Componentes específicos devem ser extraídos após repetição real e contrato estável.
