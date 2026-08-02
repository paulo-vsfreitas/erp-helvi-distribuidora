# Documentação Oficial — ERP Helvi

Esta pasta é a fonte oficial de contexto arquitetural, funcional e de planejamento do ERP Helvi.

## Ordem de leitura ao iniciar uma nova conversa ou sprint

1. `DEVELOPMENT_GUIDE.md`
2. `ARQUITETURA.md`
3. `DECISOES.md`
4. `ROADMAP.md`
5. `BACKLOG.md`
6. documentação do módulo em `MODULOS/`
7. `CHANGELOG.md`

## Regra de continuidade

Antes de criar código novo:

1. verificar se a funcionalidade já existe;
2. procurar componente, service, helper, CSS ou JavaScript reutilizável;
3. confirmar o estado atual somente no arquivo específico necessário;
4. preservar decisões já homologadas;
5. atualizar a documentação junto com o código.

## Estrutura

- `DEVELOPMENT_GUIDE.md`: metodologia permanente de desenvolvimento;
- `ARQUITETURA.md`: arquitetura oficial;
- `DECISOES.md`: decisões permanentes e regras de negócio;
- `ROADMAP.md`: estado atual e próximos marcos;
- `BACKLOG.md`: pendências priorizadas;
- `CHANGELOG.md`: evolução consolidada;
- `FRAMEWORK/`: recursos compartilhados do Framework Helvi;
- `MODULOS/`: estado funcional de cada domínio;
- `RELEASES/`: critérios de versões.
