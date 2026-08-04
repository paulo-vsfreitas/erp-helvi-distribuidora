# Changelog do ERP Helvi

## 04/08/2026 — Relatórios analíticos dedicados

- substituídos os atalhos operacionais da Central por 12 relatórios dedicados;
- adicionados filtros por período, pesquisa e status conforme o domínio;
- adicionados KPIs, tabelas detalhadas, paginação e acesso às fichas de origem;
- preservado o relatório de Vendas existente, totalizando 13 análises operantes;
- incluídos períodos rápidos, indicação de filtros ativos e paginação configurável;
- todos os relatórios oferecem CSV e versão otimizada para impressão;
- Vendas, Contas a Receber, Contas a Pagar, Fluxo de Caixa, Posição de Estoque
  e Compras emitem PDF oficial paginado com identificação da empresa.

## 04/08/2026 — Auditoria estrutural e limpeza

- remoção da aplicação vazia `relatorios`; a Central permanece no `core`;
- exclusão de templates, scripts, services e scaffolds PDF sem referências;
- correção de imports residuais de módulos vazios;
- Central de Relatórios simplificada para conter somente destinos funcionais;
- sintaxe Python/JavaScript, banco, migrations, integrações e 73 testes validados.

## 04/08/2026 — Central de Configurações de comunicação

- assunto e mensagens padrão de e-mail e WhatsApp editáveis na interface;
- editor guiado com inserção de variáveis no cursor, contador e prévia instantânea;
- modelos iniciais adequados à formalidade de e-mail e WhatsApp, personalizáveis pelo usuário;
- suporte validado às variáveis de cliente, orçamento, total, validade,
  vendedor e empresa;
- integração dos modelos ao compartilhamento de orçamentos;
- fallback preservado para as mensagens originais quando os campos estão vazios;
- testes de validação, renderização, personalização e compatibilidade adicionados.

## 04/08/2026 — Release Candidate 1.0

### Interface e Framework Helvi

- aplicação do Helvi UI nas 19 telas principais;
- cabeçalhos, cards, filtros, fichas, formulários e confirmações padronizados;
- layout fluido corrigido para telas amplas e zoom reduzido;
- revisão responsiva sem rolagem horizontal global a 768 px;
- componentes compartilhados para páginas, fichas, estados e ações;
- CSS global consolidado e CSS específico de Vendas e Usuários;
- edição de usuário redesenhada;
- telas de Compras, Fornecedores e Vendas modernizadas.

### Comercial — Orçamentos

- Valor orçado corrigido para carteira ativa;
- cards de Orçamentos, Rascunhos e Aprovados clicáveis;
- filtro seguro por status, busca e filtros adicionais;
- edição completa do orçamento;
- conversão em venda corrigida e protegida contra duplicidade;
- compartilhamento por e-mail com PDF;
- preparação do WhatsApp com histórico;
- registro de compartilhamentos e resultados;
- formatação monetária brasileira;
- testes ampliados de cálculo, filtro, edição, conversão e comunicação.

### Vendas

- total, número, responsável e bloqueios de finalização revisados;
- pagamentos à vista e a prazo corrigidos;
- baixa de estoque e Conta a Receber integradas;
- cancelamento por POST com motivo, estorno de estoque e reversão financeira;
- constraints de valores monetários;
- listagem, ficha, nova venda e relatório ajustados ao Helvi UI.

### Compras

- listagem e ficha padronizadas;
- numeração comercial protegida;
- recebimento atualiza estoque e custo;
- geração financeira idempotente;
- compras históricas #1 e #3 conciliadas, totalizando R$ 2.223,00;
- comando seguro de conciliação adicionado;
- testes de integração ampliados.

### Financeiro

- estorno manual de baixa e recebimento;
- motivo obrigatório, histórico e proteção contra repetição;
- movimento financeiro inverso e recálculo atômico;
- valores líquidos corrigidos nas fichas;
- dashboard, contas, categorias, movimentos e formulários alinhados ao Helvi UI.

### Usuários e segurança

- fluxo obrigatório de primeiro acesso;
- matriz de permissões aplicada por middleware;
- ações destrutivas relevantes restritas a POST;
- edição e listagem de usuários redesenhadas;
- configuração de produção por ambiente;
- HTTPS, cookies seguros, HSTS, headers e logging configuráveis.

### Produtos, estoque e cadastros

- constraints contra saldo e preços negativos;
- inativação por POST;
- telas de catálogo, clientes, produtos, estoque e inventário padronizadas;
- operações de estoque protegidas contra saldo inválido.

### Relatórios, auditoria e documentação

- Central de Relatórios com 13 entradas ativas;
- relatório de vendas disponível;
- comando `auditar_integracoes` criado;
- comando `reconciliar_compras` criado;
- suíte ampliada para 61 testes;
- documentação técnica, funcional, operacional e de release atualizada.

## Julho de 2026

- módulos de Compras, Estoque, Financeiro, Fornecedores e Vendas evoluídos;
- arquitetura em camadas consolidada;
- fichas padronizadas;
- integrações Compras → Estoque/Financeiro e Vendas → Estoque/Financeiro;
- Contas a Pagar e Contas a Receber;
- relatórios iniciais;
- modularização de views e services.

## Junho de 2026

- fundação do projeto;
- autenticação e usuários;
- catálogo, produtos e clientes;
- permissões e identidade visual inicial.
