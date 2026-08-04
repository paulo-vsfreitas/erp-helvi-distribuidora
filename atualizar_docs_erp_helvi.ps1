$ErrorActionPreference = "Stop"

$raiz = (Get-Location).Path
$docs = Join-Path $raiz "docs"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backup = Join-Path $raiz "docs_backup_$timestamp"

if (Test-Path $docs) {
    Copy-Item $docs $backup -Recurse -Force
    Remove-Item $docs -Recurse -Force
}

New-Item -ItemType Directory -Path $docs -Force | Out-Null

@'
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
'@ | Set-Content -Path (Join-Path $docs "ARQUITETURA.md") -Encoding UTF8

@'
# Backlog Oficial do ERP Helvi

## Prioridade alta

### Framework Helvi

- criar fonte única de formatação monetária;
- disponibilizar filtro de template oficial;
- migrar gradualmente `floatformat:2` e formatadores locais;
- eliminar duplicações sem interromper módulos;
- documentar componentes existentes.

### Comercial

- homologação completa de Orçamento → Venda;
- filtros e busca por número, cliente, documento, telefone, responsável e status;
- validade padrão configurável;
- destaque de orçamento vencido;
- histórico de status;
- envio real por WhatsApp e e-mail;
- registrar compartilhamentos.

### Vendas

- homologação integral;
- cancelamento com estorno de estoque e financeiro;
- venda avulsa sem cliente;
- comprovante/cupom;
- revisão da ficha e listagem.

## Prioridade média

### Compras

- cancelar compra recebida com estorno seguro;
- concluir edição de itens;
- histórico de entrada;
- revisar compra sem itens com pagamentos;
- homologação integral.

### Estoque

- locais de estoque;
- transferências;
- alertas de estoque mínimo;
- relatório consolidado;
- histórico detalhado de origem.

### Financeiro

- relatório financeiro;
- fluxo de caixa avançado;
- projeções;
- indicadores consolidados;
- revisão de históricos.

### Fornecedores

- confirmar edição, ficha, pesquisa e homologação atual;
- integração completa com compras e histórico.

## Plataforma

- pesquisa global;
- auditoria;
- testes automatizados prioritários;
- revisão de performance;
- backup e restauração;
- preparação de produção.
'@ | Set-Content -Path (Join-Path $docs "BACKLOG.md") -Encoding UTF8

@'
# Changelog do ERP Helvi

## Agosto de 2026

### Comercial — Orçamentos

- dashboard Comercial redesenhado;
- indicadores de orçamentos, rascunhos, aprovados e valor orçado;
- listagem com cliente, responsável, emissão, validade, status, itens, peças e total;
- cadastro para cliente cadastrado ou interessado avulso;
- autocomplete de clientes ativos;
- autocomplete de produtos ativos;
- prevenção de produto duplicado;
- indicação visual de produto já adicionado;
- resumo financeiro em tempo real;
- ações e resumo lateral sticky;
- ficha do orçamento;
- geração de PDF;
- fluxo de status: rascunho, enviado, aprovado, rejeitado, cancelado e convertido;
- conversão de orçamento em venda;
- duplicação de orçamento;
- exibição do responsável;
- melhorias de UX e correções de cálculo.

### Vendas

- regularização de numeração de vendas existentes;
- correção da listagem que recebia vendas sem número;
- integração já existente com orçamento, estoque e financeiro mantida.

### Compras

- correção de interpretação de frete;
- edição de produtos e valores em evolução;
- correção de ação duplicada de cancelamento;
- geração de PDF disponível.

### Framework Helvi

- consolidação do Framework como base já existente;
- revisão do CSS Comercial;
- evolução do Framework PDF;
- identificada duplicação de formatadores monetários;
- iniciada padronização global de moeda e apresentação.

## Julho de 2026

