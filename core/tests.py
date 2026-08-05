from django.contrib.auth import get_user_model
from django.template.loader import get_template
from django.test import Client, SimpleTestCase, TestCase
from django.urls import reverse

from core.services.central_relatorios_service import montar_central_relatorios
from produtos.models import Produto


class HelviUITemplateTests(SimpleTestCase):
    templates_migrados = (
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
        "core/relatorio_analitico.html",
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

    def test_sidebar_organiza_modulos_por_dominio_e_marca_pagina_ativa(self):
        source = get_template("core/base.html").template.source

        secoes = (
            "PRINCIPAL",
            "COMERCIAL",
            "RELACIONAMENTO",
            "CATÁLOGO",
            "OPERAÇÃO",
            "FINANCEIRO",
            "GESTÃO",
        )
        posicoes = [source.index(secao) for secao in secoes]

        self.assertEqual(posicoes, sorted(posicoes))
        self.assertIn('aria-label="Navegação principal"', source)
        self.assertIn('aria-current="page"', source)
        self.assertLess(source.index("Estoque"), source.index("Compras"))
        self.assertLess(source.index("Relatórios"), source.index("Configurações"))

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


class CSRFExperienceTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)

    def test_login_expirado_reabre_formulario_e_preserva_destino(self):
        resposta = self.client.post(
            reverse("login"),
            {
                "username": "usuario",
                "password": "senha",
                "next": "/vendas/1/pdf/",
                "csrfmiddlewaretoken": "token-expirado",
            },
        )

        self.assertRedirects(
            resposta,
            f'{reverse("login")}?next=%2Fvendas%2F1%2Fpdf%2F',
            fetch_redirect_response=False,
        )
        resposta_login = self.client.get(resposta.url)
        self.assertContains(
            resposta_login,
            "Sua sessão expirou. Entre novamente para continuar.",
        )

    def test_pagina_interna_desatualizada_recarrega_sem_executar_post(self):
        Usuario = get_user_model()
        gerente = Usuario.objects.create_user(
            username="csrf-gerente",
            password="senha-segura",
            perfil=Usuario.Perfil.GERENTE,
        )
        produto = Produto.objects.create(modelo="Produto protegido")
        self.client.force_login(gerente)

        resposta = self.client.post(
            reverse("produtos:inativar_produto", args=[produto.pk]),
            {"csrfmiddlewaretoken": "token-expirado"},
            HTTP_REFERER="http://testserver/produtos/",
        )

        self.assertRedirects(
            resposta,
            reverse("produtos:lista_produtos"),
        )
        produto.refresh_from_db()
        self.assertTrue(produto.ativo)

    def test_destino_externo_e_descartado(self):
        resposta = self.client.post(
            reverse("login"),
            {
                "username": "usuario",
                "password": "senha",
                "next": "https://site-malicioso.example/roubo",
                "csrfmiddlewaretoken": "token-expirado",
            },
        )

        self.assertRedirects(
            resposta,
            f'{reverse("login")}?next=%2F',
        )


class CentralRelatoriosTests(SimpleTestCase):
    def test_todos_os_cards_possuem_destino_funcional(self):
        contexto = montar_central_relatorios()
        relatorios = [
            relatorio
            for secao in contexto["secoes"]
            for relatorio in secao["relatorios"]
        ]

        self.assertEqual(len(relatorios), 13)
        self.assertTrue(all(item["url"] for item in relatorios))
        self.assertEqual(contexto["indicadores"]["total_relatorios"], 13)

    def test_destinos_principais_sao_relatorios_dedicados(self):
        contexto = montar_central_relatorios()
        destinos = {
            relatorio["titulo"]: relatorio["url"]
            for secao in contexto["secoes"]
            for relatorio in secao["relatorios"]
        }

        self.assertEqual(destinos["Relatório de Clientes"], reverse("relatorio_analitico", kwargs={"slug": "clientes"}))
        self.assertEqual(destinos["Fluxo de Caixa"], reverse("relatorio_analitico", kwargs={"slug": "fluxo-caixa"}))
        self.assertEqual(destinos["Movimentações de Estoque"], reverse("relatorio_analitico", kwargs={"slug": "movimentacoes-estoque"}))


class RelatoriosAnaliticosTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Usuario = get_user_model()
        cls.usuario = Usuario.objects.create_superuser(
            username="admin_relatorios",
            password="senha-segura",
            perfil=Usuario.Perfil.ADMINISTRADOR,
        )

    def setUp(self):
        self.client.force_login(self.usuario)

    def test_todos_os_relatorios_dedicados_abrem_sem_dados(self):
        slugs = (
            "clientes", "produtos", "visao-financeira", "contas-receber",
            "contas-pagar", "fluxo-caixa", "posicao-estoque",
            "movimentacoes-estoque", "giro-produtos", "compras",
            "fornecedores", "evolucao-custos",
        )
        for slug in slugs:
            with self.subTest(slug=slug):
                resposta = self.client.get(
                    reverse("relatorio_analitico", kwargs={"slug": slug})
                )
                self.assertEqual(resposta.status_code, 200)
                self.assertTemplateUsed(resposta, "core/relatorio_analitico.html")

    def test_slug_desconhecido_retorna_404(self):
        resposta = self.client.get(
            reverse("relatorio_analitico", kwargs={"slug": "inexistente"})
        )
        self.assertEqual(resposta.status_code, 404)

    def test_filtro_rejeita_periodo_invertido(self):
        resposta = self.client.get(
            reverse("relatorio_analitico", kwargs={"slug": "clientes"}),
            {"data_inicial": "2026-08-10", "data_final": "2026-08-01"},
        )
        self.assertContains(resposta, "A data inicial não pode ser posterior")

    def test_periodo_rapido_e_tamanho_de_pagina(self):
        resposta = self.client.get(
            reverse("relatorio_analitico", kwargs={"slug": "clientes"}),
            {"periodo": "30d", "por_pagina": "50"},
        )
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.context["pagina"].paginator.per_page, 50)
        self.assertEqual(resposta.context["periodo_rapido"], "30d")

    def test_todos_os_relatorios_exportam_csv(self):
        for slug in (
            "clientes", "produtos", "visao-financeira", "contas-receber",
            "contas-pagar", "fluxo-caixa", "posicao-estoque",
            "movimentacoes-estoque", "giro-produtos", "compras",
            "fornecedores", "evolucao-custos",
        ):
            with self.subTest(slug=slug):
                resposta = self.client.get(
                    reverse("relatorio_analitico", kwargs={"slug": slug}),
                    {"exportar": "csv"},
                )
                self.assertEqual(resposta.status_code, 200)
                self.assertEqual(resposta["Content-Type"], "text/csv; charset=utf-8")

    def test_relatorios_prioritarios_geram_pdf_oficial(self):
        for slug in ("contas-receber", "contas-pagar", "fluxo-caixa", "posicao-estoque", "compras"):
            with self.subTest(slug=slug):
                resposta = self.client.get(
                    reverse("relatorio_analitico", kwargs={"slug": slug}),
                    {"exportar": "pdf"},
                )
                self.assertEqual(resposta.status_code, 200)
                self.assertEqual(resposta["Content-Type"], "application/pdf")
                self.assertTrue(resposta.content.startswith(b"%PDF"))

    def test_relatorio_sem_pdf_oficial_retorna_404(self):
        resposta = self.client.get(
            reverse("relatorio_analitico", kwargs={"slug": "clientes"}),
            {"exportar": "pdf"},
        )
        self.assertEqual(resposta.status_code, 404)
