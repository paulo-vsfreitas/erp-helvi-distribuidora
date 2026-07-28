# ERP Helvi Distribuidora

Documentação oficial do ERP Helvi.

O sistema é desenvolvido em Django com arquitetura modular em camadas,
integração entre os domínios e componentes reutilizáveis.

## Documentos principais

- `ARQUITETURA.md`: arquitetura oficial;
- `PADRAO_DE_CODIGO.md`: convenções de desenvolvimento;
- `MODULOS.md`: situação atual dos módulos;
- `ROADMAP.md`: planejamento da versão 1.0;
- `CHANGELOG.md`: histórico de evolução;
- `FRAMEWORK/`: padrões e componentes reutilizáveis;
- `MODULOS/`: documentação detalhada por domínio;
- `RELEASES/`: escopo e critérios das versões.

## Regras permanentes

- preservar a arquitetura em camadas;
- manter views finas;
- concentrar regras operacionais em services;
- utilizar forms para validação de entrada;
- integrar estoque, financeiro e histórico;
- utilizar fichas como telas centrais;
- homologar cada fluxo antes de considerá-lo concluído;
- atualizar a documentação junto com o código.
