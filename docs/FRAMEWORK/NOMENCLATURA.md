# Nomenclatura do Framework Helvi

## Identificação

- `pk`: identificador interno;
- `numero`: identificador comercial persistido;
- `codigo`: código de catálogo ou representação formatada;
- `origem_id`: identificador técnico da entidade de origem;
- `responsavel`: pessoa que realizou a operação na apresentação;
- `vendedor`: vínculo técnico comercial quando esse é o campo do model.

## Estados

- `status`: situação operacional;
- `status_pagamento`: situação financeira do documento;
- `ativo`: disponibilidade de cadastro;
- `estornado/estornada`: operação compensada;
- `cancelado_por`, `cancelado_em`, `motivo_cancelamento`: auditoria de cancelamento;
- campos equivalentes de estorno seguem o mesmo padrão.

## Valores

- `subtotal`: soma antes de ajustes gerais;
- `desconto`: redução;
- `frete`: acréscimo de entrega;
- `total`: valor final;
- `valor_pago`: principal pago;
- `valor_recebido`: principal recebido;
- `valor_movimentado`: efeito em caixa incluindo juros, multa e desconto;
- `saldo`: total menos principal pago/recebido;
- `preco_custo` e `preco_venda`: valores do produto.

## Interface

- “Ficha”: detalhe operacional completo;
- “Lista”: consulta, busca, filtros e ações;
- “Dashboard”: indicadores e atalhos;
- “Central de Relatórios”: catálogo de visões e relatórios;
- “Estornar”: compensar lançamento preservando origem;
- “Cancelar”: encerrar documento e reverter efeitos definidos pela regra.
