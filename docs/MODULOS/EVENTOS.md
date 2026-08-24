# Módulo Eventos — Use Helvi

Atualizado em 24/08/2026.

## Escopo

- cadastro e edição de eventos e stands;
- agenda mensal e lista de próximos eventos;
- responsável, contato, participantes internos e externos;
- cadastro reutilizável de pessoas e equipes, selecionáveis no evento;
- inclusão automática dos integrantes ao selecionar uma equipe;
- máscara e normalização de telefone/WhatsApp no navegador e no backend;
- tipo de contato do responsável/organizador e Instagram do organizador/local
  normalizado com `@`;
- local, período, público-alvo, organizador e observações;
- despesas rápidas integradas ao Contas a Pagar;
- vendas simplificadas enquanto o módulo completo da Use Helvi não existe;
- cadastro, edição, inativação e reativação de tipos de produto, com quantidade vendida;
- despesas gerais da Use Helvi sem vínculo obrigatório com evento;
- categorias de despesas criáveis, editáveis, inativáveis e reativáveis;
- painel financeiro com receitas recebidas e pendentes integradas ao caixa;
- centro financeiro único e compacto para receitas, despesas, categorias,
  contas financeiras, obrigações e relatórios;
- relatórios por evento, intervalo e mês, com PDF, WhatsApp e e-mail;
- resultado por evento com vendas, recebimentos, custo dos produtos, despesas,
  lucro e margem.
- cancelamento com motivo obrigatório, usuário, data e preservação do histórico.
- lembrete opcional por evento, com antecedência e mensagem configuráveis;
- pop-up de lembretes na Agenda com acesso direto à ficha e à edição;
- cor definida no cadastro de cada pessoa e reutilizada em todos os eventos;
- eventos com várias pessoas combinam suas cores na faixa visual do calendário.
- pessoas da equipe guardam somente nome, contato e cor; Instagram pertence às
  informações do organizador/local do evento.

## Fluxo

```text
Use Helvi
→ Agenda
→ Evento
→ equipe e informações
→ despesas e vendas
→ lucro e margem
```

Uma despesa marcada como paga cria a Conta a Pagar, sua parcela, a baixa e a
movimentação de caixa na mesma transação. Uma despesa a pagar cria a obrigação
pendente e exige vencimento.

Despesas como expositores, equipamentos, materiais e marketing podem ser
registradas em **Despesas gerais**. Quando o gasto pertence a um stand, ele é
lançado na ficha do evento e compõe seu lucro; despesas gerais não alteram o
resultado de nenhum evento.

O lucro do evento é calculado por:

```text
vendas − custo dos produtos vendidos − despesas do evento
```

O valor recebido não substitui o valor vendido: ambos permanecem separados
para apresentar vendas a receber e o resultado econômico correto.

Receitas marcadas como recebidas criam Conta a Receber, recebimento e movimento
de entrada na mesma transação. Receitas futuras permanecem pendentes. O PDF usa
o gerador oficial do ERP; no WhatsApp o link é preparado para envio e no e-mail
o PDF segue anexado pelo backend configurado.

## Permissões e isolamento

- acesso inicial para Administrador e Gerente;
- rotas disponíveis somente com a operação Use Helvi ativa;
- cancelamento altera estado somente por POST e bloqueia novas vendas/despesas;
- despesas continuam auditáveis na ficha original do Financeiro;
- contas, obrigações e movimentos carregam a operação `use-helvi`, impedindo
  mistura com os dados da Helvi Distribuidora;
- participantes internos são usuários ativos do ERP; nomes externos podem ser
  informados sem criar acesso ao sistema.
- pessoas da equipe não precisam receber usuário ou acesso ao ERP;
- exclusão de pessoa, equipe ou categoria é lógica, preservando vínculos e
  histórico; itens inativos deixam de aparecer em novas seleções.
- nome de evento repetido no mesmo dia é bloqueado;
- responsável, participante ou pessoa cadastrada não pode estar em outro
  evento no mesmo dia; a equipe selecionada é expandida antes da validação;
- eventos cancelados deixam de ocupar a disponibilidade da agenda.
- eventos cancelados permanecem no calendário para auditoria, mas aparecem
  riscados e em vermelho;
- lembretes de eventos cancelados ou concluídos não são exibidos.

## Evoluções posteriores

- edição, cancelamento e estorno específicos de vendas simplificadas;
- anexos e comprovantes;
- checklist e notificações;
- integração automática com o futuro módulo de Vendas da Use Helvi;
- comparação entre orçamento previsto e resultado realizado.
