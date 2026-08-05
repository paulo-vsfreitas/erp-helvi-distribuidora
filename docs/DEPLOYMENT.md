# Implantação do ERP Helvi

## Pré-requisitos

- Python compatível com Django 6.0;
- PostgreSQL;
- servidor WSGI/ASGI;
- proxy reverso com HTTPS;
- armazenamento persistente para mídia;
- serviço SMTP;
- rotina de backup e restauração.

## Variáveis de ambiente

Crie `.env` a partir de `.env.example` e nunca versione o arquivo real.

Obrigatórias/relevantes:

- `SECRET_KEY`;
- `DEBUG=False`;
- `ALLOWED_HOSTS`;
- `CSRF_TRUSTED_ORIGINS`;
- `DB_ENGINE=postgresql` e parâmetros `DB_*`;
- parâmetros `EMAIL_*` e `DEFAULT_FROM_EMAIL`;
- `SECURE_SSL_REDIRECT=True`;
- `SESSION_COOKIE_SECURE=True`;
- `CSRF_COOKIE_SECURE=True`;
- HSTS conforme política do domínio;
- `LOG_LEVEL`.

O arquivo carregado pode ser selecionado explicitamente com
`DJANGO_ENV_FILE`. Cada ambiente também deve declarar `APP_ENV` como
`development`, `staging` ou `production`. Homologação força o backend de e-mail
para o console, mostra identificação visual nas telas e marca os PDFs como sem
validade operacional.

Exemplo de validação da homologação no PowerShell:

```powershell
$env:DJANGO_ENV_FILE=".env.homologacao"
python manage.py check
python manage.py migrate --plan
```

## Validação antes da publicação

```powershell
python manage.py check --deploy
python manage.py makemigrations --check --dry-run
python manage.py migrate --plan
python manage.py test
python manage.py auditar_integracoes --fail-on-error
python manage.py collectstatic --noinput
```

Se houver compra histórica sem Conta a Pagar:

```powershell
python manage.py reconciliar_compras
```

Revise e só então:

```powershell
python manage.py reconciliar_compras --aplicar
```

## Backup

Antes de aplicar código ou migration:

1. gerar dump consistente do PostgreSQL;
2. copiar mídia persistente;
3. registrar versão/commit do backup;
4. restaurar o dump em ambiente separado periodicamente;
5. validar login, documentos e contagens básicas no banco restaurado.

Um backup nunca testado não atende ao critério da versão 1.0.

## Publicação

1. instalar dependências fixadas;
2. carregar variáveis do ambiente;
3. aplicar migrations;
4. executar `collectstatic`;
5. reiniciar a aplicação de forma controlada;
6. executar system check e auditoria;
7. validar arquivos estáticos, mídia e PDFs;
8. testar SMTP e compartilhamento;
9. executar smoke test dos quatro perfis.

## Smoke test

- login e primeiro acesso;
- dashboard;
- orçamento → compartilhamento → conversão;
- venda → estoque → financeiro → cancelamento;
- compra → recebimento → estoque → financeiro;
- baixa/recebimento → estorno;
- geração de PDFs;
- usuários e permissões;
- relatório de vendas e Central de Relatórios.

## Rollback

- interromper novas operações;
- preservar logs e evidências;
- restaurar código para o commit anterior;
- restaurar banco apenas se a migration/dados exigirem e houver plano aprovado;
- restaurar mídia correspondente;
- executar auditoria antes de reabrir o sistema.

Não use `git reset --hard` ou exclusão de banco como procedimento normal de
produção.

## Pós-publicação

- auditoria de integrações;
- monitoramento de erros;
- confirmação de e-mail real;
- conferência de saldos e documentos recentes;
- registro do commit/tag publicada;
- atualização de `STATUS_ATUAL.md` e da release.
