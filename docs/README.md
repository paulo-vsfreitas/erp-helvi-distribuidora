# Documentação Oficial — ERP Helvi

Esta pasta é a fonte de verdade arquitetural, funcional e operacional do ERP.
Documentos que descrevem estado possuem data de atualização; decisões
permanentes continuam válidas até serem substituídas explicitamente.

## Leitura obrigatória para manutenção ou continuação

1. [`STATUS_ATUAL.md`](STATUS_ATUAL.md) — o que está pronto, validado e limitado;
2. [`DEVELOPMENT_GUIDE.md`](DEVELOPMENT_GUIDE.md) — como trabalhar no projeto;
3. [`ARQUITETURA.md`](ARQUITETURA.md) — camadas e dependências;
4. [`DECISOES.md`](DECISOES.md) — regras que não devem ser alteradas por acidente;
5. documentação específica em [`MODULOS/`](MODULOS/);
6. [`INTEGRACOES.md`](INTEGRACOES.md) — efeitos entre os módulos;
7. [`TESTES.md`](TESTES.md) — validação obrigatória;
8. [`MANUTENCAO.md`](MANUTENCAO.md) — rotinas e diagnóstico;
9. [`ROADMAP.md`](ROADMAP.md) e [`BACKLOG.md`](BACKLOG.md) — evolução futura.

## Índice

### Estado e planejamento

- [`STATUS_ATUAL.md`](STATUS_ATUAL.md)
- [`ROADMAP.md`](ROADMAP.md)
- [`BACKLOG.md`](BACKLOG.md)
- [`CHANGELOG.md`](CHANGELOG.md)
- [`RELEASES/ERP_HELVI_1.0.md`](RELEASES/ERP_HELVI_1.0.md)

### Engenharia e operação

- [`ARQUITETURA.md`](ARQUITETURA.md)
- [`DECISOES.md`](DECISOES.md)
- [`DEVELOPMENT_GUIDE.md`](DEVELOPMENT_GUIDE.md)
- [`INTEGRACOES.md`](INTEGRACOES.md)
- [`MAPA_TELAS.md`](MAPA_TELAS.md)
- [`TESTES.md`](TESTES.md)
- [`MANUTENCAO.md`](MANUTENCAO.md)
- [`DEPLOYMENT.md`](DEPLOYMENT.md)

### Interface e recursos compartilhados

- [`HELVI_UI.md`](HELVI_UI.md)
- [`FRAMEWORK/README.md`](FRAMEWORK/README.md)
- [`FRAMEWORK/COMPONENTES.md`](FRAMEWORK/COMPONENTES.md)
- [`FRAMEWORK/SERVICES.md`](FRAMEWORK/SERVICES.md)
- [`FRAMEWORK/FORMATADORES.md`](FRAMEWORK/FORMATADORES.md)
- [`FRAMEWORK/NOMENCLATURA.md`](FRAMEWORK/NOMENCLATURA.md)
- [`FRAMEWORK/PDF.md`](FRAMEWORK/PDF.md)

### Módulos

- [`MODULOS/CADASTROS.md`](MODULOS/CADASTROS.md)
- [`MODULOS/COMERCIAL.md`](MODULOS/COMERCIAL.md)
- [`MODULOS/VENDAS.md`](MODULOS/VENDAS.md)
- [`MODULOS/COMPRAS.md`](MODULOS/COMPRAS.md)
- [`MODULOS/ESTOQUE.md`](MODULOS/ESTOQUE.md)
- [`MODULOS/FINANCEIRO.md`](MODULOS/FINANCEIRO.md)
- [`MODULOS/FORNECEDORES.md`](MODULOS/FORNECEDORES.md)

## Regra de continuidade

Antes de criar código novo:

1. execute `git status --short` e inspecione os diffs relevantes;
2. confirme se a funcionalidade já existe;
3. procure componente, service, helper, CSS ou JavaScript reutilizável;
4. preserve as regras descritas em `DECISOES.md`;
5. não marque algo como concluído sem testes e homologação proporcional ao risco;
6. atualize status, módulo e changelog quando a entrega mudar o produto.
