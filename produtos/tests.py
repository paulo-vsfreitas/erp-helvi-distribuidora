from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from produtos.models import Produto


class AcoesProdutoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user(
            username="produto-acoes",
            password="senha-segura",
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
