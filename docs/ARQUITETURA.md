# Arquitetura Oficial do ERP Helvi

Atualizado em 04/08/2026.

## Stack

- Python e Django 6.0.6;
- PostgreSQL em homologação/produção e SQLite opcional em desenvolvimento;
- templates Django, Bootstrap, Bootstrap Icons e Helvi UI;
- JavaScript progressivo sem framework SPA;
- ReportLab para PDFs;
- Pillow para imagens;
- `python-dotenv` para configuração local.

Os ambientes são selecionados por `DJANGO_ENV_FILE` e identificados por
`APP_ENV`. Desenvolvimento, homologação e produção usam bancos e mídias
independentes; apenas código e migrations aprovados avançam entre ambientes.

## Domínios

Cada aplicação Django representa um domínio. O `core` concentra apenas recursos
transversais e a composição do dashboard/relatórios.

```text
core             recursos compartilhados, dashboard, relatórios e comandos
usuarios         autenticação, perfis, permissões e primeiro acesso
catalogo         marcas, coleções, gêneros e tipos de armação
produtos         produtos, preços, estoque de referência e imagens
clientes         clientes e óticas
fornecedores     fornecedores e visão de relacionamento
estoque          movimentações, ajustes e inventários
compras          documentos de compra e recebimento
financeiro       contas, parcelas, movimentos, baixas e recebimentos
comercial        orçamentos e compartilhamentos
vendas           vendas, pagamento, finalização e cancelamento
configuracoes    dados da empresa e modelos de comunicação
```

A Central de Relatórios é uma composição transversal do `core`; não existe
uma aplicação Django separada sem responsabilidade de domínio.

## Estrutura padrão

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
└── tests.py ou tests/
```

Nem todo módulo precisa de todas as pastas. Não crie uma camada vazia apenas
para reproduzir a estrutura.

## Fluxo de uma requisição

```text
URL
→ middleware de autenticação/permissão
→ view fina
→ form de entrada
→ service de negócio
→ models/banco
→ contexto
→ template Helvi UI ou redirecionamento
```

## Responsabilidades

### Models

- entidades, relacionamentos e choices;
- constraints e indexes;
- propriedades simples derivadas do próprio registro;
- invariantes locais de persistência.

Não devem orquestrar integrações complexas entre módulos.

### Forms

- validação e normalização da entrada;
- widgets, labels e mensagens;
- construção de dados confiáveis para o service.

### Views

- autenticação e autorização específica quando necessária;
- GET/POST, formulários, mensagens e redirecionamentos;
- chamada de services;
- montagem simples do contexto.

Views não devem calcular estoque, valores financeiros ou executar várias
gravações coordenadas.

### Services

- regras operacionais;
- transações e bloqueios com `select_for_update`;
- idempotência;
- integração explícita entre domínios;
- criação de histórico e efeitos correlatos.

Services não recebem `request`, não renderizam templates e não retornam
`HttpResponse`.

### Core e Framework Helvi

O `core` contém somente recursos reutilizáveis, como:

- layout, componentes e Helvi UI;
- formatação e template tags;
- comunicação genérica de e-mail;
- PDF compartilhado;
- central de relatórios;
- comandos de auditoria e conciliação.

Regra de dependência:

```text
módulos de negócio → core
```

Evitar fazer o `core` importar models de negócio para utilidades genéricas. A
central de relatórios e comandos de auditoria são composições deliberadas da
aplicação, não bibliotecas genéricas.

## Persistência e consistência

- valores monetários usam `Decimal`;
- datas usam timezone do Django e `America/Sao_Paulo`;
- operações compostas usam `transaction.atomic`;
- registros concorrentes críticos usam `select_for_update`;
- números comerciais são distintos de `pk`;
- constraints impedem valores negativos e combinações inválidas relevantes;
- integrações devem ser idempotentes;
- estornos preservam origem e criam contrapartida rastreável.

## Identificadores

- `pk`: identificador interno;
- `numero`: identificador comercial persistido;
- `codigo`: apresentação formatada ou código de catálogo;
- documentos comerciais preferem `numero` na URL pública interna;
- nenhum template deve depender de um número ausente.

## Segurança e permissões

- autenticação padrão do Django com model `usuarios.Usuario`;
- perfis ADM, GER, VEN e FIN;
- matriz central em `usuarios/permissoes.py`;
- aplicação por `PermissaoModuloMiddleware`;
- matriz adicional por ação para impedir operações sensíveis por URL direta;
- autorização registra separadamente solicitante e autorizador quando uma
  credencial administrativa é exigida;
- primeiro acesso força definição de senha pessoal;
- CSRF ativo e ações destrutivas por POST;
- produção exige HTTPS, cookies seguros, HSTS e `DEBUG=False`.
- tentativas de login são limitadas por usuário e IP, persistidas para auditoria
  e configuradas por variáveis de ambiente.

## Interface

- páginas internas herdam `core/templates/core/base.html`;
- páginas públicas herdam `core/templates/public/base_public.html`;
- Helvi UI complementa Bootstrap;
- `.hui-module-page` é fluido e não recebe `max-width` local;
- CSS específico fica no módulo apenas quando o comportamento não é transversal;
- fichas são a tela central de entidades e documentos relevantes.

## PDFs e comunicação

- documentos usam o Framework PDF do `core`;
- orçamento e compra possuem PDF;
- e-mail utiliza a camada `core/communication` e backend configurável;
- WhatsApp é integração por URL preparada no navegador, não API de envio.
- modelos editáveis são validados e renderizados por `configuracoes`; o
  `core/communication` permanece responsável apenas pelo transporte genérico.

## Comandos operacionais

- `auditar_integracoes`: somente leitura, verifica invariantes críticas;
- `reconciliar_compras`: simula ou cria Contas a Pagar históricas ausentes.

Detalhes estão em `MANUTENCAO.md` e `INTEGRACOES.md`.
