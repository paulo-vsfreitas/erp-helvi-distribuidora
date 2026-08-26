# Changelog do ERP Helvi

## 25/08/2026 — Validação visual da Use Helvi

- mensagens de campos obrigatórios, preenchimento inválido e falhas ao salvar
  aparecem em vermelho nos formulários de Eventos, Equipe, Financeiro e
  Categorias, com destaque visual no campo que precisa de correção.
- identidade visual da Use Helvi atualizada para rose gold, grafite e off-white,
  com cards e superfícies sólidas, sem gradientes;
- cadastro de pessoas passa a oferecer uma paleta RGB fixa para a Agenda;
- paleta de participantes refinada com dez cores contrastantes e identidade da
  interface ajustada para o rose gold cobre da logo, removendo a aparência lilás;
- Financeiro recebe filtros por busca, evento, categoria, situação e período,
  com indicadores recalculados para o conjunto filtrado;
- categorias financeiras recebem listagem em cards e editor visual dedicado.
- Centro Financeiro passa a consolidar entradas e saídas em um extrato único,
  com evento opcional, filtro por tipo e indicadores de valor lançado,
  pago/recebido, pendente, resultado dos lançamentos e resultado de caixa.
- rótulos financeiros deixam de chamar valores já pagos ou recebidos de
  “previstos”; compromissos futuros permanecem identificados em A pagar e A
  receber.

## 24/08/2026 — Eventos e lucro por stand na Use Helvi

- primeiro módulo operacional da Use Helvi com agenda mensal, próximos eventos,
  cadastro de local, período, público, responsável e participantes;
- ficha do evento reúne vendas, valores recebidos, custos dos produtos,
  despesas pagas ou pendentes, lucro e margem;
- lançamento rápido de despesa reaproveita Contas a Pagar e, quando já paga,
  registra baixa e saída de caixa atomicamente;
- lançamento simplificado de vendas preserva faturamento, recebimento e custo
  até a integração futura com o módulo completo de Vendas da Use Helvi;
- categorias usuais de stands são disponibilizadas pela migration inicial;
- acesso restrito a Administrador e Gerente com a operação Use Helvi ativa.
- suíte automatizada ampliada para 189 testes.
- Financeiro passa a identificar e filtrar contas, obrigações e movimentos por
  Helvi Distribuidora ou Use Helvi, validando a conta usada na baixa;
- contatos distinguem WhatsApp, telefone e e-mail, com campo para Instagram;
- vendas rápidas recebem tipo de produto e quantidade, apoiadas por cadastro
  inicial de linhas casuais, esportivas e estojos;
- nova área de Despesas gerais registra expositores, equipamentos, materiais e
  outros gastos sem afetar o lucro de um evento específico.
- dashboard da Use Helvi exibe acessos diretos para agenda, despesas e produtos;
- cancelamento de evento exige motivo por POST, registra usuário/data, preserva
  o histórico e impede novos lançamentos no evento cancelado.

## 13/08/2026 — Mídia definitiva e ficha responsiva de produtos

- fotos principais e galeria privada passam pelo endpoint autenticado do ERP,
  evitando falhas de redirecionamento assinado no navegador;
- leitura do Supabase privado utiliza explicitamente a rota
  `/object/authenticated`, distinta da rota usada para upload;
- respostas de imagem recebem cache privado curto;
- Financeiro e Estoque usam duas colunas responsivas, com o badge de situação
  em uma linha segura, compacta e com contraste nos diferentes níveis de zoom.

## 13/08/2026 — Runtime de OCR na homologação

- homologação passa a usar uma imagem Docker reproduzível com Python 3.12.10;
- Tesseract em português/inglês e Poppler passam a integrar o runtime online;
- o build valida os binários de OCR/PDF e interrompe a publicação se faltar
  alguma dependência nativa obrigatória.
- a URL do projeto Supabase passa a ser gerenciada no painel do Render, evitando
  que uma referência antiga do Blueprint interrompa uploads de mídia.
- Gunicorn passa a usar um worker com duas threads, timeout de cinco minutos e
  reciclagem preventiva, reduzindo estouros de memória e abortos durante OCR.
- URLs assinadas do Supabase aceitam respostas com ou sem o prefixo
  `/storage/v1`, evitando caminhos duplicados e imagens quebradas.

## 12/08/2026 — OCR, cores e desempenho da importação de catálogos

- códigos numéricos visíveis passam a tolerar espaçamento e confusões comuns
  entre `0/O` e `1/I/L`, mantendo medidas ópticas fora do código do fornecedor;
- classificação visual passa a comparar as zonas superior e inferior das
  lentes e descreve degradês de azul, cinza, marrom, rosa e combinações úteis;
- análise de layout e cor reutiliza a mesma imagem e as mesmas estatísticas;
- Hero e variações reutilizam um único JPEG progressivo dimensionado por
  arquivo, recortado por coordenadas no navegador; isso reduz CPU, memória e
  os uploads ao Render/Supabase de até nove para um por catálogo;
