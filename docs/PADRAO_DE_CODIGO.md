# Padrão de Desenvolvimento - ERP Helvi Distribuidora

## Objetivo

Este documento define os padrões oficiais de arquitetura, organização e desenvolvimento do ERP Helvi Distribuidora.

Todo novo módulo deverá seguir estas regras.

---

# Estrutura do projeto

```
catalogo/
│
├── models/
├── forms/
├── views/
├── services/
├── utils/
├── templates/
├── migrations/
└── urls.py
```

---

# Models

- Um arquivo por model.
- Nome do arquivo sempre no singular.

Exemplo:

```
marca.py
colecao.py
genero.py
material.py
```

---

# Forms

- Um arquivo por módulo.
- Nome do arquivo sempre no plural.

Exemplo:

```
marcas.py
colecoes.py
generos.py
```

Cada arquivo poderá conter um ou mais Forms relacionados ao módulo.

---

# Views

- Um arquivo por módulo.
- Nome do arquivo sempre no plural.

Exemplo:

```
marcas.py
colecoes.py
generos.py
```

---

# Templates

Sempre utilizar uma pasta por módulo.

Exemplo:

```
templates/catalogo/

marcas/
colecoes/
generos/
```

---

# CRUD

Todo cadastro simples deverá possuir:

- Lista
- Novo
- Editar
- Inativar
- Reativar

---

# Models simples

Todo cadastro simples deverá possuir, sempre que aplicável:

- nome
- descricao
- ativo
- data_cadastro
- data_atualizacao

---

# URLs

Padrão:

lista_xxx

novo_xxx

editar_xxx

inativar_xxx

reativar_xxx

---

# Ordem de desenvolvimento

Sempre seguir:

1. Model
2. Migration
3. Form
4. View
5. URL
6. Template
7. Menu
8. Permissões
9. Testes
10. Git Commit

Nunca alterar esta ordem.

---

# Convenções

Classes:

PascalCase

Funções:

snake_case

Arquivos de model:

singular

Arquivos de form:

plural

Arquivos de view:

plural

Pastas de templates:

plural

---

# Objetivo

O sistema deve priorizar:

- simplicidade
- organização
- escalabilidade
- padronização
- reutilização de código

Toda implementação deve seguir estes princípios.