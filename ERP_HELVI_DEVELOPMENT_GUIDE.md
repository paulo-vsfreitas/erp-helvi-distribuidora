# ERP Helvi Development Guide

> Documento oficial de arquitetura, desenvolvimento e padronização do ERP Helvi.
>
> Este guia deve ser consultado obrigatoriamente antes do início de qualquer Sprint, módulo ou refatoração.

---

# 1. Objetivo do Projeto

O ERP Helvi é um sistema ERP proprietário desenvolvido para a Helvi Distribuidora.

O objetivo do projeto é entregar um ERP:

- moderno;
- altamente reutilizável;
- organizado em camadas;
- de fácil manutenção;
- preparado para evolução contínua;
- visualmente consistente;
- escalável.

O desenvolvimento prioriza qualidade arquitetural sem comprometer a entrega de funcionalidades utilizáveis no dia a dia da empresa.

---

# 2. Regra Principal

Nenhuma Sprint pode começar sem revisar este documento.

Antes de qualquer implementação validar:

- arquitetura do módulo;
- integração com módulos existentes;
- padrão visual;
- componentes reutilizáveis;
- regras de negócio;
- permissões;
- serviços existentes;
- Framework Helvi;
- estado atual do projeto.

---

# 3. Filosofia do Projeto

Sempre seguir esta ordem:

```
Arquitetura

↓

Implementação

↓

Homologação

↓

Integração

↓

Refatoração incremental
```

Nunca desenvolver funcionalidades isoladas.

Todo código novo deve considerar o restante do ERP.

---

# 4. Arquitetura em Camadas

Todo módulo deverá seguir obrigatoriamente a estrutura abaixo.

```text
modulo/

admin.py
apps.py
models.py
urls.py

forms/
services/
utils/
views/

templates/
static/

migrations/
```

Separação de responsabilidades:

Models

persistência.

Forms

entrada de dados.

Services

regras de negócio.

Views

fluxo HTTP.

Utils

funções auxiliares.

Templates

interface.

Static

CSS, JS e imagens.

---

# 5. Framework Helvi

O ERP possui um Framework próprio.

Toda funcionalidade compartilhada deverá ser centralizada nele.

## 5.1 Frontend Framework

```text
static/js/core/

api.js
autocomplete.js
cep.js
image_preview.js
init.js
mascaras.js
modal.js
modal_busca.js
money.js
notifications.js
table.js
utils.js
validation.js
```

Todos os módulos utilizam estes componentes.

Nenhum módulo deve duplicar lógica já existente.

---

## 5.2 Backend Framework

```text
core/

services/
pdf/
templates/
```

O Core concentra infraestrutura compartilhada.

Nunca regras específicas de um módulo.

---

# 6. Regra de Componentização

Sempre avaliar reutilização.

Quando uma funcionalidade passar a ser utilizada por três ou mais módulos:

➡ ela deixa de pertencer ao módulo.

➡ passa para o Framework Helvi.

Exemplos:

✔ CEP

✔ Máscaras

✔ Money

✔ Preview

✔ Validation

✔ API

✔ Modal

✔ PDF

---

# 7. Regras dos Serviços

Toda regra de negócio deve existir em Services.

Views nunca devem conter regras complexas.

Exemplo:

Errado

```python
def salvar():
    atualizar_estoque()
    gerar_financeiro()
```

Correto

```python
compra_service.salvar_compra(...)
```

---

# 8. Regras dos Forms

Todo comportamento do campo deve ser configurado no Form.

Nunca diretamente no Template.

Exemplo:

Correto

```python
widget.attrs.update(...)
```

Evitar:

```html
<input data-xxx="...">
```

no template.

---

# 9. Templates

Os templates devem conter apenas apresentação.

Nunca lógica de negócio.

Nunca JavaScript complexo.

Nunca SQL.

Nunca cálculos.

---

# 10. JavaScript

Todo JavaScript compartilhado deve ficar em:

```text
static/js/core/
```

JavaScript específico:

```text
static/js/compras/

static/js/comercial/

static/js/vendas/
```

---

# 11. Framework de Documentos

Todos os documentos serão gerados exclusivamente pelo:

```text
core/pdf/
```

Nenhum módulo poderá utilizar ReportLab diretamente.

Arquitetura:

```text
core/pdf/

document.py
colors.py
styles.py
header.py
footer.py
tables.py
utils.py

elements/

company.py
logo.py
title.py
summary.py
products.py
payments.py
signature.py
```

---

