# Changelog do ERP Helvi

## 05/08/2026 — Edição de vendas em aberto

- PDFs de vendas e orçamentos agora exibem produtos distintos, itens/variações
  e total de peças.
- adicionada autorização granular de ações no backend: Vendedor consulta
  Estoque, Produtos e Catálogo, sem cadastrar, editar, inativar ou movimentar;
- tentativas de executar ações proibidas por URL direta retornam acesso negado;
- cancelamentos podem ser solicitados por qualquer perfil, mas exigem usuário e
  senha de Administrador e registram solicitante e autorizador separadamente;
- login passa a bloquear por 15 minutos após cinco falhas na mesma combinação
  de usuário e IP, mantendo auditoria de sucessos, falhas e bloqueios;
- sessão padrão corrigida para 30 minutos sem atividade.
- cabeçalho dos PDFs redistribui WhatsApp, Instagram e Facebook em uma grade
  responsiva de duas colunas, evitando cortes em identificadores longos.
- expiração de sessão e páginas com CSRF antigo deixam de exibir a tela técnica
  403: o sistema renova o login ou recarrega a página com aviso seguro.

- incluído botão **Editar venda** na ficha das vendas em aberto;
- formulário de edição carrega cliente, entrega, itens e variações de cor já selecionadas;
- recálculo seguro de subtotal, descontos, frete e total ao salvar;
- vendas finalizadas, canceladas ou com integrações processadas permanecem protegidas;
- corrigida a leitura de valores monetários digitados com vírgula no formulário.
- cores disponíveis passaram a ser clicáveis no card de busca do produto;
- o mesmo produto pode compor a venda mais de uma vez quando as cores diferem;
- administradores e gerentes podem corrigir o vendedor diretamente na lista de vendas.
- cadastro de produtos ganhou a opção explícita **Produto sem variação de cor**,
  com interface simplificada e proteção para produtos que já possuem cores.
- corrigido o envio de vendas com produtos sem cor misturados a produtos com
  variação, mantendo cada cor associada à linha correta.
- orçamento recebeu a mesma seleção visual por produto e cor usada nas vendas;
- resumo PDF da venda foi redesenhado com identidade institucional, logo das
  Configurações, dados completos do cliente, entrega, pagamento e fechamento.
- Configurações recebeu Instagram, Facebook e seleção dos canais exibidos nos PDFs;
- orçamento adotou o mesmo padrão institucional completo do documento de venda;
- ficha da venda permite compartilhar o PDF pelo recurso nativo do dispositivo;
- Administrador, Gerente e Financeiro podem corrigir o vendedor de qualquer
  venda mediante confirmação da própria senha;
- datas e horários programáticos foram normalizados para `America/Sao_Paulo`.
- site institucional movido para o rodapé dos PDFs; WhatsApp e Instagram agora
  aparecem com ícones vetoriais e os documentos exibem o último horário atualizado.
- cabeçalho evita repetir razão social quando ela é igual ao nome fantasia.
- PDFs de vendas e orçamentos exibem apenas a data própria do documento, sem
  horário, última atualização ou data/hora de geração.

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
# Alterações de 04/08/2026

- Cadastro e edição de produtos passam a aceitar Código, Modelo, Marca,
  Coleção e Nome/descrição da variação de cor em branco, com tratamento
  seguro nas listagens, fichas, buscas, PDFs e integrações.
- Corrigido o alinhamento da listagem de produtos para exibir estoque, preço,
  situação e ações nas colunas corretas, com moeda e estados padronizados.
- Adicionados endereços estruturados de clientes, modalidade e endereço de
  entrega em orçamentos/vendas, frete condicionado ao envio, variações de cor
  nos itens e resumo em PDF para vendas em aberto. Os seletores de produtos
  também foram ampliados para melhorar a leitura operacional.
# Ajuste visual do cabeçalho dos PDFs

- Reorganizados nome, dados fiscais, contatos, redes sociais e endereço no cabeçalho dos PDFs de vendas e orçamentos.
- Substituído o ícone simplificado do WhatsApp por uma representação oficial, maior e mais legível.
# Correção do fluxo de caixa e rentabilidade

- Corrigido o saldo anterior do fluxo de caixa, que incluía novamente as
  movimentações do próprio período quando nenhum filtro de data era enviado.
- Definido o mês corrente como período padrão do fluxo de caixa.
- Criada a página **Financeiro → Lucro e Margem**, com receita dos produtos,
  custo das mercadorias, lucro bruto, margem, frete e detalhamento por venda.
- Adicionado custo unitário histórico ao item da venda, consolidado no momento
  da finalização para não ser alterado por atualizações futuras do produto.
# Refinamento da ficha de venda

- Corrigida a inversão entre produto e variação de cor na tabela de itens.
- Códigos opcionais deixam de exibir `None` e passam a mostrar um estado claro.
- O resumo agora diferencia produtos distintos, itens/variações e quantidade de
  peças.
- Melhorada a leitura da tabela com identificação visual de códigos e cores.
# Cabeçalho da ficha de venda

- Removido do topo o botão duplicado de resumo em PDF; a ação permanece no
  painel próprio de ações.
- O destaque do cliente agora apresenta documento, responsável, contato e
  e-mail quando cadastrados, além do número e dos estados da venda.
- Eliminada a repetição do cliente dentro da seção de dados da venda.
# Alinhamento dos estados da venda

- Reorganizados número, situação e pagamento em uma grade com linhas e colunas
  estáveis, evitando sobreposição dos rótulos com os selos de status.
- Corrigido o carregamento do CSS específico na ficha, com atualização de
  versão para impedir o uso do estilo antigo em cache.
