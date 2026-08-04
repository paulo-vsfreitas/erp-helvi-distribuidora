from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from compras.models import Compra, ItemCompra
from compras.services.cancelamento_compra_service import cancelar_compra
from compras.services.recebimento_service import receber_compra
from financeiro.models import ContaPagar
from produtos.models import Produto


class ListaComprasTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user(
            username="compras-teste",
            password="senha-segura",
            perfil="GER",
        )
        dados = {
            "fornecedor_nome": "Fornecedor Helvi",
            "data_compra": date(2026, 8, 3),
            "subtotal": Decimal("100.00"),
            "criado_por": cls.usuario,
        }
        Compra.objects.create(status=Compra.STATUS_RECEBIDA, **dados)
        Compra.objects.create(status=Compra.STATUS_AGUARDANDO_ENTREGA, **dados)
        Compra.objects.create(status=Compra.STATUS_CANCELADA, **dados)

    def setUp(self):
        self.client.force_login(self.usuario)

    def test_indicadores_nao_contam_cancelada_como_pendente(self):
        response = self.client.get(reverse("compras:lista"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_compras"], 3)
        self.assertEqual(response.context["recebidas"], 1)
        self.assertEqual(response.context["pendentes"], 1)

    def test_filtra_por_status(self):
        response = self.client.get(
            reverse("compras:lista"),
            {"status": Compra.STATUS_RECEBIDA},
        )

        self.assertEqual(response.context["page_obj"].paginator.count, 1)
        self.assertEqual(response.context["compras"][0].status, Compra.STATUS_RECEBIDA)

    def test_filtro_invalido_volta_para_todos(self):
        response = self.client.get(
            reverse("compras:lista"),
            {"status": "inexistente", "pagamento": "inexistente"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["status"], "")
        self.assertEqual(response.context["pagamento"], "")
        self.assertEqual(response.context["page_obj"].paginator.count, 3)

    def test_dashboard_antigo_redireciona_para_lista_padronizada(self):
        response = self.client.get(reverse("compras:dashboard"))

        self.assertRedirects(response, reverse("compras:lista"))


class FluxoIntegradoCompraTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user(
            username="fluxo-compra",
            password="senha-segura",
            perfil="GER",
        )
        cls.produto = Produto.objects.create(
            codigo="COMP-001",
            modelo="Produto Compra",
            estoque_atual=0,
            preco_custo=Decimal("10.00"),
        )

    def test_recebimento_e_cancelamento_revertem_todo_o_fluxo(self):
        compra = Compra.objects.create(
            numero=900,
            fornecedor_nome="Fornecedor do fluxo",
            data_compra=date.today(),
            subtotal=Decimal("100.00"),
            criado_por=self.usuario,
        )
        ItemCompra.objects.create(
            compra=compra,
            produto=self.produto,
            quantidade=2,
            custo_unitario=Decimal("50.00"),
        )

        receber_compra(compra, self.usuario)

        compra.refresh_from_db()
        self.produto.refresh_from_db()
        conta = ContaPagar.objects.get(compra=compra)
        self.assertEqual(compra.status, Compra.STATUS_RECEBIDA)
        self.assertTrue(compra.entrada_estoque_realizada)
        self.assertTrue(compra.financeiro_gerado)
        self.assertEqual(self.produto.estoque_atual, 2)
        self.assertEqual(self.produto.preco_custo, Decimal("50.00"))
        self.assertEqual(conta.valor_total, Decimal("100.00"))

        cancelar_compra(
            compra=compra,
            usuario=self.usuario,
            motivo="Compra cadastrada em duplicidade",
        )

        compra.refresh_from_db()
        self.produto.refresh_from_db()
        conta.refresh_from_db()
        self.assertEqual(compra.status, Compra.STATUS_CANCELADA)
        self.assertEqual(self.produto.estoque_atual, 0)
        self.assertEqual(conta.status, ContaPagar.STATUS_CANCELADA)
        self.assertTrue(
            self.produto.movimentacoes_estoque.filter(
                tipo="cancelamento_compra",
                origem="Compra #900",
            ).exists()
        )
