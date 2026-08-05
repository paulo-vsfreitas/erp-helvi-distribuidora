# Módulo Estoque

Atualizado em 04/08/2026.

## Responsabilidade

Controlar saldo, entradas, saídas, ajustes, inventários e rastreabilidade das
integrações com Compras e Vendas.

## Implementado

- dashboard e indicadores;
- lista de movimentações e filtros;
- entradas manuais e por compra;
- saídas manuais e por venda;
- estornos de compra/venda conforme os fluxos de cancelamento;
- ajustes com motivo;
- inventários, conferência e conclusão;
- origem, usuário, saldo anterior e saldo atual;
- alerta operacional de estoque mínimo no dashboard;
- bloqueio de saldo negativo;
- telas padronizadas com Helvi UI.
- Vendedor possui acesso somente de consulta; entradas, saídas, ajustes e
  gestão de inventários são restritos a Administrador e Gerente no backend.

## Regras

- saldo é alterado por service, não diretamente na view;
- toda alteração gera movimentação;
- saída exige saldo suficiente;
- recebimento de compra e finalização de venda são idempotentes;
- cancelamento registra movimento compensatório;
- inventário preserva as diferenças e o responsável.

## Arquivos principais

- models: `estoque/models.py`;
- services: `estoque/services/`;
- views: `estoque/views/`;
- templates: `estoque/templates/estoque/`.

## Evoluções não bloqueantes

- locais múltiplos;
- transferências;
- endereçamento;
- relatório dedicado de giro e cobertura;
- contagem por importação ou dispositivo.
