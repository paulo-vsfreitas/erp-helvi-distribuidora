# Mapa de Telas e Permissões

## Perfis

| Perfil | Código | Acesso principal |
|---|---|---|
| Administrador | ADM | todos os módulos |
| Gerente | GER | operação, cadastros, financeiro, relatórios e compras |
| Vendedor | VEN | dashboard, vendas/orçamentos, clientes, produtos, catálogo e estoque |
| Financeiro | FIN | dashboard, clientes, financeiro e relatórios |

A matriz oficial está em `usuarios/permissoes.py` e é aplicada globalmente pelo
`PermissaoModuloMiddleware`.

## Rotas principais homologadas

| Tela | Rota |
|---|---|
| Dashboard | `/` |
| Nova venda | `/vendas/nova/` |
| Vendas | `/vendas/` |
| Orçamentos | `/comercial/` |
| Novo orçamento | `/comercial/novo/` |
| Clientes / Óticas | `/clientes/` |
| Fornecedores | `/fornecedores/` |
| Produtos | `/produtos/` |
| Marcas | `/catalogo/marcas/` |
| Coleções | `/catalogo/colecoes/` |
| Gêneros | `/catalogo/generos/` |
| Tipos de armação | `/catalogo/tipos-armacao/` |
| Estoque | `/estoque/` |
| Financeiro | `/financeiro/` |
| Fluxo de caixa | `/financeiro/movimentacoes/` |
| Relatórios | `/relatorios/` |
| Configurações | `/configuracoes/` |
| Usuários | `/usuarios/` |
| Compras | `/compras/lista/` |

Todas foram validadas com:

- `.hui-module-page` presente;
- cabeçalho Helvi UI;
- sidebar autenticada;
- ausência de erro de servidor;
- ausência de rolagem horizontal global nos breakpoints avaliados.

## Telas públicas

- login: `/senha/login/`;
- recuperação e redefinição de senha: `/senha/...`;
- primeiro acesso: `/usuarios/primeiro-acesso/` após autenticação.

Telas públicas não devem herdar o layout autenticado.

## Rotas críticas de ação

- conversão, status e compartilhamento de orçamento;
- finalização e cancelamento de venda;
- recebimento e cancelamento de compra;
- inativação/reativação de cadastros;
- baixa, recebimento e estorno financeiro.

Operações destrutivas ou irreversíveis devem alterar estado somente via `POST`.