# 12. Componentes de Documento

Todo PDF será composto por elementos.

Nunca um único arquivo gigante.

Exemplo:

```
Documento

↓

Company

↓

Title

↓

Products

↓

Summary

↓

Footer
```

---

# 13. Integração com Configurações

Dados institucionais serão sempre obtidos através de:

```
configuracoes.services.empresa_service
```

Nunca acessar Empresa diretamente.

---

# 14. Identidade Visual

Todo módulo deve seguir o padrão Helvi.

- Cards padronizados
- Botões padronizados
- Ficha central
- Sidebar única
- Dashboard padrão
- Componentes reutilizáveis

---

# 15. Ficha Central

Sempre que fizer sentido, cada módulo deve possuir uma Ficha.

A Ficha representa a tela principal da entidade.

Exemplos:

Produto

Cliente

Fornecedor

Compra

Venda

Pedido

Orçamento

Conta a Pagar

Conta a Receber

---

# 16. Dashboard

Todo módulo deverá possuir Dashboard.

O Dashboard concentra:

KPIs

Atalhos

Indicadores

Listagens

Alertas

---

# 17. Permissões

Todo módulo deve respeitar:

ADM

GER

VEN

FIN

e os demais perfis existentes.

Nunca validar permissões diretamente nas Views.

Utilizar o sistema centralizado.

---

# 18. Homologação

Nenhuma Sprint será considerada concluída sem homologação.

Fluxo:

```
Implementação

↓

Teste

↓

Correção

↓

Homologação

↓

Git

↓

Nova Sprint
```

---

# 19. Git

Sempre antes de encerrar uma Sprint:

```
python manage.py check

git diff --check

git status
```

Somente após:

Commit

Push

Nova conversa

---

# 20. Roadmap

A prioridade oficial do ERP é:

1. Produtos
2. Estoque
3. Compras
4. Financeiro
5. Comercial
6. Vendas
7. Relatórios
8. Dashboard Executivo
9. BI
10. App Mobile

Sempre finalizar completamente um módulo antes de iniciar o próximo.

---

# 21. Regras Permanentes

✔ Arquitetura em camadas.

✔ Reutilizar componentes.

✔ Não duplicar código.

✔ Explicar alterações de forma didática.

✔ Homologar cada funcionalidade.

✔ Consultar este guia antes de cada Sprint.

✔ Priorizar infraestrutura compartilhada quando houver reutilização.

✔ Nenhum módulo conhece diretamente bibliotecas externas quando existir um componente equivalente no Framework.

✔ Toda evolução deve preservar a organização do ERP.

✔ O ERP deve evoluir incrementalmente, mantendo o sistema sempre funcional.

---


# 22. Convenções de Código, definindo padrões como:

nomenclatura de arquivos (snake_case);
nomenclatura de classes (PascalCase);
nomenclatura de funções (snake_case);
padrão para nomes de URLs;
padrão para nomes de templates;
padrão para CSS;
padrão para JavaScript;
convenções de mensagens de commit.

------

# Missão do Projeto

Construir um ERP profissional, moderno, reutilizável e escalável, capaz de atender integralmente a operação da Helvi Distribuidora, priorizando qualidade arquitetural, experiência do usuário, manutenção simplificada e evolução contínua.


## Componentização no Framework de Documentos

A criação de componentes compartilhados no Framework de PDF deve ocorrer somente quando houver reutilização comprovada.

### Regra

- Blocos utilizados por dois ou mais tipos de documentos devem ser promovidos para o Framework compartilhado.
- Blocos exclusivos de um único documento devem permanecer dentro do próprio documento.
- Não criar componentes antecipadamente apenas por possibilidade futura de reutilização.
- A extração deve ocorrer após a homologação do primeiro fluxo completo.

### Exemplos de componentes compartilhados

Devem permanecer no Framework:

- cabeçalho institucional;
- logo da empresa;
- estilos;
- cores;
- rodapé;
- paginação;
- tabela genérica de produtos;
- resumo financeiro;
- formatação de moeda e datas.

### Exemplos de conteúdo específico

Devem permanecer no documento correspondente enquanto não houver reutilização:

- dados específicos da compra;
- informações exclusivas de uma venda;
- regras particulares de um orçamento;
- blocos exclusivos de determinado relatório.

### Fluxo recomendado

```text
Documento funcional completo
        ↓
Homologação
        ↓
Identificação de repetição real
        ↓
Extração do componente
        ↓
Reutilização nos demais documentos