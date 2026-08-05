# Cadastros Base

Atualizado em 04/08/2026.

## Usuários

Aplicação: `usuarios`.

Implementado:

- autenticação Django;
- perfis ADM, GER, VEN e FIN;
- matriz central de permissões por módulo;
- middleware de proteção das rotas;
- listagem, cadastro e edição;
- foto, telefone, contato, status e perfil;
- inativação por POST;
- primeiro acesso com definição obrigatória de senha;
- telas públicas independentes para login e recuperação.

Regras:

- novo usuário criado no ERP recebe `primeiro_acesso=True`;
- usuário autenticado nessa condição é direcionado para a troca de senha;
- perfis não devem ser comparados por texto de apresentação;
- usuários com histórico devem ser inativados, não excluídos.

## Catálogo

Aplicação: `catalogo`.

- marcas;
- coleções;
- gêneros;
- tipos de armação;
- listagem, pesquisa, cadastro e edição;
- inativação e reativação com confirmação por POST;
- telas padronizadas pelo Helvi UI.

Esses registros alimentam o cadastro e os filtros de produtos.

## Produtos

- opção explícita **Produto sem variação de cor** no cadastro e na edição;
- produtos sem cor utilizam o estoque geral e aparecem como “Sem variação” nas operações;
- produtos com cores existentes exigem a remoção individual das variações antes
  de voltar ao controle sem cor, evitando perda acidental de estoque.

Aplicação: `produtos`.

- código ERP e código de fornecedor;
- modelo, marca, coleção, gênero e tipo de armação;
- custo, preço de venda, estoque atual e mínimo;
- ficha, listagem, filtros e pesquisa;
- galeria e imagens;
- ativação/inativação;
- constraints contra valores negativos;
- integração com compras, vendas, estoque e relatórios.
- código, modelo, marca e coleção opcionais no cadastro e na edição;
- nome/descrição opcional nas variações de cor.

Alterações de saldo devem passar pelos services de estoque. Não ajuste
`estoque_atual` diretamente em views ou templates.

## Clientes / Óticas

Aplicação: `clientes`.

- cadastro e edição;
- pessoa física e jurídica conforme os campos atuais;
- validações e máscaras;
- pesquisa e filtros;
- integração com orçamento, venda e Contas a Receber;
- suporte a venda/orçamento avulso sem obrigar o cadastro.
- endereço estruturado com CEP, logradouro, número, complemento, bairro,
  cidade e UF, usando o autocomplete de CEP compartilhado do ERP.

## Configurações

Aplicação: `configuracoes`.

- dados institucionais da empresa;
- tela interna padronizada;
- fonte para identificação do ERP e documentos quando utilizada.

Configurações técnicas, segredos e credenciais permanecem no ambiente, nunca
neste cadastro nem no Git.

## Manutenção

Ao alterar cadastros:

- revisar dependências com `on_delete=PROTECT`;
- preservar registros históricos;
- manter ações destrutivas em POST;
- testar pesquisa, filtros, permissões e estados ativo/inativo;
- homologar produtos em Compras, Estoque, Comercial e Vendas.
