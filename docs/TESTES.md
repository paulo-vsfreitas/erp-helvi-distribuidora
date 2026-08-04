# Testes e Qualidade

Atualizado em 04/08/2026.

## Estado

A suíte completa possui **73 testes** e estava integralmente aprovada no
fechamento desta documentação.

Os testes cobrem principalmente:

- cálculo, filtro, edição, status, compartilhamento e conversão de orçamentos;
- finalização, pagamento, numeração e cancelamento de vendas;
- recebimento, numeração, integração e cancelamento de compras;
- regras negativas e operações destrutivas de produtos;
- permissões, usuários e primeiro acesso;
- fornecedores e listagens;
- central de relatórios e formatadores;
- estornos de baixas e recebimentos;
- auditoria e idempotência dos fluxos críticos.

## Comandos

Suíte completa:

```powershell
python manage.py test
```

Reutilizando o banco temporário:

```powershell
python manage.py test --keepdb
```

Módulo específico:

```powershell
python manage.py test comercial
python manage.py test vendas
python manage.py test compras
python manage.py test financeiro
```

Validações complementares:

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py auditar_integracoes --fail-on-error
git diff --check
```

## Critério para novos testes

Toda correção deve reproduzir primeiro o cenário e comprovar depois o resultado.
Toda nova operação crítica deve cobrir:

- caminho de sucesso;
- entrada inválida;
- permissão;
- repetição/idempotência;
- efeito em estoque e/ou financeiro;
- rollback quando uma etapa falha;
- método HTTP correto para ações destrutivas.

## Homologação visual

Para mudanças de template ou CSS, validar no mínimo:

- largura desktop comum;
- tela ampla ou zoom reduzido, garantindo conteúdo fluido;
- 768 px, sem rolagem horizontal global;
- cabeçalho, sidebar, cards, filtros, tabelas e estados vazios;
- console do navegador sem erros.

As 19 rotas do roteiro oficial estão em `MAPA_TELAS.md`.

## Antes de publicar

O deploy só pode continuar quando:

- testes estiverem verdes;
- nenhuma migration estiver ausente;
- auditoria retornar zero;
- `check --deploy` não apontar risco não aceito;
- os fluxos críticos forem homologados no ambiente candidato.
