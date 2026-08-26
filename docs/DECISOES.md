# Decisões Permanentes do ERP Helvi

## Produto

- A versão 1.0 cobre a operação essencial de ponta a ponta.
- Evoluções avançadas não devem comprometer fluxos já homologados.
- Código, testes e documentação fazem parte da mesma entrega.
- O status documentado deve refletir o código executável, não apenas intenção.

## Metodologia

- Verificar primeiro se a funcionalidade já existe.
- Preservar alterações locais que não pertençam à tarefa.
- Preferir mudanças pequenas, reversíveis e testadas.
- Regras críticas ficam em services transacionais.
- Funcionalidade só é concluída após validação técnica e visual proporcional.

## Interface

- Helvi UI é o padrão de todas as páginas internas.
- Preto, dourado, branco e tons neutros formam a identidade visual.
- Cabeçalhos de página ficam dentro do card/padrão oficial do framework.
- O layout é fluido; reduzir zoom deve aumentar a área útil, não criar uma ilha
  estreita centralizada.
- A ficha é a tela central de Produto, Cliente, Fornecedor, Compra, Orçamento,
  Venda e contas financeiras.
- Telas públicas não herdam a base interna autenticada.
- “Responsável” identifica quem realizou a operação na apresentação.

## Produtos e itens

- O mesmo produto não aparece duplicado na lista de itens.
- Nova tentativa orienta a alterar quantidade ou desconto na linha existente.
- Autocompletes pesquisam campos relevantes e retornam registros ativos.
- Estoque, custo e preço não podem ficar negativos.

## Comercial

```text
Cliente ou interessado
→ orçamento
→ itens
→ ficha/PDF
→ compartilhamento/status
→ aprovação ou rejeição
→ conversão em venda
```

- orçamento aceita cliente cadastrado ou interessado avulso;
- edição preserva o documento e respeita os estados permitidos;
- cópia nasce em rascunho, com novo número e responsável atual;
- conversão é única e preserva dados, itens, frete, descontos e total;
- “Valor orçado” representa carteira ativa: rascunho, enviado e aprovado;
- rejeitado, cancelado e convertido não entram no valor orçado;
- compartilhamentos registram canal, destinatário, resultado e usuário;
- WhatsApp registra preparação; e-mail registra o resultado do backend.

## Vendas

- venda pode ocorrer sem cliente cadastrado;
- venda originada de orçamento preserva o vínculo;
- finalização baixa estoque e gera financeiro atomicamente;
- finalização não pode ocorrer duas vezes;
- pagamento à vista e a prazo atualiza status e valores coerentemente;
- cancelamento exige motivo, devolve estoque e reverte/cancela o financeiro;
- venda cancelada permanece disponível para auditoria.

## Compras e estoque

- recebimento atualiza estoque, custo e financeiro;
- entrada de uma compra ocorre uma única vez;
- compra recebida não pode ser editada de forma a corromper histórico;
- cancelamento valida estoque disponível para o estorno;
- rastreabilidade usa movimentações e origem;
- múltiplos locais e transferências são evolução posterior à versão 1.0.

## Financeiro

- todo registro financeiro identifica persistentemente sua operação;
- a troca de operação nunca mistura contas, obrigações ou fluxo de caixa;
- despesas gerais da Use Helvi usam o motor transacional do Financeiro, com
  evento opcional;
- baixa e recebimento criam movimentos explícitos;
- estorno nunca apaga a operação original;
- estorno exige motivo, usuário e data;
- o movimento inverso e o recálculo da parcela/conta são atômicos;
- uma operação não pode ser estornada duas vezes;
- ajustes manuais não substituem services operacionais existentes.
- categorias com histórico financeiro são inativadas, nunca apagadas fisicamente.

## Eventos — Use Helvi

- pessoas de stands possuem cadastro próprio e não exigem acesso ao ERP;
- equipes agrupam pessoas reutilizáveis e preenchem os integrantes do evento;
- telefone e WhatsApp são normalizados também no backend;
- o Financeiro da Use Helvi reutiliza Contas a Pagar, Contas a Receber e caixa;
- relatórios distinguem vendas, recebimentos, custos, despesas e resultado.
- o mesmo dia não aceita duplicidade de evento nem dupla alocação de pessoas;
- a tela Financeiro concentra os lançamentos e acessos financeiros da Use Helvi.
- a cor da agenda pertence ao cadastro da pessoa e vem de uma paleta RGB fixa,
  formada por cores visualmente distantes para facilitar a identificação;
- eventos com mais de uma pessoa usam a cor da primeira pessoa em ordem
  alfabética, sem gradientes;
- a identidade visual da operação Use Helvi é o rose gold cobre da logo,
  grafite e off-white, sem roxo ou misturas em gradiente;
- lembretes aparecem na Agenda conforme a antecedência definida no evento.
- cancelamento não remove o evento da Agenda: preserva o histórico com estilo
  riscado e cor neutra de alerta, sem confundir com eventos ativos.

## Usuários e permissões

- perfis oficiais: ADM, GER, VEN e FIN;
- permissões por módulo vêm de uma matriz central;
- ações sensíveis possuem autorização granular no backend, além da visibilidade
  dos botões na interface;
- Vendedor consulta Estoque, Produtos e Catálogo, sem alterar seus registros;
- cancelamento de venda pode ser solicitado por qualquer perfil, mas exige
  credenciais válidas de Administrador e registra solicitante e autorizador;
- novos usuários cadastrados no ERP devem trocar a senha no primeiro acesso;
- inativação é preferível à exclusão de usuário com histórico.
- autenticação limita tentativas repetidas sem revelar se uma conta existe;
- auditoria de login nunca armazena senhas e seus eventos são somente leitura.

## Framework

- Framework Helvi e Helvi UI já existem e devem ser ampliados, não recriados.
- Componentes transversais ficam no `core` ou `static/helvi_ui`.
- Abstrações nascem de repetição real e contrato estável.
- formatação monetária oficial fica em `core/formatters.py` e no filtro `moeda`.
- não criar novos formatadores locais.