- módulos de Compras, Estoque, Financeiro, Fornecedores e Vendas evoluídos;
- arquitetura em camadas consolidada;
- fichas padronizadas;
- integração Compras → Estoque;
- integração Compras → Financeiro;
- Contas a Pagar e Contas a Receber;
- fluxo principal de Vendas;
- baixa automática de estoque;
- integração de Vendas com Contas a Receber;
- relatórios iniciais;
- modularização de views e services.

## Junho de 2026

- fundação do projeto;
- autenticação e usuários;
- catálogo;
- produtos;
- clientes;
- permissões;
- identidade visual inicial.
'@ | Set-Content -Path (Join-Path $docs "CHANGELOG.md") -Encoding UTF8

@'
# Decisões Permanentes do ERP Helvi

## Produto e metodologia

- Priorizar um sistema completo e utilizável antes de grandes refatorações.
- Concluir e homologar os fluxos principais antes de avançar de módulo.
- Iniciar novas conversas recuperando esta documentação e o estado mais recente.
- Solicitar somente arquivos específicos quando a implementação atual precisar ser confirmada.

## Interface

- A ficha é a tela central de Produto, Cliente, Fornecedor, Compra, Orçamento e Venda.
- Telas públicas não herdam a base interna autenticada.
- Resumos financeiros podem ser sticky quando isso melhora a conferência.
- Ações principais devem permanecer próximas do resumo no fluxo de formulários longos.
- Usar “Responsável” nas listagens para identificar quem realizou a operação, independentemente do perfil.
- Componentes visuais devem seguir a identidade Helvi: preto, dourado, branco e tons neutros.

## Produtos e itens

- O mesmo produto não pode aparecer duplicado em uma lista de itens.
- Ao tentar adicioná-lo novamente, informar que já está incluído e orientar a alteração da quantidade/desconto na linha existente.
- Autocompletes devem permitir busca por dados relevantes do domínio e, quando útil, exibir registros ativos ao focar o campo.

## Comercial

Fluxo oficial de orçamento:

```text
Cliente ou interessado
→ Novo orçamento
→ Produtos
→ Salvar
→ Visualizar
→ PDF
→ Enviar/compartilhar
→ Aprovar ou rejeitar
→ Converter em venda
```

- Orçamento pode ser criado para cliente cadastrado ou interessado avulso.
- Conversão em venda reutiliza cliente, produtos, quantidades, descontos, frete e totais.
- Conversão deve ser idempotente: não permitir conversão duplicada.
- “Enviar” como alteração de status deve ser identificado como “Marcar como enviado” ou equivalente quando existir envio real por canal.
- Orçamentos podem ser duplicados; a cópia nasce em rascunho, com nova numeração e responsável atual.

## Vendas

- Venda pode ocorrer sem cliente cadastrado, preservando dados básicos para comprovante.
- Finalização integra estoque e financeiro.
- Cancelamentos futuros devem estornar efeitos de forma segura e rastreável.

## Compras e estoque

- Receber compra atualiza estoque e custo, registra movimentação e impede duplicidade de entrada.
- Transferências de estoque dependem da implementação de locais de estoque.
- Compra recebida não deve ser editada de forma que comprometa o histórico.

## Framework

- O Framework Helvi já existe e deve ser consolidado, não recriado.
- Nenhum módulo deve reinventar recurso transversal já disponível.
- Abstrações devem nascer do uso real e da repetição comprovada.
- Formatação monetária, documentos, telefone, datas, badges, KPIs e mensagens devem convergir para fontes únicas.
'@ | Set-Content -Path (Join-Path $docs "DECISOES.md") -Encoding UTF8

@'
# ERP Helvi Development Guide

## 1. Objetivo principal

Entregar primeiro um ERP minimamente completo, confiável e utilizável na operação real da Helvi. Refinamentos arquiteturais extensos devem ocorrer de forma incremental, sem interromper a evolução funcional.

## 2. Ritual obrigatório antes de qualquer sprint

Antes de implementar:

