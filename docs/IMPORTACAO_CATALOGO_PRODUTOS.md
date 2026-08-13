# Importação de Catálogo de Produtos

## Fluxo

1. Informar fornecedor, tipo de armação, preços e estoque padrão.
2. Enviar um ou vários arquivos PDF/JPG/JPEG/PNG.
3. O ERP cria um lote de staging e analisa os arquivos.
4. A prévia permite editar código do fornecedor, modelo, preços, estoque, variações e itens selecionados.
5. Duplicidade exata é verificada por `fornecedor + codigo_fornecedor`.
6. Somente a confirmação definitiva cria `Produto`, `VariacaoCor`, `ImagemProduto` e movimentações de estoque.

## Leitura automática

A implementação atual usa ferramentas locais quando disponíveis:

- `tesseract` para OCR de imagens;
- `pdftotext` para texto nativo de PDF;
- `pdftoppm` para gerar preview da primeira página e permitir OCR de PDF digitalizado.

Na homologação Render, essas ferramentas são instaladas pelo `Dockerfile`. O
build deve falhar se Tesseract (incluindo o idioma `por`) ou Poppler não estiver
disponível, evitando publicar o OCR parcialmente funcional.

Se alguma ferramenta não estiver instalada, o lote continua disponível e a conferência manual permanece funcional. A saída da leitura é sempre tratada como sugestão.

## Regras preservadas

- Excel/CSV continua funcionando pelo fluxo existente.
- Catálogo reutiliza `produtos.services.importacao.importar_produtos`.
- Estoque inicial passa por `registrar_entrada_estoque` / domínio oficial de estoque.
- O catálogo não cria Marca, Coleção, Gênero ou Tipo de Armação a partir de OCR.
- O mesmo código de fornecedor pode existir em fornecedores diferentes.
- Imagens ficam ligadas ao produto; não há vínculo foto ↔ variação nesta primeira versão.

## Infraestrutura

Os arquivos usam o `default_storage` configurado pelo Django. Para produção, o storage precisa ser persistente. O analisador não depende de `storage.path()`: ele materializa os arquivos temporariamente para as ferramentas locais, permitindo evolução posterior para storage externo.

## Homologação obrigatória

Executar no ambiente real:

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate
python manage.py test produtos estoque comercial vendas usuarios --keepdb
python manage.py auditar_integracoes
```

Depois validar visualmente:

- Produtos > Importar Catálogo;
- upload múltiplo;
- PDF e imagens;
- edição da prévia;
- adicionar/remover variações na prévia;
- alerta de duplicidade;
- confirmação;
- ficha do produto com fornecedor e imagens;
- estoque total por variação;
- histórico de movimentações.
