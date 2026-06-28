# Arquitetura - ERP Helvi Distribuidora

O ERP Helvi Distribuidora utiliza arquitetura modular, separando responsabilidades por camadas.

## Estrutura principal

- models: definição das tabelas e regras básicas dos dados
- forms: formulários do sistema
- views: controle das telas e ações do usuário
- templates: arquivos HTML
- services: regras de negócio mais complexas
- utils: funções reutilizáveis
- docs: documentação do projeto

## Padrão dos módulos

Cada módulo deve seguir:

- Model no singular
- Form no plural
- View no plural
- Templates em pasta no plural
- URLs centralizadas no arquivo `catalogo/urls.py`

## Objetivo

Manter o sistema simples, organizado, escalável e fácil de manter.