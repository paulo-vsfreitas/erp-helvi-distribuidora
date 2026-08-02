# PDF Framework - ERP Helvi

## Objetivo

O Framework PDF do ERP Helvi foi desenvolvido para centralizar toda a geração de documentos do sistema, garantindo:

- identidade visual única;
- reutilização de componentes;
- facilidade de manutenção;
- padronização entre todos os documentos.

Nenhum documento deve implementar diretamente estilos, cabeçalhos ou tabelas quando já existir um componente reutilizável.

---

# Estrutura

core/
└── pdf/
    ├── assets/
    ├── documents/
    ├── elements/
    ├── colors.py
    ├── document.py
    ├── footer.py
    ├── header.py
    ├── styles.py
    ├── tables.py
    └── utils.py

---

# Responsabilidade de cada arquivo

## document.py

Classe base `HelviPDF`.

Responsável por:

- criar o documento;
- controlar margens;
- configurar páginas;
- construir o PDF;
- aplicar cabeçalho;
- aplicar rodapé.

Nenhum documento deve criar diretamente um `SimpleDocTemplate`.

---

## header.py

Cabeçalho institucional.

Exibe:

- logo;
- dados da empresa;
- linha institucional.

É reutilizado em todos os documentos.

---

## footer.py

Rodapé institucional.

Responsável por:

- data de emissão;
- número da página;
- identificação do ERP.

---

## colors.py

Paleta oficial do ERP.

Todas as cores institucionais devem ser declaradas aqui.

Exemplo:

- HELVI_GOLD
- HELVI_BLACK
- HELVI_GRAY

Nunca utilizar códigos HEX espalhados pelo projeto.

---

## styles.py

Centraliza todos os ParagraphStyles.

Exemplo:

- TITLE
- SUBTITLE
- LABEL
- TEXT

---

## tables.py

Componentes reutilizáveis de tabelas.

Hoje contém:

- tabela de produtos.

Futuramente:

- contas a pagar;
- contas a receber;
- fluxo de caixa;
- relatórios.

---

# Elements

Os elementos representam pequenos blocos reutilizáveis.

## company.py

Dados institucionais.

## logo.py

Logo da empresa.

## purchase_info.py

Informações da compra.

## summary.py

Resumo financeiro.

## title.py

Título do documento.

---

# Documents

Cada documento monta sua estrutura utilizando os componentes.

Hoje:

- CompraPDF

Futuramente:

- OrcamentoPDF
- VendaPDF
- ReciboPDF
- EtiquetaPDF
- RelatorioPDF

Nenhum documento deve duplicar código existente no Framework.

---

# Como criar um novo documento

Criar:

core/pdf/documents/novo_documento.py

Estrutura básica:

1. Cabeçalho
2. Título
3. Informações
4. Tabelas
5. Resumos
6. Observações
7. Rodapé

Sempre reutilizar componentes existentes.

---

# Regras do Framework

- Não duplicar código.
- Componentes reutilizáveis ficam em `elements`.
- Tabelas reutilizáveis ficam em `tables.py`.
- Cores somente em `colors.py`.
- Estilos somente em `styles.py`.
- O documento apenas organiza os componentes.
- Melhorias estruturais devem beneficiar dois ou mais documentos.

---

# Status

Framework PDF

Versão: 1.0

Status: Homologado

Primeiro documento homologado:

✓ PDF da Compra