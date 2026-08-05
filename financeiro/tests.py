from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from financeiro.models import (
    CategoriaFinanceira,
    ContaFinanceira,
    ContaPagar,
    ContaReceber,
    HistoricoContaPagar,
    HistoricoContaReceber,
    MovimentacaoFinanceira,
    ParcelaPagar,
    ParcelaReceber,
)
from financeiro.services.baixa_service import registrar_baixa
from financeiro.services.estorno_service import (
    estornar_baixa,
    estornar_recebimento,
)
from financeiro.services.recebimento_service import registrar_recebimento
from financeiro.services.fluxo_caixa_service import obter_fluxo_caixa
from financeiro.services.rentabilidade_service import obter_rentabilidade
from produtos.models import Produto
from vendas.models import ItemVenda, Venda


class EstornoFinanceiroTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user(
            username="financeiro",
            password="senha-segura",
            perfil="ADM",
        )
        cls.conta_financeira = ContaFinanceira.objects.create(
            nome="Caixa de testes",
            tipo=ContaFinanceira.TIPO_CAIXA,
            saldo_inicial=Decimal("1000.00"),
        )
        cls.categoria_despesa = CategoriaFinanceira.objects.create(
            nome="Despesa de testes",
            tipo=CategoriaFinanceira.TIPO_DESPESA,
        )
        cls.categoria_receita = CategoriaFinanceira.objects.create(
            nome="Receita de testes",
            tipo=CategoriaFinanceira.TIPO_RECEITA,
        )

    def criar_baixa(self):
        conta = ContaPagar.objects.create(
            descricao="Conta a pagar de testes",
            categoria=self.categoria_despesa,
            valor_total=Decimal("100.00"),
            criado_por=self.usuario,
        )
        parcela = ParcelaPagar.objects.create(
            conta_pagar=conta,
            numero=1,
            data_vencimento=date.today(),
            valor_original=Decimal("100.00"),
        )
        baixa = registrar_baixa(
            parcela=parcela,
            conta_financeira=self.conta_financeira,
            data_pagamento=date.today(),
            valor=Decimal("100.00"),
            usuario=self.usuario,
        )
        return conta, parcela, baixa

    def criar_recebimento(self):
        conta = ContaReceber.objects.create(
            descricao="Conta a receber de testes",
            nome_devedor="Cliente de testes",
            categoria=self.categoria_receita,
            valor_total=Decimal("100.00"),
            criado_por=self.usuario,
        )
        parcela = ParcelaReceber.objects.create(
            conta_receber=conta,
            numero=1,
            data_vencimento=date.today(),
            valor_original=Decimal("100.00"),
        )
        recebimento = registrar_recebimento(
            parcela=parcela,
            conta_financeira=self.conta_financeira,
            data_recebimento=date.today(),
            valor=Decimal("100.00"),
            forma_recebimento="pix",
            usuario=self.usuario,
        )
        return conta, parcela, recebimento

    def test_estorno_de_baixa_reabre_parcela_e_preserva_saldo(self):
        conta, parcela, baixa = self.criar_baixa()
        self.assertEqual(self.conta_financeira.saldo_atual, Decimal("900.00"))

        estornar_baixa(
            baixa=baixa,
            usuario=self.usuario,
            motivo="Pagamento lançado em duplicidade",
        )

        baixa.refresh_from_db()
        parcela.refresh_from_db()
        conta.refresh_from_db()
        self.assertTrue(baixa.estornada)
        self.assertEqual(parcela.valor_pago, Decimal("0.00"))
        self.assertEqual(parcela.status, ParcelaPagar.STATUS_PENDENTE)
        self.assertEqual(conta.valor_pago, Decimal("0.00"))
        self.assertEqual(conta.status, ContaPagar.STATUS_PENDENTE)
        self.assertEqual(self.conta_financeira.saldo_atual, Decimal("1000.00"))
        self.assertTrue(
            baixa.movimentacoes.filter(
                tipo=MovimentacaoFinanceira.TIPO_ESTORNO_SAIDA,
            ).exists()
        )
        self.assertTrue(
            conta.historicos.filter(
                tipo_evento=HistoricoContaPagar.EVENTO_ESTORNO,
            ).exists()
        )

    def test_estorno_de_recebimento_reabre_parcela_e_preserva_saldo(self):
        conta, parcela, recebimento = self.criar_recebimento()
        self.assertEqual(self.conta_financeira.saldo_atual, Decimal("1100.00"))

        estornar_recebimento(
            recebimento=recebimento,
            usuario=self.usuario,
            motivo="Recebimento informado na conta errada",
        )

        recebimento.refresh_from_db()
        parcela.refresh_from_db()
        conta.refresh_from_db()
        self.assertTrue(recebimento.estornado)
        self.assertEqual(parcela.valor_recebido, Decimal("0.00"))
        self.assertEqual(parcela.status, ParcelaReceber.STATUS_PENDENTE)
        self.assertEqual(conta.valor_recebido, Decimal("0.00"))
        self.assertEqual(conta.status, ContaReceber.STATUS_PENDENTE)
        self.assertEqual(self.conta_financeira.saldo_atual, Decimal("1000.00"))
        self.assertTrue(
            recebimento.movimentacoes.filter(
                tipo=MovimentacaoFinanceira.TIPO_ESTORNO_ENTRADA,
            ).exists()
        )
        self.assertTrue(
            conta.historicos.filter(
                tipo_evento=HistoricoContaReceber.EVENTO_ESTORNO,
            ).exists()
        )

    def test_estorno_exige_motivo_e_nao_altera_dados(self):
        conta, parcela, baixa = self.criar_baixa()

        with self.assertRaises(ValidationError):
            estornar_baixa(
                baixa=baixa,
                usuario=self.usuario,
                motivo="não",
            )

        baixa.refresh_from_db()
        parcela.refresh_from_db()
        conta.refresh_from_db()
        self.assertFalse(baixa.estornada)
        self.assertEqual(parcela.valor_pago, Decimal("100.00"))
        self.assertEqual(conta.valor_pago, Decimal("100.00"))
        self.assertEqual(baixa.movimentacoes.count(), 1)

    def test_estorno_nao_pode_ser_repetido(self):
        _, _, baixa = self.criar_baixa()
        estornar_baixa(
            baixa=baixa,
            usuario=self.usuario,
            motivo="Primeiro estorno válido",
        )

        with self.assertRaises(ValidationError):
            estornar_baixa(
                baixa=baixa,
                usuario=self.usuario,
                motivo="Tentativa de repetir o estorno",
            )

        self.assertEqual(
            baixa.movimentacoes.filter(
                tipo=MovimentacaoFinanceira.TIPO_ESTORNO_SAIDA,
            ).count(),
            1,
        )

    def test_view_de_estorno_processa_somente_no_post(self):
        conta, _, baixa = self.criar_baixa()
        self.client.force_login(self.usuario)
        url = reverse("financeiro:estornar_baixa", args=[baixa.pk])

        resposta_get = self.client.get(url)
        baixa.refresh_from_db()
        self.assertEqual(resposta_get.status_code, 200)
        self.assertFalse(baixa.estornada)

        resposta_post = self.client.post(
            url,
            {"motivo": "Correção validada pela equipe financeira"},
        )
        baixa.refresh_from_db()
        self.assertRedirects(
            resposta_post,
            reverse("financeiro:ficha_conta_pagar", args=[conta.pk]),
        )
        self.assertTrue(baixa.estornada)