1. ler esta documentação;
2. revisar arquitetura e decisões permanentes;
3. verificar o estado do módulo;
4. procurar recursos já existentes no Framework Helvi;
5. solicitar somente o arquivo específico necessário para confirmar a implementação;
6. evitar recriar código, componentes ou regras já consolidados.

## 3. Metodologia

- explicar alterações de forma didática;
- preservar arquitetura em camadas;
- implementar em etapas pequenas;
- homologar cada fluxo antes de considerá-lo concluído;
- não encerrar uma sprint com funcionalidade crítica pendente;
- registrar pendências reais no backlog;
- atualizar documentação e Git ao final de cada marco.

## 4. Ordem recomendada de implementação

1. blueprint e regras;
2. models e migrations;
3. forms e validações;
4. services;
5. views;
6. URLs;
7. templates;
8. CSS e JavaScript;
9. permissões;
10. integrações;
11. homologação;
12. documentação;
13. commit e tag quando aplicável.

## 5. Reuso

- recursos transversais ficam no `core`;
- regras específicas permanecem no módulo;
- componentes estruturais podem nascer no primeiro uso;
- componentes específicos devem ser extraídos quando houver reutilização real;
- antes de criar algo novo, pesquisar em todo o projeto.

## 6. Critério de conclusão

Um módulo só é concluído após validar:

- cadastro e edição;
- listagem, pesquisa e filtros;
- validações e mensagens;
- permissões;
- interface;
- integrações;
- duplicidade e idempotência;
- cenários de erro;
- homologação funcional.
'@ | Set-Content -Path (Join-Path $docs "DEVELOPMENT_GUIDE.md") -Encoding UTF8

@'
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
'@ | Set-Content -Path (Join-Path $docs "FRAMEWORK\COMPONENTES.md") -Encoding UTF8

@'
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
'@ | Set-Content -Path (Join-Path $docs "FRAMEWORK\FORMATADORES.md") -Encoding UTF8

@'
# Nomenclatura do Framework Helvi

- `pk`: identificador interno;
- `numero`: identificador comercial;
- `codigo`: representação formatada ou código de cadastro;
- `status`: situação operacional;
- `status_pagamento`: situação financeira;
- `subtotal`: soma antes dos ajustes gerais;
- `desconto`: redução aplicada;
- `frete`: acréscimo de entrega;
- `total`: valor final;
- `valor_pago`: valor pago em compras;
- `valor_recebido`: valor recebido em vendas;
- `saldo_pagar`: obrigação pendente;
- `saldo_receber`: recebimento pendente;
- `responsavel`: pessoa que realizou a operação na apresentação;
- `vendedor`: vínculo técnico do responsável comercial quando esse for o campo do modelo.
'@ | Set-Content -Path (Join-Path $docs "FRAMEWORK\NOMENCLATURA.md") -Encoding UTF8

@'
# Framework PDF — ERP Helvi

## Objetivo

Centralizar a geração de documentos, garantindo identidade visual, reutilização e manutenção única.

## Estrutura

```text
core/pdf/
├── assets/
├── documents/
├── elements/
├── colors.py
├── document.py
├── footer.py
├── header.py
├── styles.py
├── tables.py
└── utils.py
```

## Regras

- documentos usam `HelviPDF`;
- não criar `SimpleDocTemplate` diretamente quando a base atende;
- cores ficam em `colors.py`;
- estilos ficam em `styles.py`;
- blocos reutilizáveis ficam em `elements`;
- tabelas reutilizáveis ficam em `tables.py`;
- documentos apenas organizam componentes;
- formatação monetária deve reutilizar o formatador oficial do Framework.

## Documentos atuais

- PDF de Compra;
- PDF de Orçamento.

## Evoluções

- PDF de Venda;
- recibo;
- comprovante/cupom;
- etiquetas;
- relatórios.

## Status

Framework em uso e homologado nos documentos já validados, com pendência de consolidar formatadores duplicados.
'@ | Set-Content -Path (Join-Path $docs "FRAMEWORK\PDF.md") -Encoding UTF8

