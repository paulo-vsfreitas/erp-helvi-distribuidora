# Arquitetura Oficial do ERP Helvi

## Visão geral

Cada aplicação Django representa um domínio de negócio. O `core` concentra somente recursos transversais e o Framework Helvi.

Domínios atuais:

- `core`;
- `usuarios`;
- `catalogo`;
- `produtos`;
- `clientes`;
- `fornecedores`;
- `estoque`;
- `compras`;
- `financeiro`;
- `comercial`;
- `vendas`;
- `configuracoes`.

## Estrutura padrão dos módulos

```text
modulo/
├── admin.py
├── apps.py
├── models.py
├── urls.py
├── forms/
├── services/
├── utils/
├── views/
├── templates/
├── migrations/
└── tests/
```

## Responsabilidades

### Models

Entidades persistidas, relacionamentos, choices, constantes e propriedades simples.

### Forms

Validação de entrada, normalização, mensagens de erro e preparação dos dados.

### Views

Autenticação, permissões, forms, chamada de services, contexto, renderização e redirecionamento. Views devem permanecer finas.

### Services

Regras operacionais, transações e integrações entre módulos. Não recebem `request`, não renderizam templates e não retornam `HttpResponse`.

Operações compostas devem utilizar `transaction.atomic`.

### Utils

Funções puras e auxiliares sem dependência de HTTP ou de regra operacional complexa.

## Dependências

Permitido:

```text
modulos de negocio -> core
```

Evitar:

```text
core -> modulo de negocio
```

Integrações entre domínios devem ocorrer por services explícitos.

## Identificadores

- `pk`: identificador interno;
- `numero`: identificador comercial;
- documentos comerciais usam `numero` nas URLs;
- códigos formatados são propriedades de apresentação.

## Fichas

A ficha é a tela central de cadastros e documentos relevantes, reunindo identificação, status, ações, dados gerais, itens, resumo financeiro, histórico e observações.

## Telas públicas

Login, recuperação de senha, redefinição e páginas 403/404/500 usam layout independente e nunca herdam `core/base.html`.

## Dados monetários

Valores monetários usam `Decimal`. A formatação de apresentação deve ser centralizada no Framework Helvi; não criar novos formatadores locais.
