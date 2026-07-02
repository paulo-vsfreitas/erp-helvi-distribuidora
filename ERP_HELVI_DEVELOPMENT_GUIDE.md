# ERP Helvi Development Guide

## 1. Regra principal

Antes de iniciar qualquer nova sprint, este documento deve ser consultado.

Nenhuma sprint nova deve começar sem validar:

- arquitetura do módulo;
- padrão de pastas;
- padrão de views, services, forms e utils;
- padrão visual;
- componentes reutilizáveis;
- ficha central;
- dashboard;
- permissões;
- validações;
- integração com módulos existentes.

---

## 2. Arquitetura padrão dos módulos

Todo novo módulo deve nascer com:

```text
modulo/
├── admin.py
├── apps.py
├── models.py
├── urls.py
├── forms/
├── services/
├── utils/
├── views/
├── templates/
├── static/
└── migrations/