@'
# Framework Helvi

O Framework Helvi é a camada transversal já utilizada pelo ERP para padronizar arquitetura, interface, documentos e recursos reutilizáveis.

## Princípio

Nenhum módulo deve reinventar algo que já exista no Framework.

## Escopo

O Framework pode fornecer:

- layout e identidade visual;
- componentes estruturais;
- KPIs, cards, tabelas e estados vazios;
- fichas e resumos;
- mensagens e modais;
- formatação e template tags;
- helpers JavaScript;
- Framework PDF;
- contratos e nomenclatura.

Não deve absorver regras específicas de Compras, Vendas, Estoque, Comercial ou Financeiro.

## Estado atual

Já aplicado em diferentes níveis:

- arquitetura em camadas;
- base autenticada e base pública;
- fichas;
- cards;
- tabelas;
- forms;
- sidebar/topbar;
- permissões;
- autocompletes;
- resumos sticky;
- PDF;
- services e helpers compartilhados.

## Consolidação atual

A prioridade é consolidar o que já existe, eliminar duplicações e registrar contratos oficiais antes de criar novas abstrações.
'@ | Set-Content -Path (Join-Path $docs "FRAMEWORK\README.md") -Encoding UTF8

@'
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
'@ | Set-Content -Path (Join-Path $docs "FRAMEWORK\SERVICES.md") -Encoding UTF8

@'
# Cadastros Base

## Usuários

- autenticação;
- perfis ADM, GER, VEN e FIN;
- permissões;
- foto e menu;
- telas públicas independentes.

## Catálogo

- marcas;
- coleções;
- gêneros;
- tipos de armação;
- CRUD e controle de ativos.

## Produtos

- código, modelo e atributos de catálogo;
- preços;
- estoque atual e mínimo;
- imagens;
- filtros;
- ficha.

## Clientes

- cadastro e edição;
- validações;
- máscaras;
- PF sem CNPJ;
- pesquisa;
- integração com Comercial e Vendas.
'@ | Set-Content -Path (Join-Path $docs "MODULOS\CADASTROS.md") -Encoding UTF8

@'
# Módulo Comercial — Orçamentos

## Fluxo

```text
Cliente cadastrado ou interessado avulso
→ Novo orçamento
→ Produtos
→ Salvar
→ Ficha
→ PDF
→ Marcar como enviado
→ Aprovar ou rejeitar
→ Converter em venda
```

## Implementado

- dashboard;
- KPIs;
- listagem;
- responsável;
- cadastro;
- edição;
- cliente cadastrado ou avulso;
- autocomplete de clientes;
- autocomplete de produtos;
- prevenção de duplicidade de produto;
- cálculo em tempo real;
- resumo e ações sticky;
- ficha;
- PDF;
- status;
- duplicação;
- conversão em venda.

## Regras

- produto não se repete na lista;
- a quantidade é alterada na linha existente;
- cópia nasce como rascunho;
- conversão não pode ocorrer duas vezes;
- o orçamento original permanece preservado.

## Pendências

- homologação integrada completa;
- filtros e busca;
- vencimento visual;
- validade padrão;
- histórico de status;
- envio real por WhatsApp/e-mail;
- registro de compartilhamentos.
'@ | Set-Content -Path (Join-Path $docs "MODULOS\COMERCIAL.md") -Encoding UTF8

@'
# Módulo Compras

## Fluxo

```text
Compra
→ Fornecedor
→ Itens
→ Pagamentos
→ Recebimento
→ Entrada no estoque
→ Atualização do custo
→ Financeiro
→ Histórico
```

## Implementado

- nova compra;
- fornecedor cadastrado;
- busca de produtos;
- itens e valores;
- ficha;
- edição de dados e itens em evolução;
- pagamentos;
- status de pagamento;
- recebimento;
- entrada no estoque;
- movimentações;
- integração financeira;
- PDF.

