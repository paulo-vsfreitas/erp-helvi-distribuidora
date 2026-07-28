# Arquitetura Oficial do ERP Helvi

## Visão geral

Cada aplicação Django representa um domínio de negócio.

Exemplos:

- usuários;
- catálogo;
- produtos;
- clientes;
- fornecedores;
- estoque;
- compras;
- financeiro;
- vendas;
- core.

O `core` contém recursos transversais e componentes compartilhados.
Ele não deve concentrar regras específicas dos módulos de negócio.

## Estrutura recomendada

```text
modulo/
|-- admin.py
|-- apps.py
|-- models.py
|-- urls.py
|-- forms/
|-- services/
|-- utils/
|-- views/
|-- templates/
|-- migrations/
`-- tests/
```

## Models

Representam entidades persistidas, relacionamentos, choices, constantes e
propriedades simples.

Fluxos que afetam vários módulos devem ficar em services.

## Forms

Responsáveis por:

- validação de entrada;
- normalização;
- mensagens de erro;
- preparação dos dados.

## Views

Devem:

- receber a requisição;
- validar autenticação e permissões;
- instanciar forms;
- chamar services;
- montar o contexto;
- renderizar ou redirecionar.

Views não devem executar fluxos complexos de negócio.

## Services

Concentram regras operacionais e integrações.

Um service não deve:

- receber `request`;
- renderizar templates;
- retornar `HttpResponse`;
- depender de HTML.

Operações compostas devem utilizar `transaction.atomic`.

## URLs

Cada app possui seu próprio `urls.py` e namespace.

Documentos comerciais utilizam `numero` nas URLs. A chave primária continua
sendo usada internamente.

## Fichas

A ficha é a tela central de documentos e cadastros relevantes.

Pode apresentar:

- identificação;
- status;
- ações;
- resumo;
- dados gerais;
- itens;
- financeiro;
- histórico;
- observações.

## Telas públicas

Login, recuperação de senha e páginas de erro não devem herdar
`core/base.html`.

## Conclusão de módulos

Um módulo somente é considerado concluído após validar:

- cadastro;
- edição;
- pesquisa;
- validações;
- permissões;
- interface;
- integrações;
- cenários de erro;
- homologação.
