# Operação e Manutenção

## Checklist antes de alterar código

```powershell
git status --short
git diff --stat
python manage.py check
python manage.py auditar_integracoes
```

Depois:

1. leia `STATUS_ATUAL.md`, `DECISOES.md` e o documento do módulo;
2. inspecione alterações locais e nunca as descarte sem autorização;
3. localize a view, form, service, template, CSS e testes já existentes;
4. confirme a regra no model e nas migrations antes de alterar o banco;
5. faça mudanças pequenas e com teste de regressão.

## Checklist depois de alterar código

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
python manage.py auditar_integracoes --fail-on-error
git diff --check
git status --short
```

Também valide visualmente as rotas afetadas em largura ampla e reduzida.

## Diagnóstico de integrações

O comando abaixo é somente leitura:

```powershell
python manage.py auditar_integracoes
```

Ele verifica:

- orçamento convertido sem venda;
- venda finalizada sem baixa de estoque;
- venda finalizada sem Conta a Receber;
- venda paga com saldo pendente;
- compra recebida sem entrada de estoque;
- compra recebida sem Conta a Pagar;
- produto com saldo ou preço negativo.

Em automações use `--fail-on-error` para retornar código diferente de zero.

## Conciliação de compras históricas

Primeiro execute a simulação:

```powershell
python manage.py reconciliar_compras
```

Revise cada número e valor. Somente depois faça a alteração:

```powershell
python manage.py reconciliar_compras --aplicar
```

O comando cria apenas Contas a Pagar ausentes de compras já recebidas. Uma
segunda execução deve informar que nenhuma compra exige conciliação.

## Migrações

- nunca edite uma migration já aplicada em produção;
- gere uma nova migration para alterações de schema;
- revise operações e constraints antes de aplicar;
- execute `migrate --plan` e faça backup antes da publicação;
- mantenha os models e migrations no mesmo commit.

## Dados e dinheiro

- use `Decimal`, nunca `float`;
- não altere saldos diretamente quando existir service operacional;
- estornos preservam o lançamento original e criam o movimento inverso;
- cancelamentos devem ser atômicos e registrar usuário, data e motivo;
- após correções de dados, execute a auditoria de integrações.

## Interface

- toda página interna herda `core/base.html`;
- use `.hui-module-page` e o `page_header` do Helvi UI;
- não aplique `max-width` local ao contêiner principal;
- tabelas extensas devem ficar em contêiner responsivo;
- telas públicas usam `core/templates/public/base_public.html`;
- mudanças globais de CSS exigem homologação em todos os módulos principais.

## Git

- mantenha código, testes e documentação juntos;
- não versione `.env`, credenciais, banco local, logs ou mídia particular;
- confira `git diff --cached` antes do commit;
- use mensagens de commit que descrevam o marco funcional;
- crie tags somente após homologação e backup do artefato publicado.

## Incidentes comuns

### Banco de testes já existe

Use:

```powershell
python manage.py test --keepdb
```

### Auditoria encontra compra sem Conta a Pagar

Use a conciliação em modo de simulação, valide os dados e só então aplique.

### Página perde proporção em zoom reduzido

Procure `max-width`, largura fixa ou contêiner Bootstrap local envolvendo
`.hui-module-page`. O layout oficial é fluido.

### Usuário fica preso no primeiro acesso

Confirme `usuario.primeiro_acesso`, a rota `usuarios:primeiro_acesso` e o
middleware `PermissaoModuloMiddleware`. Não desative o middleware para contornar
o problema.
