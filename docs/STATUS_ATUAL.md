# Status Atual do ERP Helvi

Atualizado em **07/08/2026**.

## Resumo executivo

O ERP Helvi está em **release candidate 1.0**. Os fluxos essenciais funcionam de
ponta a ponta, as telas principais compartilham o Helvi UI, as integrações
críticas possuem auditoria e o pacote automatizado possui 132 testes aprovados.

O código está pronto para a homologação de aceitação e para a preparação do
ambiente definitivo. Publicação em produção ainda exige backup, configuração
de infraestrutura, SMTP real, HTTPS e plano de restauração.
O projeto já suporta configuração isolada de homologação, com banco próprio,
aviso visual permanente, e-mail em modo seguro e PDFs identificados.
O acesso de homologação agora usa a identidade Helvi ERP e seleciona a operação
ativa entre Helvi Distribuidora e Use Helvi. A Distribuidora preserva o painel
atual e a Use Helvi possui um dashboard inicial próprio para evolução modular.
Há também uma especificação de implantação gratuita no Render, ligada à branch
de homologação e com segredos fornecidos apenas pelo painel da hospedagem.

A Central de Configurações permite manter os dados institucionais, WhatsApp,
Instagram, Facebook, os canais exibidos nos PDFs e os modelos
padrão de WhatsApp e e-mail usados no compartilhamento de orçamentos. O editor
insere variáveis de forma guiada e mostra uma prévia com dados de exemplo.
Os PDFs de vendas e orçamentos apresentam também o resumo de produtos distintos,
itens/variações e peças.

## Validação registrada

- `python manage.py test --keepdb`: **132 testes aprovados**;
- `python manage.py check`: nenhum problema;
- `python manage.py makemigrations --check --dry-run`: nenhuma mudança;
- `python manage.py auditar_integracoes`: zero divergências;
- `python manage.py reconciliar_compras`: nenhuma compra pendente;
- homologação visual de 19 rotas principais;
- nenhuma rolagem horizontal indevida a 768 px;
- conteúdo ocupando aproximadamente 96% da área útil a 1920 px;
- nenhum erro registrado no console do navegador durante a homologação.

## Módulos funcionais

| Domínio | Estado | Destaques |
|---|---|---|
| Autenticação e usuários | Concluído | perfis, primeiro acesso, edição, ativação e proteção por módulo |
| Catálogo | Concluído | marcas, coleções, gêneros e tipos de armação |
| Produtos | Concluído | ficha, imagens, preços, estoque, filtros e identificação opcional |
| Clientes / Óticas | Concluído | cadastro, edição, pesquisa e vínculo comercial |
| Fornecedores | Concluído | dashboard, filtros, ficha e vínculo com compras |
| Estoque | Concluído no escopo 1.0 | entradas, saídas, ajustes, inventários e rastreio |
| Compras | Concluído | criação, edição, recebimento, estoque, custo, financeiro, cancelamento e PDF |
| Financeiro | Concluído no escopo 1.0 | contas, parcelas, baixas, recebimentos, estornos, fluxo e rentabilidade comercial |
| Comercial | Concluído | orçamento, edição, filtros, PDF, compartilhamento, status e conversão |
| Vendas | Concluído | venda direta, edição em aberto, orçamento, pagamento, estoque, financeiro e cancelamento |
| Relatórios | Concluído no escopo 1.0 | 13 análises com filtros, KPIs, CSV e impressão; 6 PDFs oficiais |
| Configurações | Funcional | dados institucionais e modelos de comunicação com variáveis validadas |

## Regras críticas já implementadas

- valor orçado considera somente rascunhos, enviados e aprovados;
- conversão de orçamento em venda é idempotente;
- finalização de venda gera estoque e financeiro uma única vez;
- cancelamento de venda reverte estoque e financeiro;
- recebimento de compra atualiza estoque, custo e Conta a Pagar;
- cancelamento de compra valida e reverte efeitos permitidos;
- estorno manual de baixa ou recebimento exige motivo e gera movimento inverso;
- operações destrutivas relevantes são processadas por `POST`;
- produtos e valores financeiros não podem ficar negativos pelas regras atuais;
- o custo do item é preservado na finalização da venda para manter o lucro
  histórico estável mesmo após alterações no cadastro do produto;
- o middleware aplica matrizes centrais por módulo e por ação sensível;
- Vendedor consulta Estoque, Produtos e Catálogo sem conseguir alterá-los por
  botões ou URLs diretas;
- cancelamento de venda exige credencial administrativa e audita separadamente
  o solicitante e o Administrador autorizador;
- cinco falhas de login por usuário e IP bloqueiam novas tentativas por 15
  minutos, com auditoria de sucessos, falhas e bloqueios;
- novos usuários criados pelo ERP passam pelo fluxo de primeiro acesso.

## Limitações conhecidas que não bloqueiam a versão 1.0

- WhatsApp prepara um link e registra o resultado como “preparado”; a confirmação
  final ocorre no aplicativo do usuário;
- e-mail depende de SMTP configurado; em desenvolvimento, o backend padrão pode
  apenas escrever a mensagem no console;
- os 13 relatórios possuem visão analítica dedicada, exportação CSV e impressão;
  gráficos interativos permanecem como evolução futura;
- não há locais múltiplos de estoque nem transferências entre depósitos;
- pesquisa global entre todos os módulos ainda não existe;
- não há API pública nem aplicativo móvel nesta versão;
- monitoramento externo, tarefas assíncronas e armazenamento de mídia em nuvem
  dependem da infraestrutura escolhida para produção.

## Próxima ação recomendada

1. criar backup verificável do banco e da mídia;
2. preparar ambiente de homologação equivalente à produção;
3. executar o roteiro de aceitação com usuários ADM, GER, VEN e FIN;
4. configurar e validar SMTP, HTTPS, estáticos e mídia;
5. publicar a versão 1.0 e criar a tag correspondente;
6. iniciar apenas depois o backlog evolutivo.
