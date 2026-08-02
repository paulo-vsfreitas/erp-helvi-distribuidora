# Decisões Permanentes do ERP Helvi

## Produto e metodologia

- Priorizar um sistema completo e utilizável antes de grandes refatorações.
- Concluir e homologar os fluxos principais antes de avançar de módulo.
- Iniciar novas conversas recuperando esta documentação e o estado mais recente.
- Solicitar somente arquivos específicos quando a implementação atual precisar ser confirmada.

## Interface

- A ficha é a tela central de Produto, Cliente, Fornecedor, Compra, Orçamento e Venda.
- Telas públicas não herdam a base interna autenticada.
- Resumos financeiros podem ser sticky quando isso melhora a conferência.
- Ações principais devem permanecer próximas do resumo no fluxo de formulários longos.
- Usar “Responsável” nas listagens para identificar quem realizou a operação, independentemente do perfil.
- Componentes visuais devem seguir a identidade Helvi: preto, dourado, branco e tons neutros.

## Produtos e itens

- O mesmo produto não pode aparecer duplicado em uma lista de itens.
- Ao tentar adicioná-lo novamente, informar que já está incluído e orientar a alteração da quantidade/desconto na linha existente.
- Autocompletes devem permitir busca por dados relevantes do domínio e, quando útil, exibir registros ativos ao focar o campo.

## Comercial

Fluxo oficial de orçamento:

```text
Cliente ou interessado
→ Novo orçamento
→ Produtos
→ Salvar
→ Visualizar
→ PDF
→ Enviar/compartilhar
→ Aprovar ou rejeitar
→ Converter em venda
```

- Orçamento pode ser criado para cliente cadastrado ou interessado avulso.
- Conversão em venda reutiliza cliente, produtos, quantidades, descontos, frete e totais.
- Conversão deve ser idempotente: não permitir conversão duplicada.
- “Enviar” como alteração de status deve ser identificado como “Marcar como enviado” ou equivalente quando existir envio real por canal.
- Orçamentos podem ser duplicados; a cópia nasce em rascunho, com nova numeração e responsável atual.

## Vendas

- Venda pode ocorrer sem cliente cadastrado, preservando dados básicos para comprovante.
- Finalização integra estoque e financeiro.
- Cancelamentos futuros devem estornar efeitos de forma segura e rastreável.

## Compras e estoque

- Receber compra atualiza estoque e custo, registra movimentação e impede duplicidade de entrada.
- Transferências de estoque dependem da implementação de locais de estoque.
- Compra recebida não deve ser editada de forma que comprometa o histórico.

## Framework

- O Framework Helvi já existe e deve ser consolidado, não recriado.
- Nenhum módulo deve reinventar recurso transversal já disponível.
- Abstrações devem nascer do uso real e da repetição comprovada.
- Formatação monetária, documentos, telefone, datas, badges, KPIs e mensagens devem convergir para fontes únicas.
