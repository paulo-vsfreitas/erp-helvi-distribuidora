import re
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from produtos.forms import ProdutoForm, VariacaoCorForm
from produtos.models import Produto, VariacaoCor
from django.core.files.uploadedfile import SimpleUploadedFile
from produtos.services.importacao import (
    importar_produtos,
)
from estoque.models import MovimentacaoEstoque


class AcoesProdutoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user(
            username="produto-acoes",
            password="senha-segura",
            perfil="GER",
        )
        cls.produto = Produto.objects.create(
            codigo="ACAO-001",
            modelo="Produto Ações",
        )

    def setUp(self):
        self.client.force_login(self.usuario)

    def test_get_nao_inativa_produto(self):
        response = self.client.get(
            reverse(
                "produtos:inativar_produto",
                args=[self.produto.pk],
            )
        )

        self.assertEqual(response.status_code, 405)
        self.produto.refresh_from_db()
        self.assertTrue(self.produto.ativo)

    def test_post_inativa_produto(self):
        response = self.client.post(
            reverse(
                "produtos:inativar_produto",
                args=[self.produto.pk],
            )
        )

        self.assertRedirects(
            response,
            reverse("produtos:lista_produtos"),
        )
        self.produto.refresh_from_db()
        self.assertFalse(self.produto.ativo)

    def test_listagem_alinha_dados_com_os_cabecalhos(self):
        self.produto.codigo_fornecedor = "FORN-6561"
        self.produto.estoque_atual = 15
        self.produto.estoque_minimo = 1
        self.produto.preco_venda = Decimal("55.00")
        self.produto.save()

        response = self.client.get(reverse("produtos:lista_produtos"))
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        cabecalho = re.search(r"<thead>.*?<tr>(.*?)</tr>", html, re.S).group(1)
        linha = re.search(r"<tbody>\s*<tr>(.*?)</tr>", html, re.S).group(1)

        self.assertEqual(cabecalho.count("<th"), 9)
        self.assertEqual(linha.count("<td"), 9)
        self.assertContains(response, "FORN-6561")
        self.assertContains(response, "15")
        self.assertContains(response, "Disponível")
        self.assertContains(response, "R$ 55,00")
        self.assertContains(response, "Ativo")
        self.assertNotContains(response, "produto.fornecedor")


class CamposOpcionaisProdutoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user(
            username="produto-campos-opcionais",
            password="senha-segura",
            perfil="GER",
        )

    def setUp(self):
        self.client.force_login(self.usuario)

    def payload_vazio(self):
        return {
            "categoria_comercial": Produto.CategoriaComercial.ARMACAO,
            "modelo": "",
            "marca": "",
            "colecao": "",
            "preco_custo": "0",
            "preco_venda": "0",
            "estoque_atual": "0",
            "estoque_minimo": "0",
            "ativo": "on",
            "cores-TOTAL_FORMS": "0",
            "cores-INITIAL_FORMS": "0",
            "cores-MIN_NUM_FORMS": "0",
            "cores-MAX_NUM_FORMS": "1000",
        }

    def test_formulario_aceita_identificacao_e_classificacao_vazias(self):
        form = ProdutoForm(self.payload_vazio())
        self.assertTrue(form.is_valid(), form.errors)
        self.assertIsNone(form.cleaned_data["codigo"])
        self.assertEqual(form.cleaned_data["modelo"], "")
        self.assertIsNone(form.cleaned_data["marca"])
        self.assertIsNone(form.cleaned_data["colecao"])

    def test_cadastro_e_edicao_aceitam_campos_vazios(self):
        resposta = self.client.post(
            reverse("produtos:novo_produto"),
            self.payload_vazio(),
        )
        self.assertRedirects(resposta, reverse("produtos:lista_produtos"))
        produto = Produto.objects.get()
        self.assertIsNone(produto.codigo)
        self.assertEqual(produto.modelo, "")

        resposta = self.client.post(
            reverse("produtos:editar_produto", args=[produto.pk]),
            self.payload_vazio(),
        )
        self.assertRedirects(resposta, reverse("produtos:lista_produtos"))

    def test_varios_produtos_podem_ficar_sem_codigo(self):
        Produto.objects.create(codigo=None, modelo="")
        Produto.objects.create(codigo=None, modelo="")
        self.assertEqual(Produto.objects.filter(codigo__isnull=True).count(), 2)

    def test_nome_descricao_da_cor_e_opcional(self):
        form = VariacaoCorForm({"nome": "", "codigo": "AZ01", "estoque": "0"})
        self.assertTrue(form.is_valid(), form.errors)

    def test_novo_produto_exibe_opcao_sem_variacao_marcada(self):
        resposta = self.client.get(reverse("produtos:novo_produto"))

        self.assertContains(resposta, "Produto sem variação de cor")
        self.assertContains(resposta, 'id="sem-variacao-cor" name="sem_variacao_cor" checked')

    def test_produto_sem_cor_e_salvo_sem_variacoes(self):
        dados = self.payload_vazio()
        dados["sem_variacao_cor"] = "on"

        resposta = self.client.post(reverse("produtos:novo_produto"), dados)

        self.assertRedirects(resposta, reverse("produtos:lista_produtos"))
        self.assertFalse(Produto.objects.get().variacoes_cor.exists())


