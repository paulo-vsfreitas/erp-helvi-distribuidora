from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from clientes.models import Cliente
from financeiro.models import (
    ContaFinanceira,
    ContaReceber,
    MovimentacaoFinanceira,
    ParcelaReceber,
    RecebimentoConta,
)
from produtos.models import Produto
from vendas.services.cancelamento_service import cancelar_venda
from vendas.services.finalizacao_service import finalizar_venda
from vendas.services.processamento_pagamento_service import (
    processar_pagamento_venda,
)
from vendas.models import ItemVenda, Venda


class ListaVendasTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user(
            username="vendas-teste",
            password="senha-segura",
        )
        Venda.objects.create(
            numero=1,
            status=Venda.STATUS_FINALIZADA,
            status_pagamento=Venda.PAGAMENTO_PAGO,
            total=Decimal("100.00"),
            valor_recebido=Decimal("100.00"),
            criada_por=cls.usuario,
        )
        Venda.objects.create(
            numero=2,
            status=Venda.STATUS_EM_ABERTO,
            status_pagamento=Venda.PAGAMENTO_PENDENTE,
            total=Decimal("50.00"),
            criada_por=cls.usuario,
        )
        Venda.objects.create(
            numero=3,
            status=Venda.STATUS_CANCELADA,
            status_pagamento=Venda.PAGAMENTO_PAGO,
            total=Decimal("200.00"),
            criada_por=cls.usuario,
        )

    def setUp(self):
        self.client.force_login(self.usuario)

    def test_indicadores_usam_somente_finalizadas_no_faturamento(self):
        response = self.client.get(reverse("vendas:lista"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_vendas"], 3)
        self.assertEqual(response.context["vendas_finalizadas"], 1)
        self.assertEqual(response.context["vendas_em_aberto"], 1)
        self.assertEqual(response.context["faturamento"], Decimal("100.00"))

    def test_filtra_por_status_e_pagamento(self):
        response = self.client.get(
            reverse("vendas:lista"),
            {
                "status": Venda.STATUS_FINALIZADA,
                "pagamento": Venda.PAGAMENTO_PAGO,
            },
        )

        self.assertEqual(response.context["page_obj"].paginator.count, 1)
        self.assertEqual(response.context["page_obj"][0].numero, 1)
        self.assertEqual(response.context["total_vendas"], 3)

    def test_busca_numero_aceita_prefixo(self):
        response = self.client.get(reverse("vendas:lista"), {"busca": "#2"})

        self.assertEqual(response.context["page_obj"].paginator.count, 1)
        self.assertEqual(response.context["page_obj"][0].numero, 2)

    def test_filtros_invalidos_voltam_para_todos(self):
        response = self.client.get(
            reverse("vendas:lista"),
            {"status": "inexistente", "pagamento": "inexistente"},
        )

        self.assertEqual(response.context["status"], "")
        self.assertEqual(response.context["pagamento"], "")
        self.assertEqual(response.context["page_obj"].paginator.count, 3)

    def test_relatorio_preserva_filtros_na_paginacao(self):
        response = self.client.get(
            reverse("vendas:relatorio"),
            {"status": Venda.STATUS_FINALIZADA, "pagina": 1},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["querystring"],
            f"status={Venda.STATUS_FINALIZADA}",
        )


class ProcessamentoPagamentoVendaTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user(
            username="pagamento-teste",
            password="senha-segura",
        )
        cls.cliente = Cliente.objects.create(
            razao_social="Cliente Pagamento Ltda",
            nome_fantasia="Cliente Pagamento",
            cnpj="22.222.222/0001-22",
        )

    def test_venda_a_prazo_sem_entrada_permanece_pendente(self):
        venda = Venda.objects.create(
            numero=100,
            cliente=self.cliente,
            forma_pagamento=Venda.FORMA_PRAZO,
            total=Decimal("300.00"),
            valor_entrada=Decimal("0.00"),
            quantidade_parcelas=3,
            criada_por=self.usuario,
        )

        conta = processar_pagamento_venda(
            venda=venda,
            usuario=self.usuario,
        )

        venda.refresh_from_db()
        self.assertEqual(
            venda.status_pagamento,
            Venda.PAGAMENTO_PENDENTE,
        )
        self.assertEqual(venda.valor_recebido, Decimal("0.00"))
        self.assertEqual(conta.valor_recebido, Decimal("0.00"))
        self.assertEqual(conta.parcelas.count(), 3)


class CancelamentoVendaTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user(
            username="cancelamento-venda",
            password="senha-segura",
        )
        cls.cliente = Cliente.objects.create(
            razao_social="Cliente Cancelamento Ltda",
            nome_fantasia="Cliente Cancelamento",
            cnpj="33.333.333/0001-33",
        )
        cls.produto = Produto.objects.create(
            codigo="CANC-001",
            modelo="Produto Cancelamento",
            preco_venda=Decimal("50.00"),
            estoque_atual=10,
        )

    def _criar_venda(self, *, numero, forma_pagamento):
        venda = Venda.objects.create(
            numero=numero,
            cliente=self.cliente,
            forma_pagamento=forma_pagamento,
            subtotal=Decimal("100.00"),
            total=Decimal("100.00"),
            quantidade_parcelas=2,
            criada_por=self.usuario,
        )
        ItemVenda.objects.create(
            venda=venda,
            produto=self.produto,
            quantidade=2,
            preco_unitario=Decimal("50.00"),
            total=Decimal("100.00"),
        )
        return venda

    def test_cancelamento_reverte_estoque_e_conta_a_receber(self):
        venda = self._criar_venda(
            numero=501,
            forma_pagamento=Venda.FORMA_PRAZO,
        )
        finalizar_venda(venda_id=venda.pk, usuario=self.usuario)

        cancelar_venda(
            venda=venda,
            usuario=self.usuario,
            motivo="Venda lançada incorretamente",
        )

        venda.refresh_from_db()
        self.produto.refresh_from_db()
        conta = ContaReceber.objects.get(
            origem=ContaReceber.ORIGEM_VENDA,
            origem_id=venda.pk,
        )

        self.assertEqual(venda.status, Venda.STATUS_CANCELADA)
        self.assertFalse(venda.estoque_baixado)
        self.assertEqual(self.produto.estoque_atual, 10)
        self.assertEqual(conta.status, ContaReceber.STATUS_CANCELADA)
        self.assertFalse(
            conta.parcelas.exclude(
                status=ParcelaReceber.STATUS_CANCELADA,
            ).exists()
        )
        self.assertTrue(
            self.produto.movimentacoes_estoque.filter(
                tipo="cancelamento_venda",
                origem="Venda nº 501",
            ).exists()
        )

    def test_cancelamento_estorna_recebimento_e_movimento_financeiro(self):
        conta_financeira = ContaFinanceira.objects.create(
            nome="Conta cancelamento",
        )
        venda = self._criar_venda(
            numero=502,
            forma_pagamento=Venda.FORMA_PIX,
        )
        venda.conta_financeira = conta_financeira
        venda.save(update_fields=["conta_financeira"])
        finalizar_venda(venda_id=venda.pk, usuario=self.usuario)

        recebimento = RecebimentoConta.objects.get(
            parcela__conta_receber__origem_id=venda.pk,
        )
        movimento = MovimentacaoFinanceira.objects.get(
            recebimento_conta=recebimento,
        )

        cancelar_venda(
            venda=venda,
            usuario=self.usuario,
            motivo="Cancelamento solicitado pelo cliente",
        )

        recebimento.refresh_from_db()
        movimento.refresh_from_db()
        self.assertTrue(recebimento.estornado)
        self.assertEqual(recebimento.estornado_por, self.usuario)
        self.assertTrue(movimento.estornada)

    def test_rota_de_cancelamento_aceita_somente_post(self):
        venda = self._criar_venda(
            numero=503,
            forma_pagamento=Venda.FORMA_PRAZO,
        )
        self.client.force_login(self.usuario)

        response = self.client.get(
            reverse("vendas:cancelar", args=[venda.numero])
        )

        self.assertEqual(response.status_code, 405)
        venda.refresh_from_db()
        self.assertEqual(venda.status, Venda.STATUS_EM_ABERTO)
