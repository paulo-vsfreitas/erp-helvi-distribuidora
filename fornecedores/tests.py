from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from fornecedores.models import Fornecedor


class PainelFornecedoresTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_superuser(
            username="fornecedores-teste",
            password="senha-segura",
            email="teste@helvi.local",
        )
        Fornecedor.objects.create(
            razao_social="Fornecedor Ativo SP",
            cpf_cnpj="11.111.111/0001-11",
            estado="SP",
            ativo=True,
        )
        Fornecedor.objects.create(
            razao_social="Fornecedor Inativo RJ",
            cpf_cnpj="22.222.222/0001-22",
            estado="RJ",
            ativo=False,
        )

    def setUp(self):
        self.client.force_login(self.usuario)

    def test_dashboard_exibe_indicadores_e_listagem(self):
        response = self.client.get(reverse("fornecedores:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_fornecedores"], 2)
        self.assertEqual(response.context["fornecedores_ativos"], 1)
        self.assertEqual(response.context["fornecedores_inativos"], 1)
        self.assertEqual(response.context["page_obj"].paginator.count, 2)
        self.assertContains(response, "Filtrar fornecedores")

    def test_filtra_por_situacao_e_estado(self):
        response = self.client.get(
            reverse("fornecedores:dashboard"),
            {"status": "ativos", "estado": "SP"},
        )

        self.assertEqual(response.context["page_obj"].paginator.count, 1)
        self.assertEqual(
            response.context["page_obj"][0].razao_social,
            "Fornecedor Ativo SP",
        )
        self.assertEqual(response.context["total_fornecedores"], 2)

    def test_filtros_invalidos_voltam_para_todos(self):
        response = self.client.get(
            reverse("fornecedores:lista"),
            {"status": "desconhecido", "estado": "XX"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["status_atual"], "")
        self.assertEqual(response.context["estado_atual"], "")
        self.assertEqual(response.context["page_obj"].paginator.count, 2)

    def test_dashboard_e_lista_usam_o_mesmo_painel(self):
        for nome_rota in ("fornecedores:dashboard", "fornecedores:lista"):
            with self.subTest(rota=nome_rota):
                response = self.client.get(reverse(nome_rota))
                self.assertContains(response, "hui-module-page--fornecedores")
                self.assertContains(response, "Novo fornecedor")
