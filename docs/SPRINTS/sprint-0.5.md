# Sprint 0.5 – Infraestrutura do ERP

## Objetivo

Criar a infraestrutura compartilhada que será utilizada por todos os módulos do ERP Helvi.

## Concluído

* Criação da pasta `core/base`
* Criação de `CadastroBase`
* Criação de `BaseModelForm`
* Definição da estratégia de arquitetura compartilhada

## Próximos passos

* Criar mixins reutilizáveis
* Definir autenticação e permissões
* Criar o módulo Usuários
* Criar Materiais utilizando a nova infraestrutura

## Decisões arquiteturais

* Não utilizar o Admin do Django como interface do ERP.
* Centralizar recursos compartilhados em `core/base`.
* Utilizar o Django como base, estendendo seus recursos em vez de substituí-los.
* Desenvolver primeiro a infraestrutura e depois os módulos de negócio.

## Status

🚧 Em andamento
