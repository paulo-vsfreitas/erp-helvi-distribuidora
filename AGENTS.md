# Instruções de manutenção — ERP Helvi

Estas regras valem para todo o repositório.

## Antes de alterar

1. Leia `docs/STATUS_ATUAL.md`.
2. Leia `docs/DECISOES.md` e `docs/ARQUITETURA.md`.
3. Leia o documento correspondente em `docs/MODULOS/`.
4. Execute `git status --short` e preserve rigorosamente alterações locais.
5. Pesquise o projeto antes de criar service, componente, formatador ou CSS.

## Implementação

- Mantenha views finas e regras de negócio nos services.
- Use `transaction.atomic` em operações compostas.
- Garanta idempotência em estoque, financeiro, conversões e cancelamentos.
- Use `Decimal` para valores monetários.
- Use `core.formatters.formatar_moeda_br` e o filtro `moeda`.
- Novas páginas internas seguem `docs/HELVI_UI.md`.
- Não aplique `max-width` local em `.hui-module-page`.
- Ações destrutivas alteram estado somente por POST.
- Não edite migrations já aplicadas; crie uma nova migration.
- Não versione `.env`, credenciais, bancos, logs ou mídia privada.

## Validação obrigatória

```text
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test --keepdb
python manage.py auditar_integracoes --fail-on-error
git diff --check
```

Mudanças visuais devem ser homologadas em desktop, tela ampla/zoom reduzido e
768 px. Mudanças de integração exigem teste do fluxo completo afetado.

## Documentação

Atualize no mesmo commit:

- `docs/STATUS_ATUAL.md` quando o estado do produto mudar;
- o arquivo em `docs/MODULOS/` correspondente;
- `docs/CHANGELOG.md` para entregas funcionais;
- `docs/ROADMAP.md` e `docs/BACKLOG.md` quando o planejamento mudar;
- `docs/RELEASES/` quando houver marco de versão.

Não marque uma funcionalidade como concluída apenas porque a interface existe.
Confirme regra, integração, permissão, testes e homologação.