- miniaturas deixam de carregar o original quando existe recorte persistido e
  URLs assinadas são reutilizadas por um cache curto, mantendo o bucket privado.
- o endpoint transmite os recortes no storage local mesmo com `DEBUG=False` e
  mantém redirect direto para URLs assinadas no Supabase privado;
- fotos principais e imagens definitivas dos produtos usam endpoints próprios:
  no storage local são transmitidas mesmo com `DEBUG=False` e, no Supabase,
  seguem diretamente por URL assinada;
- a confirmação gera uma foto principal otimizada a partir do Hero ou, quando
  ele não existe, da primeira variação; o catálogo completo permanece na
  galeria para conferência e auditoria;
- miniaturas de produtos preservam a proporção horizontal do óculos sem cortes,
  e as imagens completas do catálogo ficam contidas nos cartões da galeria;
- o OCR especializado evita o segundo passe geral quando o código vermelho já
  foi encontrado, e bordas externas deixam de interferir na detecção do Hero.
- o passe especializado agora envia ao OCR somente a caixa de texto vermelho,
  reduz o fallback geral e analisa a cópia temporária do upload sem baixá-la
  novamente do Storage privado.
- suíte automatizada ampliada para 174 testes aprovados.

## 12/08/2026 — Recortes persistidos na importação de catálogos

- Hero e variações C1..Cn passam a ser gerados uma única vez durante a
  análise/reanálise do catálogo;
- JPEGs e metadados visuais ficam persistidos no staging do storage privado;
- conferência normal deixa de baixar a imagem original e recalcular layout/crop;
- navegador recebe redirect para a URL assinada de cada recorte, sem proxy pelo
  worker da aplicação;
- reanálise de lotes antigos migra os recortes e limpa os objetos substituídos;
- confirmação definitiva, imagens do produto e estoque por variação preservados;
- suíte automatizada ampliada para 169 testes aprovados.

## 07/08/2026 — Fase 1 da experiência Helvi ERP

- novo login com identidade unificada Helvi ERP, preservando autenticação
  segura, bloqueio por tentativas, auditoria e primeiro acesso;
- seleção pós-login entre Helvi Distribuidora e Use Helvi;
- operação ativa armazenada na sessão e opção de troca sem novo login;
- Helvi Distribuidora mantém o dashboard atual sem alteração funcional;
- Use Helvi recebe dashboard inicial próprio no ambiente de homologação;
- fluxo coberto por testes automatizados e layouts responsivos dedicados.

## 05/08/2026 — Edição de vendas em aberto

- adicionada seleção explícita entre desenvolvimento, homologação e produção,
  com aviso visual, e-mail seguro e marcação de PDFs na homologação;
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
# 24/08/2026 — Equipes e categorias flexíveis na Use Helvi

- cadastro próprio de pessoas e equipes para reutilização entre eventos;
- seleção de equipe com inclusão automática dos integrantes;
- formatação automática e normalização de telefone/WhatsApp;
- criação, edição, exclusão lógica e reativação de categorias de despesas;
- categoria “Outros” pré-cadastrada e “Compras Homologação” retirada das novas despesas.
- edição, exclusão lógica e reativação dos tipos de produto usados nos eventos.
- módulo Financeiro da Use Helvi com lançamento de receitas recebidas/pendentes;
- relatórios por evento, período e mês com PDF oficial, WhatsApp e e-mail.
- Financeiro consolidado e recolhível, com receitas, despesas, categorias e contas;
- bloqueio de evento duplicado e de pessoa/equipe em dois eventos no mesmo dia.
# 24/08/2026 — Isolamento de módulos por operação

- menus passam a considerar simultaneamente perfil e operação ativa;
- Use Helvi fica restrita ao painel próprio, Eventos e Financeiro;
- módulos da Distribuidora e relatórios gerais são bloqueados no backend quando
  a Use Helvi está ativa;
- Eventos é bloqueado quando a operação ativa é Helvi Distribuidora;
- sessões novas exigem seleção de operação; sessões legadas sem a chave são
  tratadas como Distribuidora para manter compatibilidade com os dados atuais.

# 24/08/2026 — Lembretes e cores na Agenda da Use Helvi

- cadastro de pessoa recebe uma cor reutilizável na Agenda;
- eventos com vários integrantes combinam as cores de todos no calendário e na
  lista de próximos eventos;
- evento recebe lembrete opcional, antecedência em dias e mensagem própria;
- Agenda apresenta os lembretes vigentes em pop-up com atalhos para visualizar
  ou editar o evento.
- Instagram foi retirado do cadastro de pessoas e mantido somente nas
  informações do organizador/local de cada evento.
- eventos cancelados passam a aparecer riscados e em vermelho no
  calendário, mantendo a rastreabilidade sem parecerem compromissos ativos.
