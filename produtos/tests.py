import re
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from produtos.forms import ProdutoForm, VariacaoCorForm
from produtos.models import Produto


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
            "codigo": "",
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
