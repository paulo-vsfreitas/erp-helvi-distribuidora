# Backlog Oficial do ERP Helvi

Atualizado em 04/08/2026. Itens abaixo são evoluções ou atividades de produção;
não representam falhas conhecidas nos fluxos 1.0 já homologados.

## Antes da publicação 1.0

- backup completo de PostgreSQL e mídia;
- teste documentado de restauração;
- ambiente de homologação com configuração de produção;
- SMTP real e teste de entrega com PDF;
- domínio, certificado HTTPS e proxy;
- armazenamento e política de retenção de mídia;
- aceite dos perfis ADM, GER, VEN e FIN;
- tag e notas finais da versão.

## Relatórios e gestão

- relatórios analíticos dedicados de clientes e produtos;
- demonstrativo financeiro por período e categoria;
- posição e giro de estoque com exportação;
- desempenho de fornecedores e evolução de custos;
- CSV/PDF e comparação entre períodos;
- filtros salvos.

## Estoque e logística

- locais de estoque;
- transferências entre locais;
- endereçamento físico;
- alertas configuráveis de mínimo;
- contagem por coletor ou importação.

## Comercial e relacionamento

- comprovantes e checklist dos eventos da Use Helvi;
- integração das vendas simplificadas dos eventos ao futuro fluxo completo de
  vendas, produtos e estoque da Use Helvi;

- integração oficial com provedor de WhatsApp, se contratada;
- confirmação automática de entrega/leitura quando o provedor permitir;
- validade padrão configurável por empresa;
- lembretes de orçamento próximo do vencimento.

## Plataforma

- pesquisa global;
- paginação padronizada para grandes volumes;
- tarefas assíncronas;
- cache e revisão de consultas em alta escala;
- monitoramento de erros e métricas;
- trilha de auditoria administrativa ampliada;
- API autenticada para integrações futuras.

## Qualidade contínua

- consolidar aliases históricos de componentes após mapear todos os includes;
- migrar formatadores monetários locais restantes para `core.formatters`;
- ampliar testes de fornecedores, estoque e configurações;
- testes de concorrência em numeração comercial;
- testes end-to-end dos quatro perfis;
- teste automatizado de restauração de backup;
- revisão periódica de dependências e segurança.
