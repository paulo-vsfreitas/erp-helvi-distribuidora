# Guia de Desenvolvimento do ERP Helvi

## Objetivo

Manter e evoluir o ERP sem regredir integrações, identidade visual, permissões
ou rastreabilidade financeira.

## Preparação obrigatória

1. leia `STATUS_ATUAL.md` e `DECISOES.md`;
2. leia o documento do módulo afetado;
3. execute `git status --short` e inspecione os diffs;
4. nunca descarte alterações locais sem autorização explícita;
5. pesquise o projeto com `rg` antes de criar um recurso;
6. execute `python manage.py check` e a auditoria quando o ambiente permitir.

## Ordem recomendada

1. descrever regra, estados e efeitos;
2. localizar models, constraints e migrations;
3. ajustar forms e validações;
4. implementar ou reutilizar service;
5. manter view fina;
6. registrar URL e método HTTP correto;
7. aplicar template e Helvi UI;
8. acrescentar teste de sucesso, falha e repetição;
9. homologar integração e interface;
10. atualizar documentação;
11. revisar diff, commit e publicação.

## Convenções

- Python em português quando o domínio já usa português;
- nomes explícitos em vez de abreviações;
- `Decimal` para valores;
- `timezone.localdate()`/`timezone.now()` para datas operacionais;
- `transaction.atomic` para efeitos múltiplos;
- `select_for_update` em concorrência crítica;
- POST para alteração de estado destrutiva;
- templates sem regra de negócio;
- CSS novo com prefixo `hui-` quando transversal.

## Reuso

Antes de criar:

- cabeçalho: ver `core/templates/components/layout/page_header.html`;
- estado vazio/confirmação: ver `core/templates/components/states/`;
- componentes: ver `core/templates/helvi_ui/`;
- moeda: ver `core/formatters.py` e `core/templatetags/moeda.py`;
- comunicação: ver `core/communication/`;
- PDF: ver o Framework PDF;
- regras operacionais: ver `services/` do módulo.

## Definição de pronto

Uma entrega só está pronta quando:

- regra e permissões estão corretas;
- caminho de sucesso e erros estão tratados;
- repetição não duplica efeitos;
- estoque/financeiro permanecem consistentes;
- mensagens são compreensíveis;
- interface segue Helvi UI e é responsiva;
- testes relacionados e suíte completa passam;
- auditoria retorna zero quando aplicável;
- migrations estão sincronizadas;
- documentação e changelog foram atualizados.

## Comandos de fechamento

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test --keepdb
python manage.py auditar_integracoes --fail-on-error
git diff --check
git status --short
```

Para produção, acrescente `check --deploy`, `migrate --plan`, backup e
`collectstatic`, conforme `DEPLOYMENT.md`.
