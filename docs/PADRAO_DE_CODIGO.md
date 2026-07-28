# Padrão de Código do ERP Helvi

## Convenções

- classes: `PascalCase`;
- funções e variáveis: `snake_case`;
- constantes: letras maiúsculas;
- valores monetários: `Decimal`;
- identificador interno: `pk`;
- identificador comercial: `numero`.

## Ordem recomendada

1. arquitetura;
2. models;
3. migrations;
4. forms;
5. services;
6. views;
7. URLs;
8. templates;
9. CSS e JavaScript;
10. permissões;
11. homologação;
12. documentação;
13. commit.

## Consultas

Utilizar quando apropriado:

- `select_related`;
- `prefetch_related`;
- `annotate`;
- `aggregate`;
- `exists`;
- paginação;
- ordenação explícita.

## Componentização

Componentes estruturais podem ser criados desde o primeiro uso.

Componentes específicos de negócio devem ser extraídos quando houver
reutilização real.

## Verificação antes do commit

```powershell
python manage.py check
git status
```