class ImportacaoProdutosTests(TestCase):
    def setUp(self):
        from usuarios.models import Usuario

        self.usuario = Usuario.objects.create_user(
            username="admin_importacao",
            password="senha123",
            perfil="ADM",
        )
        self.client.force_login(self.usuario)

    def test_tela_importacao_abre(self):
        resposta = self.client.get(
            reverse("produtos:importar_produtos")
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Importar Produtos")
        self.assertContains(resposta, "Simular Importação")
        self.assertContains(resposta, "Baixar modelo Excel")

    def test_importacao_rejeita_extensao_invalida(self):
        arquivo = SimpleUploadedFile(
            "produtos.txt",
            b"arquivo invalido",
            content_type="text/plain",
        )

        resposta = self.client.post(
            reverse("produtos:importar_produtos"),
            {
                "arquivo": arquivo,
            },
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertContains(
            resposta,
            "Envie um arquivo Excel (.xlsx) ou CSV (.csv).",
        )

    def test_download_modelo_excel(self):
        resposta = self.client.get(
            reverse("produtos:modelo_importacao_produtos")
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(
            resposta["Content-Type"],
            (
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
        )
        self.assertIn(
            "modelo_importacao_produtos_helvi.xlsx",
            resposta["Content-Disposition"],
        )
        self.assertGreater(len(resposta.content), 1000)

class CategoriaComercialProdutoTests(TestCase):
    def test_novo_produto_assume_armacao_por_padrao(self):
        produto = Produto.objects.create(
            preco_custo=Decimal("10.00"),
            preco_venda=Decimal("20.00"),
        )

        self.assertEqual(
            produto.categoria_comercial,
            Produto.CategoriaComercial.ARMACAO,
        )

    def test_formulario_aceita_acessorio_sem_genero_e_tipo_armacao(self):
        form = ProdutoForm(
            data={
                "categoria_comercial": Produto.CategoriaComercial.ACESSORIO,
                "codigo_fornecedor": "FL-001",
                "modelo": "Flanela Premium",
                "marca": "",
                "colecao": "",
                "genero": "",
                "tipo_armacao": "",
                "preco_custo": "2.50",
                "preco_venda": "8.00",
                "estoque_atual": "20",
                "estoque_minimo": "5",
                "observacoes": "",
                "ativo": "on",
            }
        )

        self.assertTrue(form.is_valid(), form.errors)

    def test_acessorio_remove_genero_e_tipo_armacao(self):
        form = ProdutoForm(
            data={
                "categoria_comercial": Produto.CategoriaComercial.ACESSORIO,
                "codigo_fornecedor": "EST-001",
                "modelo": "Estojo Premium",
                "marca": "",
                "colecao": "",
                "genero": "",
                "tipo_armacao": "",
                "preco_custo": "5.00",
                "preco_venda": "15.00",
                "estoque_atual": "10",
                "estoque_minimo": "2",
                "observacoes": "",
                "ativo": "on",
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        self.assertIsNone(form.cleaned_data["genero"])
        self.assertIsNone(form.cleaned_data["tipo_armacao"])

class ImportadorRealProdutosTests(TestCase):
    def setUp(self):
        self.usuario = (
            get_user_model().objects.create_user(
                username="importador-real",
                password="senha123",
                perfil="ADM",
            )
        )

    def test_importa_armacao_com_variacoes(self):
        linhas = [
            {
                "linha": 2,
                "categoria_comercial": "armacao",
                "codigo_fornecedor": "ROM-001",
                "codigo": "",
                "modelo": "Roma",
                "marca": "",
                "colecao": "",
                "genero": "Adulto",
                "tipo_armacao": "Acetato",
                "sem_variacao": False,
                "cor_variacao": "Preto",
                "codigo_variacao": "C1",
                "custo": Decimal("25.00"),
                "venda": Decimal("75.00"),
                "estoque": 10,
                "estoque_minimo": 2,
                "observacoes": "",
                "erros": [],
            },
            {
                "linha": 3,
                "categoria_comercial": "armacao",
                "codigo_fornecedor": "ROM-001",
                "codigo": "",
                "modelo": "Roma",
                "marca": "",
                "colecao": "",
                "genero": "Adulto",
                "tipo_armacao": "Acetato",
                "sem_variacao": False,
                "cor_variacao": "Tartaruga",
                "codigo_variacao": "C2",
                "custo": Decimal("25.00"),
                "venda": Decimal("75.00"),
                "estoque": 5,
                "estoque_minimo": 2,
                "observacoes": "",
                "erros": [],
            },
        ]

        resultado = importar_produtos(
            linhas=linhas,
            usuario=self.usuario,
        )

        produto = Produto.objects.get(
            codigo_fornecedor="ROM-001"
        )

        self.assertEqual(
            resultado["produtos_criados"],
            1,
        )

        self.assertEqual(
            produto.variacoes_cor.count(),
            2,
        )

        self.assertEqual(
            produto.estoque_atual,
            15,
        )

        self.assertEqual(
            produto.variacoes_cor.get(
                codigo="C1"
            ).estoque,
            10,
        )

        self.assertEqual(
            produto.variacoes_cor.get(
                codigo="C2"
            ).estoque,
            5,
        )

        self.assertEqual(
            MovimentacaoEstoque.objects.filter(
                produto=produto,
                origem="Importação Inicial",
            ).count(),
            2,
        )

    def test_importa_acessorio_com_estoque_simples(self):
        linhas = [
            {
                "linha": 2,
                "categoria_comercial": "acessorio",
                "codigo_fornecedor": "FLA-001",
                "codigo": "",
                "modelo": "Flanela Premium",
                "marca": "",
                "colecao": "",
                "genero": "",
                "tipo_armacao": "",
                "sem_variacao": True,
                "cor_variacao": "",
                "codigo_variacao": "",
                "custo": Decimal("2.00"),
                "venda": Decimal("7.00"),
                "estoque": 30,
                "estoque_minimo": 5,
                "observacoes": "",
                "erros": [],
            },
        ]

        importar_produtos(
            linhas=linhas,
            usuario=self.usuario,
        )

        produto = Produto.objects.get(
            codigo_fornecedor="FLA-001"
        )

        self.assertEqual(
            produto.categoria_comercial,
            Produto.CategoriaComercial.ACESSORIO,
        )

        self.assertEqual(
            produto.estoque_atual,
            30,
        )

        self.assertFalse(
            produto.variacoes_cor.exists()
        )

        self.assertEqual(
            MovimentacaoEstoque.objects.filter(
                produto=produto,
                origem="Importação Inicial",
            ).count(),
            1,
        )

    def test_importacao_cria_referencias_do_catalogo(self):
        linhas = [
            {
                "linha": 2,
                "categoria_comercial": "armacao",
                "codigo_fornecedor": "TEST-001",
                "codigo": "",
                "modelo": "Teste",
                "marca": "Helvi Teste",
                "colecao": "Coleção Teste",
                "genero": "Adulto",
                "tipo_armacao": "Metal",
                "sem_variacao": False,
                "cor_variacao": "Preto",
                "codigo_variacao": "C1",
                "custo": Decimal("10.00"),
                "venda": Decimal("30.00"),
                "estoque": 1,
                "estoque_minimo": 0,
                "observacoes": "",
                "erros": [],
            },
        ]

        importar_produtos(
            linhas=linhas,
            usuario=self.usuario,
        )

        produto = Produto.objects.get(
            codigo_fornecedor="TEST-001"
        )

        self.assertEqual(
            produto.marca.nome,
            "Helvi Teste",
        )
        self.assertEqual(
            produto.colecao.nome,
            "Coleção Teste",
        )
        self.assertEqual(
            produto.genero.nome,
            "Adulto",
        )
        self.assertEqual(
            produto.tipo_armacao.nome,
            "Metal",
        )