## Pendências

- cancelar compra recebida com estorno;
- concluir edição de itens;
- histórico de entrada;
- revisar compra sem itens com pagamentos;
- homologação integral.
'@ | Set-Content -Path (Join-Path $docs "MODULOS\COMPRAS.md") -Encoding UTF8

@'
# Módulo Estoque

## Responsabilidade

Movimentações, entradas, saídas, ajustes, inventários e integrações com Compras e Vendas.

## Implementado

- dashboard;
- lista de movimentações;
- filtros;
- entradas por compra;
- saídas por venda;
- ajustes;
- inventário;
- rastreio de origem.

## Pendências

- locais de estoque;
- transferências;
- alertas de estoque mínimo;
- relatório consolidado;
- homologação integrada de estornos.
'@ | Set-Content -Path (Join-Path $docs "MODULOS\ESTOQUE.md") -Encoding UTF8

@'
# Módulo Financeiro

## Responsabilidade

Contas a Pagar, Contas a Receber, parcelas, contas financeiras, movimentações, baixas, recebimentos e históricos.

## Implementado

- Contas a Pagar;
- Contas a Receber;
- parcelas;
- contas financeiras;
- movimentações;
- baixas e recebimentos;
- integração com Compras;
- integração com Vendas;
- histórico financeiro.

## Pendências

- relatório financeiro;
- fluxo de caixa avançado;
- projeções;
- indicadores consolidados;
- revisão de históricos;
- padronização monetária.
'@ | Set-Content -Path (Join-Path $docs "MODULOS\FINANCEIRO.md") -Encoding UTF8

@'
# Módulo Fornecedores

## Responsabilidade

Cadastro, consulta e vínculo histórico com Compras.

## Estado conhecido

- model e migrations;
- dashboard;
- cadastro;
- arquitetura modular em forms, services, utils e views;
- integração básica com Compras.

## Pendências a confirmar no código atual

- edição;
- ficha;
- pesquisa;
- inativação/reativação;
- homologação completa.

Este documento deve ser atualizado após a próxima revisão funcional do módulo.
'@ | Set-Content -Path (Join-Path $docs "MODULOS\FORNECEDORES.md") -Encoding UTF8

@'
# Módulo Vendas

## Fluxo

```text
Venda direta ou originada de orçamento
→ Cliente opcional
→ Produtos
→ Pagamento
→ Finalização
→ Baixa de estoque
→ Conta a receber
→ Movimentação financeira
→ Histórico
```

## Implementado

- nova venda;
- listagem;
- ficha;
- numeração comercial;
- origem por orçamento;
- finalização;
- baixa de estoque;
- financeiro;
- pagamentos;
- relatórios iniciais.

## Regras

- venda pode ocorrer sem cliente cadastrado;
- conversão de orçamento preserva vínculo;
- finalização deve ser idempotente;
- venda sem número não pode quebrar listagens.

## Pendências

- homologação integral;
- cancelamento com estorno;
- comprovante/cupom;
- revisão da venda avulsa;
- rankings;
- comparação de períodos;
- exportações.
'@ | Set-Content -Path (Join-Path $docs "MODULOS\VENDAS.md") -Encoding UTF8

@'
# Documentação Oficial — ERP Helvi

Esta pasta é a fonte oficial de contexto arquitetural, funcional e de planejamento do ERP Helvi.

## Ordem de leitura ao iniciar uma nova conversa ou sprint

1. `DEVELOPMENT_GUIDE.md`
2. `ARQUITETURA.md`
3. `DECISOES.md`
4. `ROADMAP.md`
5. `BACKLOG.md`
6. documentação do módulo em `MODULOS/`
7. `CHANGELOG.md`

## Regra de continuidade

Antes de criar código novo:

1. verificar se a funcionalidade já existe;
2. procurar componente, service, helper, CSS ou JavaScript reutilizável;
3. confirmar o estado atual somente no arquivo específico necessário;
4. preservar decisões já homologadas;
5. atualizar a documentação junto com o código.

