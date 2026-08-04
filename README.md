# ERP Helvi

ERP web da Helvi Distribuidora de Armações, desenvolvido em Django para cobrir
cadastros, catálogo, clientes, fornecedores, estoque, compras, financeiro,
orçamentos, vendas, usuários, configurações e relatórios.

## Estado da versão

Em 04/08/2026, o projeto está em **release candidate da versão 1.0**:

- 19 telas principais homologadas com o Helvi UI;
- fluxos críticos integrados e auditados;
- 61 testes automatizados aprovados;
- nenhuma migração pendente;
- nenhuma divergência encontrada pela auditoria de integrações.

O retrato completo e as limitações conhecidas estão em
[`docs/STATUS_ATUAL.md`](docs/STATUS_ATUAL.md).

## Início rápido

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

O `.env.example` usa PostgreSQL como referência. Para desenvolvimento local
isolado, `DB_ENGINE=sqlite` ativa o SQLite.

## Validação mínima

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
python manage.py auditar_integracoes --fail-on-error
```

## Documentação

Comece por [`docs/README.md`](docs/README.md). O índice aponta para:

- status atual e próximos passos;
- arquitetura e decisões permanentes;
- módulos e integrações;
- Helvi UI e Framework Helvi;
- testes, manutenção e implantação;
- histórico, backlog e release.

## Regra de manutenção

Antes de alterar o projeto:

1. leia o status atual e a documentação do módulo;
2. confira o estado do Git e preserve alterações locais;
3. procure services, componentes e formatadores existentes;
4. mantenha views finas e regras transacionais nos services;
5. acrescente testes para a regra alterada;
6. execute a auditoria e atualize a documentação no mesmo commit.