class FluxoCaixaTests(TestCase):
    def setUp(self):
        self.usuario = get_user_model().objects.create_user(
            username="caixa", password="senha-segura", perfil="ADM"
        )
        self.conta = ContaFinanceira.objects.create(
            nome="Banco", tipo=ContaFinanceira.TIPO_CONTA_CORRENTE, saldo_inicial=Decimal("0.00")
        )

    def test_movimento_do_periodo_nao_entra_no_saldo_anterior(self):
        MovimentacaoFinanceira.objects.create(
            conta_financeira=self.conta,
            tipo=MovimentacaoFinanceira.TIPO_ENTRADA,
            data_movimentacao=date.today(),
            valor=Decimal("1099.00"),
            descricao="Recebimento da venda",
            criado_por=self.usuario,
        )
        resultado = obter_fluxo_caixa({})
        self.assertEqual(resultado["saldo_anterior"], Decimal("0.00"))
        self.assertEqual(resultado["total_entradas"], Decimal("1099.00"))
        self.assertEqual(resultado["saldo_final"], Decimal("1099.00"))
        self.assertEqual(resultado["quantidade_movimentacoes"], 1)


class RentabilidadeTests(TestCase):
    def setUp(self):
        self.usuario = get_user_model().objects.create_user(
            username="gestor", password="senha-segura", perfil="ADM"
        )
        self.produto = Produto.objects.create(
            modelo="Produto rentável", preco_custo=Decimal("40.00"),
            preco_venda=Decimal("70.00"), estoque_atual=10,
        )
        self.venda = Venda.objects.create(
            numero=9001, status=Venda.STATUS_FINALIZADA,
            subtotal=Decimal("140.00"), desconto=Decimal("10.00"),
            frete=Decimal("20.00"), total=Decimal("150.00"),
            criada_por=self.usuario,
        )
        ItemVenda.objects.create(
            venda=self.venda, produto=self.produto, quantidade=2,
            preco_unitario=Decimal("70.00"), custo_unitario=Decimal("40.00"),
            desconto=Decimal("0.00"), total=Decimal("140.00"),
        )

    def test_calcula_lucro_com_custo_historico_e_sem_frete(self):
        self.produto.preco_custo = Decimal("99.00")
        self.produto.save(update_fields=["preco_custo"])
        resultado = obter_rentabilidade({})
        self.assertEqual(resultado["receita_produtos"], Decimal("130.00"))
        self.assertEqual(resultado["custo_total"], Decimal("80.00"))
        self.assertEqual(resultado["lucro_bruto"], Decimal("50.00"))
        self.assertEqual(resultado["frete_total"], Decimal("20.00"))

    def test_tela_de_rentabilidade_exibe_venda(self):
        self.client.force_login(self.usuario)
        resposta = self.client.get(reverse("financeiro:rentabilidade"))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Lucro e margem")
        self.assertContains(resposta, "#009001")
