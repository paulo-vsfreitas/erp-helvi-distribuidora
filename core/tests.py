from django.template.loader import get_template
from django.test import SimpleTestCase
from django.urls import reverse

from core.services.central_relatorios_service import montar_central_relatorios


class HelviUITemplateTests(SimpleTestCase):
    templates_migrados = (
        "helvi_ui/page_header.html",
        "helvi_ui/section_card.html",
        "helvi_ui/empty_state.html",
        "helvi_ui/action_bar.html",
        "components/layout/page_header.html",
        "components/ui/page_header.html",
        "components/states/confirmation_page.html",
        "comercial/dashboard.html",
        "comercial/novo_orcamento.html",
        "comercial/ficha_orcamento.html",
        "comercial/orcamentos/vincular_cliente.html",
        "clientes/lista_clientes.html",
        "clientes/form_cliente.html",
        "produtos/lista_produtos.html",
        "produtos/form_produto.html",
        "produtos/ficha_produto.html",
        "produtos/galeria_produto.html",
        "catalogo/marcas/lista_marcas.html",
        "catalogo/marcas/form_marca.html",
        "catalogo/marcas/confirmar_inativacao_marca.html",
        "catalogo/marcas/confirmar_reativacao_marca.html",
        "catalogo/colecoes/lista_colecoes.html",
        "catalogo/colecoes/form_colecao.html",
        "catalogo/colecoes/confirmar_inativacao_colecao.html",
        "catalogo/colecoes/confirmar_reativacao_colecao.html",
        "catalogo/generos/lista_generos.html",
        "catalogo/generos/form_genero.html",
        "catalogo/generos/confirmar_inativacao_genero.html",
        "catalogo/generos/confirmar_reativacao_genero.html",
        "catalogo/lista_tipo_armacao.html",
        "catalogo/form_tipo_armacao.html",
        "estoque/dashboard.html",
        "estoque/lista_movimentacoes.html",
        "estoque/nova_entrada.html",
        "estoque/nova_saida.html",
        "estoque/ajuste_estoque.html",
        "estoque/inventarios/lista.html",
        "estoque/inventarios/novo.html",
        "estoque/inventarios/conferir.html",
        "financeiro/dashboard.html",
        "financeiro/lista_movimentacoes.html",
        "financeiro/lista_contas_financeiras.html",
        "financeiro/form_conta_financeira.html",
        "financeiro/ficha_conta_financeira.html",
        "financeiro/lista_contas_pagar.html",
        "financeiro/form_conta_pagar.html",
        "financeiro/ficha_conta_pagar.html",
        "financeiro/registrar_baixa.html",
        "financeiro/lista_contas_receber.html",
        "financeiro/form_conta_receber.html",
        "financeiro/ficha_conta_receber.html",
        "financeiro/registrar_recebimento.html",
        "financeiro/lista_categorias.html",
        "financeiro/form_categoria.html",
        "core/relatorios.html",
        "core/dashboard.html",
        "core/login.html",
        "registration/password_reset_form.html",
        "registration/password_reset_done.html",
        "registration/password_reset_confirm.html",
        "registration/password_reset_complete.html",
        "usuarios/lista_usuarios.html",
        "usuarios/form_usuario.html",
        "compras/lista_compras.html",
        "compras/nova_compra.html",
        "compras/editar_compra.html",
        "compras/ficha_compra.html",
        "fornecedores/dashboard.html",
        "fornecedores/lista_fornecedores.html",
        "fornecedores/form_fornecedor.html",
        "fornecedores/ficha_fornecedor.html",
        "vendas/lista.html",
        "vendas/nova.html",
        "vendas/ficha.html",
        "vendas/relatorios/vendas.html",
        "configuracoes/dados_empresa.html",
    )

    def test_templates_migrados_compilam(self):
        for template_name in self.templates_migrados:
            with self.subTest(template=template_name):
                get_template(template_name)

    def test_base_carrega_helvi_ui_depois_dos_estilos_de_modulo(self):
        template = get_template("core/base.html")
        source = template.template.source

        self.assertLess(
            source.index("{% block extra_css %}"),
            source.index("helvi_ui/helvi-ui.css"),
        )
        self.assertIn('class="page helvi-ui"', source)

    def test_framework_helvi_contem_estruturas_compartilhadas(self):
        template = get_template("core/base.html")
        source = template.template.source

        self.assertIn("helvi_ui/helvi-ui.css", source)
        self.assertIn("?v=1.9.0", source)

    def test_telas_principais_usam_card_de_cabecalho(self):
        templates = (
            "vendas/nova.html",
            "comercial/novo_orcamento.html",
            "clientes/lista_clientes.html",
            "estoque/dashboard.html",
            "financeiro/lista_movimentacoes.html",
            "core/dashboard.html",
        )

        for template_name in templates:
            with self.subTest(template=template_name):
                source = get_template(template_name).template.source
                self.assertIn("hui-page-header", source)


class CentralRelatoriosTests(SimpleTestCase):
    def test_todos_os_cards_possuem_destino_funcional(self):
        contexto = montar_central_relatorios()
        relatorios = [
            relatorio
            for secao in contexto["secoes"]
            for relatorio in secao["relatorios"]
        ]

        self.assertEqual(len(relatorios), 13)
        self.assertTrue(all(item["disponivel"] for item in relatorios))
        self.assertTrue(all(item["url"] for item in relatorios))
        self.assertEqual(contexto["indicadores"]["total_disponiveis"], 13)
        self.assertEqual(contexto["indicadores"]["total_desenvolvimento"], 0)

    def test_destinos_principais_sao_os_paineis_existentes(self):
        contexto = montar_central_relatorios()
        destinos = {
            relatorio["titulo"]: relatorio["url"]
            for secao in contexto["secoes"]
            for relatorio in secao["relatorios"]
        }

        self.assertEqual(destinos["Relatório de Clientes"], reverse("lista_clientes"))
        self.assertEqual(destinos["Fluxo de Caixa"], reverse("financeiro:lista_movimentacoes"))
        self.assertEqual(destinos["Movimentações de Estoque"], reverse("estoque:lista_movimentacoes"))
