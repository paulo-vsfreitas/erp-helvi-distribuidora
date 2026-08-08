from django.test import TestCase

from produtos.models import Produto, VariacaoCor
from estoque.services.saldos import (
    alterar_saldo,
    sincronizar_estoque_produto,
)

class SaldoEstoquePorVariacaoTests(TestCase):
    def setUp(self):
        self.produto = Produto.objects.create(
            modelo="Produto A",
            preco_custo=10,
            preco_venda=20,
            estoque_atual=0,
        )

        self.c1 = VariacaoCor.objects.create(
            produto=self.produto,
            nome="Preto",
            codigo="C1",
            estoque=10,
        )

        self.c2 = VariacaoCor.objects.create(
            produto=self.produto,
            nome="Azul",
            codigo="C2",
            estoque=10,
        )

        self.c3 = VariacaoCor.objects.create(
            produto=self.produto,
            nome="Tartaruga",
            codigo="C3",
            estoque=5,
        )

        sincronizar_estoque_produto(
            self.produto
        )

    def test_total_produto_e_soma_das_variacoes(self):
        self.produto.refresh_from_db()

        self.assertEqual(
            self.produto.estoque_atual,
            25,
        )

    def test_entrada_em_variacao_atualiza_cor_e_total(self):
        alterar_saldo(
            produto=self.produto,
            variacao_cor=self.c2,
            quantidade=5,
            operacao="entrada",
        )

        self.c2.refresh_from_db()
        self.produto.refresh_from_db()

        self.assertEqual(self.c2.estoque, 15)
        self.assertEqual(
            self.produto.estoque_atual,
            30,
        )

    def test_saida_em_variacao_atualiza_cor_e_total(self):
        alterar_saldo(
            produto=self.produto,
            variacao_cor=self.c1,
            quantidade=3,
            operacao="saida",
        )

        self.c1.refresh_from_db()
        self.produto.refresh_from_db()

        self.assertEqual(self.c1.estoque, 7)
        self.assertEqual(
            self.produto.estoque_atual,
            22,
        )

    def test_produto_com_variacoes_exige_variacao(self):
        with self.assertRaisesMessage(
            Exception,
            "Selecione a Cor / Variação",
        ):
            alterar_saldo(
                produto=self.produto,
                quantidade=1,
                operacao="entrada",
            )