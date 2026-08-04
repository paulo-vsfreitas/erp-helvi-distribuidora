# Módulo Comercial — Orçamentos

Atualizado em 04/08/2026.

## Fluxo

```text
Cliente cadastrado ou interessado avulso
→ novo orçamento
→ produtos e condições
→ salvar/editar
→ ficha e PDF
→ compartilhar ou mudar status
→ aprovar/rejeitar
→ converter em venda
```

## Implementado

- dashboard Comercial;
- cards globais de Orçamentos, Rascunhos, Aprovados e Valor orçado;
- cards clicáveis com filtro da tabela;
- busca e filtros por dados do documento;
- cliente cadastrado ou interessado avulso;
- autocomplete de clientes e produtos;
- prevenção de produto duplicado;
- cálculo e resumo financeiro;
- criação e edição;
- ficha e PDF;
- duplicação;
- status rascunho, enviado, aprovado, rejeitado, cancelado e convertido;
- histórico de compartilhamentos;
- e-mail com PDF anexado;
- URL preparada para WhatsApp;
- conversão idempotente em venda;
- formatação monetária brasileira;
- testes de regra, filtros, comunicação e conversão.

## Valor orçado

Representa a carteira ativa:

```text
rascunho + enviado + aprovado
```

Rejeitados, cancelados e convertidos não são somados. Os totais dos cards são
globais mesmo quando a tabela está filtrada.

## Status e edição

- cópia sempre nasce em rascunho;
- conversão só ocorre uma vez;
- o orçamento convertido preserva vínculo com a venda;
- filtros inválidos retornam com segurança para a listagem geral;
- mudanças de status devem respeitar as transições do service;
- documento histórico não deve ser apagado para “desfazer” uma operação.

## Compartilhamento

E-mail:

- usa o backend Django configurado;
- anexa o PDF;
- registra enviado ou falha;
- pode marcar o orçamento como enviado.

WhatsApp:

- prepara o link e a mensagem;
- registra resultado “preparado”;
- a confirmação final depende do usuário no aplicativo externo.

## Arquivos principais

- models: `comercial/models.py`;
- regras: `comercial/services/`;
- forms: `comercial/forms/`;
- views: `comercial/views/`;
- templates: `comercial/templates/comercial/`;
- scripts: `static/js/comercial/`;
- testes: `comercial/tests.py`.

## Evoluções não bloqueantes

- templates de mensagem configuráveis;
- validade padrão por configuração;
- provedor oficial de WhatsApp;
- lembretes e automações de acompanhamento;
- funil comercial analítico.
