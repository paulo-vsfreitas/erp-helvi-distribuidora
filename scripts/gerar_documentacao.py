from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"


DOCUMENTOS = {
    "README.md": '''
    # ERP Helvi Distribuidora

    Documentação oficial do ERP Helvi.

    O sistema é desenvolvido em Django com arquitetura modular em camadas,
    integração entre os domínios e componentes reutilizáveis.

    ## Documentos principais

    - `ARQUITETURA.md`: arquitetura oficial;
    - `PADRAO_DE_CODIGO.md`: convenções de desenvolvimento;
    - `MODULOS.md`: situação atual dos módulos;
    - `ROADMAP.md`: planejamento da versão 1.0;
    - `CHANGELOG.md`: histórico de evolução;
    - `FRAMEWORK/`: padrões e componentes reutilizáveis;
    - `MODULOS/`: documentação detalhada por domínio;
    - `RELEASES/`: escopo e critérios das versões.

    ## Regras permanentes

    - preservar a arquitetura em camadas;
    - manter views finas;
    - concentrar regras operacionais em services;
    - utilizar forms para validação de entrada;
    - integrar estoque, financeiro e histórico;
    - utilizar fichas como telas centrais;
    - homologar cada fluxo antes de considerá-lo concluído;
    - atualizar a documentação junto com o código.
    ''',

    "ARQUITETURA.md": '''
    # Arquitetura Oficial do ERP Helvi

    ## Visão geral

    Cada aplicação Django representa um domínio de negócio.

    Exemplos:

    - usuários;
    - catálogo;
    - produtos;
    - clientes;
    - fornecedores;
    - estoque;
    - compras;
    - financeiro;
    - vendas;
    - core.

    O `core` contém recursos transversais e componentes compartilhados.
    Ele não deve concentrar regras específicas dos módulos de negócio.

    ## Estrutura recomendada

    ```text
    modulo/
    |-- admin.py
    |-- apps.py
    |-- models.py
    |-- urls.py
    |-- forms/
    |-- services/
    |-- utils/
    |-- views/
    |-- templates/
    |-- migrations/
    `-- tests/
    ```

    ## Models

    Representam entidades persistidas, relacionamentos, choices, constantes e
    propriedades simples.

    Fluxos que afetam vários módulos devem ficar em services.

    ## Forms

    Responsáveis por:

    - validação de entrada;
    - normalização;
    - mensagens de erro;
    - preparação dos dados.

    ## Views

    Devem:

    - receber a requisição;
    - validar autenticação e permissões;
    - instanciar forms;
    - chamar services;
    - montar o contexto;
    - renderizar ou redirecionar.

    Views não devem executar fluxos complexos de negócio.

    ## Services

    Concentram regras operacionais e integrações.

    Um service não deve:

    - receber `request`;
    - renderizar templates;
    - retornar `HttpResponse`;
    - depender de HTML.

    Operações compostas devem utilizar `transaction.atomic`.

    ## URLs

    Cada app possui seu próprio `urls.py` e namespace.

    Documentos comerciais utilizam `numero` nas URLs. A chave primária continua
    sendo usada internamente.

    ## Fichas

    A ficha é a tela central de documentos e cadastros relevantes.

    Pode apresentar:

    - identificação;
    - status;
    - ações;
    - resumo;
    - dados gerais;
    - itens;
    - financeiro;
    - histórico;
    - observações.

    ## Telas públicas

    Login, recuperação de senha e páginas de erro não devem herdar
    `core/base.html`.

    ## Conclusão de módulos

    Um módulo somente é considerado concluído após validar:

    - cadastro;
    - edição;
    - pesquisa;
    - validações;
    - permissões;
    - interface;
    - integrações;
    - cenários de erro;
    - homologação.
    ''',

    "PADRAO_DE_CODIGO.md": '''
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
    ''',

    "MODULOS.md": '''
    # Estado dos Módulos

    ## Funcionais

    - autenticação e usuários;
    - catálogo;
    - produtos;
    - clientes;
    - estoque;
    - compras;
    - contas a pagar;
    - contas a receber;
    - vendas.

    ## Em evolução

    - fornecedores;
    - relatórios;
    - dashboard;
    - framework de componentes.

    ## Planejados

    - pesquisa global;
    - auditoria;
    - relatórios financeiros avançados;
    - relatórios de estoque;
    - transferências entre locais;
    - homologação integrada da versão 1.0.
    ''',

    "ROADMAP.md": '''
    # Roadmap do ERP Helvi

    ## Concluído no fluxo principal

    - [x] autenticação;
    - [x] usuários e permissões;
    - [x] catálogo;
    - [x] produtos;
    - [x] clientes;
    - [x] estoque;
    - [x] compras;
    - [x] contas a pagar;
    - [x] contas a receber;
    - [x] vendas;
    - [x] integração Vendas com Estoque;
    - [x] integração Vendas com Financeiro;
    - [x] relatório inicial de vendas;
    - [x] componente reutilizável de KPIs.

    ## Fechamento da versão 1.0

    - [ ] relatório financeiro;
    - [ ] relatório de estoque;
    - [ ] pesquisa global;
    - [ ] auditoria;
    - [ ] revisão de permissões;
    - [ ] revisão visual;
    - [ ] revisão de performance;
    - [ ] homologação integrada;
    - [ ] estratégia de backup;
    - [ ] release ERP Helvi 1.0.
    ''',

    "CHANGELOG.md": '''
    # Changelog do ERP Helvi

    ## Julho de 2026

    ### Adicionado

    - fluxo principal de vendas;
    - baixa automática de estoque;
    - integração com contas a receber;
    - recebimentos financeiros;
    - ficha de venda;
    - relatório de vendas;
    - filtros comerciais;
    - indicadores de vendas;
    - componente reutilizável de KPIs;
    - URLs comerciais baseadas no número do documento.

    ### Arquitetura

    - modularização das views de vendas;
    - expansão da camada de services;
    - formalização do Framework Helvi;
    - atualização da documentação oficial.

    ## Junho de 2026

    - fundação do projeto;
    - autenticação;
    - catálogo;
    - produtos;
    - clientes;
    - estoque;
    - compras;
    - financeiro;
    - permissões;
    - identidade visual inicial.
    ''',

    "FRAMEWORK/README.md": '''
    # Framework Helvi

    O Framework Helvi reúne padrões internos, componentes visuais, helpers e
    contratos reutilizáveis.

    O framework pode padronizar apresentação e recursos transversais, mas não
    deve absorver regras específicas de Vendas, Compras, Estoque ou Financeiro.
    ''',

    "FRAMEWORK/COMPONENTES.md": '''
    # Componentes do Framework Helvi

    ## KPI Cards

    Arquivo atual:

    ```text
    core/templates/components/dashboard/kpi_cards.html
    ```

    Contrato:

    ```python
    {
        "titulo": "Faturamento",
        "valor": "R$ 15.800,00",
        "icone": "bi-cash-stack",
        "subtitulo": "Vendas finalizadas no período",
        "url": None,
    }
    ```

    O componente apresenta os dados, mas não realiza cálculos de negócio.
    ''',

    "FRAMEWORK/SERVICES.md": '''
    # Services do Framework Helvi

    Services de negócio permanecem dentro de seus módulos.

    ```text
    vendas/services/
    compras/services/
    estoque/services/
    financeiro/services/
    ```

    O `core` pode fornecer apenas recursos genéricos.

    Dependência permitida:

    ```text
    vendas -> core
    financeiro -> core
    estoque -> core
    ```

    Dependência que deve ser evitada:

    ```text
    core -> vendas
    core -> financeiro
    core -> estoque
    ```
    ''',

    "FRAMEWORK/NOMENCLATURA.md": '''
    # Nomenclatura do Framework Helvi

    - `pk`: identificador interno;
    - `numero`: identificador comercial;
    - `status`: situação operacional;
    - `status_pagamento`: situação financeira;
    - `subtotal`: soma antes dos ajustes gerais;
    - `desconto`: redução aplicada;
    - `frete`: acréscimo de entrega;
    - `total`: valor final;
    - `valor_pago`: valor pago em compras;
    - `valor_recebido`: valor recebido em vendas;
    - `saldo_pagar`: obrigação pendente;
    - `saldo_receber`: recebimento pendente.
    ''',

    "MODULOS/VENDAS.md": '''
    # Módulo Vendas

    Fluxo principal:

    ```text
    Venda
    -> Cliente
    -> Produtos
    -> Pagamento
    -> Finalização
    -> Baixa de estoque
    -> Conta a receber
    -> Recebimento
    -> Movimentação financeira
    -> Histórico
    ```

    Pendências:

    - homologação integral;
    - cancelamento com estorno;
    - comparação de períodos;
    - ranking de clientes;
    - ranking de vendedores;
    - exportações.
    ''',

    "MODULOS/COMPRAS.md": '''
    # Módulo Compras

    Fluxo principal:

    ```text
    Compra
    -> Itens
    -> Pagamentos
    -> Recebimento
    -> Entrada no estoque
    -> Atualização do custo
    -> Financeiro
    -> Histórico
    ```

    Pendências:

    - cancelar compra recebida;
    - editar itens;
    - concluir histórico de entrada;
    - revisar compra sem itens com pagamentos.
    ''',

    "MODULOS/ESTOQUE.md": '''
    # Módulo Estoque

    Responsável por movimentações, ajustes, inventários e integração com
    compras e vendas.

    Pendências:

    - locais de estoque;
    - transferências;
    - alertas de estoque mínimo;
    - relatório consolidado.
    ''',

    "MODULOS/FINANCEIRO.md": '''
    # Módulo Financeiro

    Responsável por contas a pagar, contas a receber, parcelas, contas
    financeiras, movimentações e históricos.

    Próximas evoluções:

    - relatório financeiro;
    - fluxo de caixa avançado;
    - indicadores;
    - projeções.
    ''',

    "ROADMAP/BACKLOG.md": '''
    # Backlog Oficial

    ## Fornecedores

    - edição;
    - ficha;
    - pesquisa;
    - homologação.

    ## Compras

    - cancelamento de compra recebida;
    - edição de itens;
    - histórico de entrada.

    ## Estoque

    - locais;
    - transferências;
    - alertas;
    - relatório.

    ## Vendas

    - homologação;
    - cancelamento com estorno;
    - rankings;
    - comparação entre períodos.

    ## Plataforma

    - pesquisa global;
    - auditoria;
    - revisão visual;
    - performance;
    - testes;
    - backup e restauração.
    ''',

    "RELEASES/ERP_HELVI_1.0.md": '''
    # ERP Helvi 1.0

    ## Critérios de lançamento

    - fluxos principais homologados;
    - integrações consistentes;
    - ausência de erros críticos;
    - permissões revisadas;
    - interface responsiva;
    - documentação atualizada;
    - banco validado;
    - estratégia de backup definida.

    ## Entregas restantes

    - relatório financeiro;
    - relatório de estoque;
    - pesquisa global;
    - auditoria;
    - polimento visual;
    - revisão de performance;
    - homologação integrada.
    ''',
}


def preparar(conteudo: str) -> str:
    return dedent(conteudo).strip() + "\n"


def salvar_documentos() -> None:
    DOCS.mkdir(parents=True, exist_ok=True)

    for caminho_relativo, conteudo in DOCUMENTOS.items():
        destino = DOCS / caminho_relativo
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(preparar(conteudo), encoding="utf-8")

        print(f"Atualizado: {destino.relative_to(ROOT)}")


def remover_diagnostico() -> None:
    diagnostico = DOCS / "_diagnostico_documentacao.txt"

    if diagnostico.exists():
        diagnostico.unlink()
        print("Removido: docs/_diagnostico_documentacao.txt")


def main() -> None:
    print("Atualizando documentação...\n")
    salvar_documentos()
    remover_diagnostico()
    print("\nDocumentação atualizada com sucesso.")


if __name__ == "__main__":
    main()