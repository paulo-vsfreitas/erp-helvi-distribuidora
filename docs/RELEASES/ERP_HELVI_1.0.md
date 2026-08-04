# ERP Helvi 1.0

Status em 04/08/2026: **release candidate**.

## Objetivo

Primeira versão utilizável de ponta a ponta na operação da Helvi, com
rastreabilidade de documentos, estoque e financeiro.

## Escopo entregue

- autenticação, usuários, perfis e primeiro acesso;
- catálogo, produtos, clientes e fornecedores;
- estoque, ajustes e inventários;
- compras, recebimento, cancelamento e PDF;
- contas financeiras, contas a pagar/receber, baixas, recebimentos e estornos;
- orçamentos, PDF, compartilhamento, status, edição e conversão;
- vendas, pagamentos, cancelamento e integrações;
- dashboard, fluxo de caixa, relatório de vendas e Central de Relatórios;
- Helvi UI responsivo;
- auditoria, conciliação, segurança de implantação e documentação.

## Evidências técnicas

| Critério | Resultado |
|---|---|
| Testes automatizados | 61 aprovados |
| System check | sem problemas |
| Migrations | nenhuma pendente |
| Auditoria de integrações | zero divergências |
| Compras a conciliar | zero |
| Telas principais homologadas | 19 |
| Relatórios/cards ativos | 13 |
| Erros de console na homologação | zero |

## Critérios de aceite de publicação

- [x] fluxos principais implementados;
- [x] integrações consistentes e idempotentes;
- [x] cancelamentos e estornos críticos;
- [x] permissões centralizadas;
- [x] interface responsiva e padronizada;
- [x] testes e auditoria aprovados;
- [x] documentação atualizada;
- [x] estratégia de configuração de produção documentada;
- [ ] backup e restauração testados no ambiente definitivo;
- [ ] SMTP, HTTPS, estáticos e mídia homologados;
- [ ] aceite final dos usuários responsáveis;
- [ ] tag 1.0 criada após a publicação aprovada.

## Limites do escopo 1.0

Não fazem parte do bloqueio desta versão:

- múltiplos depósitos e transferências;
- API pública;
- aplicativo móvel;
- relatórios analíticos avançados e exportações completas;
- integração contratada com provedor oficial de WhatsApp;
- filas assíncronas e observabilidade externa.

Esses itens permanecem no backlog pós-1.0.