## Estrutura

- `DEVELOPMENT_GUIDE.md`: metodologia permanente de desenvolvimento;
- `ARQUITETURA.md`: arquitetura oficial;
- `DECISOES.md`: decisões permanentes e regras de negócio;
- `ROADMAP.md`: estado atual e próximos marcos;
- `BACKLOG.md`: pendências priorizadas;
- `CHANGELOG.md`: evolução consolidada;
- `FRAMEWORK/`: recursos compartilhados do Framework Helvi;
- `MODULOS/`: estado funcional de cada domínio;
- `RELEASES/`: critérios de versões.
'@ | Set-Content -Path (Join-Path $docs "README.md") -Encoding UTF8

@'
# ERP Helvi 1.0

## Objetivo

Primeira versão utilizável de ponta a ponta na operação real da Helvi.

## Critérios

- fluxos principais homologados;
- integrações consistentes;
- ausência de erros críticos;
- permissões revisadas;
- interface responsiva;
- documentação atualizada;
- banco validado;
- backup e restauração definidos;
- estratégia de produção estabelecida.

## Escopo funcional esperado

- cadastros;
- produtos e catálogo;
- clientes e fornecedores;
- estoque;
- compras;
- financeiro;
- orçamentos;
- vendas;
- PDFs essenciais;
- relatórios básicos.

## Entregas restantes

- homologação integrada;
- cancelamentos e estornos;
- relatórios financeiro e de estoque;
- pesquisa global;
- auditoria;
- padronização visual e monetária;
- revisão de performance;
- backup;
- preparação de produção.
'@ | Set-Content -Path (Join-Path $docs "RELEASES\ERP_HELVI_1.0.md") -Encoding UTF8

@'
# Roadmap Atual do ERP Helvi

Atualizado em 02/08/2026.

## Concluído ou funcional no fluxo principal

- [x] autenticação, usuários e permissões;
- [x] catálogo;
- [x] produtos;
- [x] clientes;
- [x] fornecedores em operação básica;
- [x] estoque e inventário;
- [x] compras;
- [x] contas a pagar;
- [x] contas a receber;
- [x] contas financeiras e movimentações;
- [x] vendas;
- [x] integração Vendas → Estoque;
- [x] integração Vendas → Financeiro;
- [x] Comercial → Orçamentos;
- [x] PDF de Compra;
- [x] PDF de Orçamento;
- [x] conversão Orçamento → Venda;
- [x] duplicação de orçamento;
- [x] Framework Helvi em uso;
- [x] Framework PDF em uso.

## Etapa atual

### Consolidação do Comercial e do Framework Helvi

- [ ] padronizar moeda em templates, Python e PDFs;
- [ ] revisar documentação oficial;
- [ ] homologar integralmente Orçamento → Venda → Estoque → Financeiro;
- [ ] concluir filtros e pesquisa de orçamentos;
- [ ] definir envio real por WhatsApp/e-mail;
- [ ] registrar histórico de status e envios.

## Fechamento da versão 1.0

- [ ] cancelamentos e estornos críticos;
- [ ] relatório financeiro;
- [ ] relatório de estoque;
- [ ] pesquisa global;
- [ ] auditoria;
- [ ] revisão de permissões;
- [ ] revisão visual global;
- [ ] revisão de performance;
- [ ] homologação integrada;
- [ ] backup e restauração;
- [ ] preparação de produção;
- [ ] release ERP Helvi 1.0.
'@ | Set-Content -Path (Join-Path $docs "ROADMAP.md") -Encoding UTF8

Write-Host ""
Write-Host "Documentação atualizada com sucesso." -ForegroundColor Green
Write-Host "Backup anterior: $backup" -ForegroundColor Yellow
Write-Host ""
Get-ChildItem $docs -Recurse -File | Select-Object FullName