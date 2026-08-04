# Changelog do ERP Helvi

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
