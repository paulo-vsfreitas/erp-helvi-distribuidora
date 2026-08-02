# ERP Helvi Development Guide

## 1. Objetivo principal

Entregar primeiro um ERP minimamente completo, confiável e utilizável na operação real da Helvi. Refinamentos arquiteturais extensos devem ocorrer de forma incremental, sem interromper a evolução funcional.

## 2. Ritual obrigatório antes de qualquer sprint

Antes de implementar:

1. ler esta documentação;
2. revisar arquitetura e decisões permanentes;
3. verificar o estado do módulo;
4. procurar recursos já existentes no Framework Helvi;
5. solicitar somente o arquivo específico necessário para confirmar a implementação;
6. evitar recriar código, componentes ou regras já consolidados.

## 3. Metodologia

- explicar alterações de forma didática;
- preservar arquitetura em camadas;
- implementar em etapas pequenas;
- homologar cada fluxo antes de considerá-lo concluído;
- não encerrar uma sprint com funcionalidade crítica pendente;
- registrar pendências reais no backlog;
- atualizar documentação e Git ao final de cada marco.

## 4. Ordem recomendada de implementação

1. blueprint e regras;
2. models e migrations;
3. forms e validações;
4. services;
5. views;
6. URLs;
7. templates;
8. CSS e JavaScript;
9. permissões;
10. integrações;
11. homologação;
12. documentação;
13. commit e tag quando aplicável.

## 5. Reuso

- recursos transversais ficam no `core`;
- regras específicas permanecem no módulo;
- componentes estruturais podem nascer no primeiro uso;
- componentes específicos devem ser extraídos quando houver reutilização real;
- antes de criar algo novo, pesquisar em todo o projeto.

## 6. Critério de conclusão

Um módulo só é concluído após validar:

- cadastro e edição;
- listagem, pesquisa e filtros;
- validações e mensagens;
- permissões;
- interface;
- integrações;
- duplicidade e idempotência;
- cenários de erro;
- homologação funcional.
