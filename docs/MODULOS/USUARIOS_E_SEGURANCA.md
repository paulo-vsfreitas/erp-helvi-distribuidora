# Usuários e Segurança

Atualizado em 05/08/2026.

## Autenticação

- autenticação padrão do Django com usuário próprio do ERP;
- login único com identidade Helvi ERP e seleção obrigatória da operação após
  a autenticação;
- operação ativa mantida na sessão, com troca sem novo login;
- troca obrigatória da senha no primeiro acesso;
- sessão expira após 30 minutos sem atividade e ao fechar o navegador;
- cinco falhas para a mesma combinação de usuário e IP geram bloqueio por
  15 minutos;
- login correto zera o contador daquela combinação;
- mensagens de falha não informam se o usuário existe, se a senha está errada
  ou se o bloqueio está ativo.
- páginas com token CSRF expirado são recuperadas por um fluxo amigável: sessão
  expirada abre um login novo e preserva o destino; páginas internas são
  recarregadas sem repetir a operação enviada.

Os limites são configuráveis por ambiente:

```text
SESSION_COOKIE_AGE=1800
LOGIN_MAX_TENTATIVAS=5
LOGIN_BLOQUEIO_SEGUNDOS=900
```

## Auditoria de login

Cada sucesso, falha e tentativa bloqueada registra:

- nome de usuário informado, normalizado;
- endereço IP da conexão;
- resultado;
- usuário autenticado, quando houver;
- navegador informado;
- data e horário.

Senha e conteúdo de credenciais nunca são persistidos. Os registros são de
somente leitura na administração do Django.

## Permissões

- módulos e ações sensíveis são validados no backend;
- ocultar um botão não substitui autorização;
- tentativas diretas a ações proibidas retornam HTTP 403;
- Vendedor consulta Estoque, Produtos e Catálogo sem modificá-los;
- cancelamento de venda exige credenciais de Administrador e registra quem
  solicitou e quem autorizou.
- a matriz de acesso combina perfil e operação ativa; ser Administrador não
  libera módulos pertencentes à outra empresa;
- a Use Helvi acessa somente seu painel, Eventos e o Financeiro isolado;
- Produtos, Catálogo, Estoque, Compras, Vendas, Relacionamento, Configurações e
  Relatórios gerais permanecem exclusivos da Helvi Distribuidora;
- o bloqueio ocorre no backend para acessos diretos por URL e a mesma matriz
  remove do menu os links incompatíveis com a operação.
- dentro do Financeiro compartilhado, Lucro e Margem comercial permanece
  exclusivo da Distribuidora; a Use Helvi usa seu relatório financeiro próprio.
- sessões legadas sem a chave de operação assumem Distribuidora, origem dos
  registros históricos; novos logins continuam exigindo seleção explícita.
