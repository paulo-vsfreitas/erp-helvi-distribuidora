import json
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from clientes.models import Cliente
from comercial.models import (
    CompartilhamentoOrcamento,
    ItemOrcamento,
    Orcamento,
)
from comercial.services.compartilhamento_service import (
    compartilhar_por_email,
    compartilhar_por_whatsapp,
)
from comercial.services.conversao_service import (
    converter_orcamento_em_venda,
)
from produtos.models import Produto
from usuarios.models import Usuario
from vendas.models import Venda


class DashboardComercialTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user(
            username="vendedor",
            password="senha-teste",
        )
        hoje = date.today()
        cls.orcamentos = {}
        valores = {
            Orcamento.Status.RASCUNHO: Decimal("1000.00"),
            Orcamento.Status.ENVIADO: Decimal("458.50"),
            Orcamento.Status.APROVADO: Decimal("880.30"),
            Orcamento.Status.REJEITADO: Decimal("381.70"),
            Orcamento.Status.CANCELADO: Decimal("200.00"),
            Orcamento.Status.CONVERTIDO: Decimal("780.30"),
        }
        for status, total in valores.items():
            cls.orcamentos[status] = Orcamento.objects.create(
                cliente_nome=f"Cliente {status}",
                vendedor=cls.usuario,
                data_emissao=hoje,
                data_validade=hoje + timedelta(days=15),
                status=status,
                total=total,
            )

    def setUp(self):
        self.client.force_login(self.usuario)
        self.url = reverse("comercial:dashboard")

    def test_valor_orcado_soma_apenas_carteira_ativa(self):
        response = self.client.get(self.url)

        self.assertEqual(response.context["valor_total"], Decimal("2338.80"))
        self.assertContains(response, "R$ 2.338,80")

    def test_cards_possuem_links_para_as_listas_correspondentes(self):
        response = self.client.get(self.url)

        self.assertContains(response, f'href="{self.url}"')
        self.assertContains(response, f'href="{self.url}?status=rascunho"')
        self.assertContains(response, f'href="{self.url}?status=aprovado"')

    def test_filtro_exibe_apenas_status_solicitado_e_mantem_totais_globais(self):
        response = self.client.get(self.url, {"status": "rascunho"})

        self.assertEqual(list(response.context["orcamentos"]), [
            self.orcamentos[Orcamento.Status.RASCUNHO],
        ])
        self.assertEqual(response.context["titulo_lista"], "Rascunhos")
        self.assertEqual(response.context["total_orcamentos"], 6)
        self.assertEqual(response.context["total_aprovados"], 1)

    def test_filtro_aprovado_exibe_apenas_aprovados(self):
        response = self.client.get(self.url, {"status": "aprovado"})

        self.assertEqual(list(response.context["orcamentos"]), [
            self.orcamentos[Orcamento.Status.APROVADO],
        ])
        self.assertEqual(response.context["titulo_lista"], "Aprovados")

    def test_filtro_invalido_volta_para_todos(self):
        response = self.client.get(self.url, {"status": "invalido"})

        self.assertEqual(response.context["filtro_status"], "")
        self.assertEqual(response.context["titulo_lista"], "Orçamentos recentes")
        self.assertEqual(response.context["orcamentos"].count(), 6)

    def test_filtro_por_cliente(self):
        response = self.client.get(self.url, {"busca": "Cliente enviado"})

        self.assertEqual(list(response.context["orcamentos"]), [
            self.orcamentos[Orcamento.Status.ENVIADO],
        ])
        self.assertTrue(response.context["filtros_ativos"])

    def test_filtro_por_codigo_do_orcamento(self):
        orcamento = self.orcamentos[Orcamento.Status.APROVADO]
        response = self.client.get(self.url, {"busca": orcamento.codigo})

        self.assertEqual(list(response.context["orcamentos"]), [orcamento])

    def test_filtros_de_status_e_periodo_podem_ser_combinados(self):
        hoje = date.today().isoformat()
        response = self.client.get(self.url, {
            "status": Orcamento.Status.REJEITADO,
            "data_inicio": hoje,
            "data_fim": hoje,
        })

        self.assertEqual(list(response.context["orcamentos"]), [
            self.orcamentos[Orcamento.Status.REJEITADO],
        ])

    def test_datas_invalidas_sao_ignoradas_com_seguranca(self):
        response = self.client.get(self.url, {
            "data_inicio": "invalida",
            "data_fim": "31-12-2026",
        })

        self.assertEqual(response.context["data_inicio"], "")
        self.assertEqual(response.context["data_fim"], "")
        self.assertEqual(response.context["orcamentos"].count(), 6)


class ConversaoOrcamentoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user(
            username="conversao-vendedor",
            password="senha-teste",
            perfil=Usuario.Perfil.VENDEDOR,
        )
        cls.cliente = Cliente.objects.create(
            razao_social="Cliente Conversão Ltda",
            nome_fantasia="Cliente Conversão",
            cnpj="11.111.111/0001-11",
        )
        cls.produto = Produto.objects.create(
            codigo="CONV-001",
            modelo="Produto Conversão",
            preco_venda=Decimal("100.00"),
            estoque_atual=10,
        )
        hoje = date.today()
        cls.orcamento = Orcamento.objects.create(
            cliente=cls.cliente,
            cliente_nome=cls.cliente.nome_fantasia,
            vendedor=cls.usuario,
            data_emissao=hoje,
            data_validade=hoje + timedelta(days=15),
            status=Orcamento.Status.APROVADO,
            desconto=Decimal("20.00"),
            frete=Decimal("5.00"),
        )
        ItemOrcamento.objects.create(
            orcamento=cls.orcamento,
            produto=cls.produto,
            quantidade=2,
            valor_unitario=Decimal("100.00"),
            desconto=Decimal("10.00"),
            total=Decimal("190.00"),
        )

    def test_conversao_copia_totais_itens_numero_e_responsavel(self):
        venda = converter_orcamento_em_venda(
            self.orcamento,
            usuario=self.usuario,
        )

        self.assertIsNotNone(venda.numero)
        self.assertEqual(venda.criada_por, self.usuario)
        self.assertEqual(venda.subtotal, Decimal("200.00"))
        self.assertEqual(venda.desconto, Decimal("30.00"))
        self.assertEqual(venda.frete, Decimal("5.00"))
        self.assertEqual(venda.total, Decimal("175.00"))

        item = venda.itens.get()
        self.assertEqual(item.desconto, Decimal("10.00"))
        self.assertEqual(item.total, Decimal("190.00"))

        self.orcamento.refresh_from_db()
        self.assertEqual(
            self.orcamento.status,
            Orcamento.Status.CONVERTIDO,
        )
        self.assertEqual(self.orcamento.venda_gerada, venda)

    def test_conversao_repetida_nao_cria_outra_venda(self):
        converter_orcamento_em_venda(
            self.orcamento,
            usuario=self.usuario,
        )

        with self.assertRaisesMessage(
            ValidationError,
            "Este orçamento já foi convertido em venda.",
        ):
            converter_orcamento_em_venda(
                self.orcamento,
                usuario=self.usuario,
            )

        self.assertEqual(Venda.objects.count(), 1)

    def test_rota_de_conversao_exige_autenticacao(self):
        response = self.client.post(
            reverse(
                "comercial:converter_orcamento",
                args=[self.orcamento.numero],
            )
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Venda.objects.count(), 0)

    def test_perfil_sem_vendas_nao_converte_orcamento(self):
        financeiro = get_user_model().objects.create_user(
            username="conversao-financeiro",
            password="senha-teste",
            perfil=Usuario.Perfil.FINANCEIRO,
        )
        self.client.force_login(financeiro)

        response = self.client.post(
            reverse(
                "comercial:converter_orcamento",
                args=[self.orcamento.numero],
            )
        )

        self.assertRedirects(response, reverse("dashboard"))
        self.assertEqual(Venda.objects.count(), 0)


class EdicaoOrcamentoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user(
            username="edicao-orcamento",
            password="senha-teste",
        )
        cls.cliente = Cliente.objects.create(
            razao_social="Cliente Edição Ltda",
            nome_fantasia="Cliente Edição",
            cnpj="44.444.444/0001-44",
        )
        cls.produto = Produto.objects.create(
            codigo="EDIT-001",
            modelo="Produto Edição",
            preco_venda=Decimal("50.00"),
        )
        hoje = date.today()
        cls.orcamento = Orcamento.objects.create(
            cliente=cls.cliente,
            cliente_nome=cls.cliente.nome_fantasia,
            vendedor=cls.usuario,
            data_emissao=hoje,
            data_validade=hoje + timedelta(days=10),
            status=Orcamento.Status.RASCUNHO,
        )
        ItemOrcamento.objects.create(
            orcamento=cls.orcamento,
            produto=cls.produto,
            quantidade=1,
            valor_unitario=Decimal("50.00"),
            total=Decimal("50.00"),
        )

    def setUp(self):
        self.client.force_login(self.usuario)

    def test_tela_carrega_itens_existentes(self):
        response = self.client.get(
            reverse("comercial:editar", args=[self.orcamento.numero])
        )

        self.assertEqual(response.status_code, 200)
        itens = json.loads(response.context["itens_json"])
        self.assertEqual(len(itens), 1)
        self.assertEqual(itens[0]["produto_id"], self.produto.pk)

    def test_edicao_atualiza_dados_itens_e_totais(self):
        response = self.client.post(
            reverse("comercial:editar", args=[self.orcamento.numero]),
            {
                "cliente": self.cliente.pk,
                "cliente_nome": "Cliente Edição Atualizado",
                "cliente_documento": "44.444.444/0001-44",
                "cliente_telefone": "11999999999",
                "cliente_email": "cliente@edicao.test",
                "data_validade": (
                    date.today() + timedelta(days=20)
                ).isoformat(),
                "desconto": "5,00",
                "frete": "0,00",
                "condicoes_comerciais": "30 dias",
                "observacoes": "Orçamento revisado",
                "itens_json": json.dumps(
                    [
                        {
                            "produto_id": self.produto.pk,
                            "quantidade": 3,
                            "valor_unitario": "50.00",
                            "desconto": "5.00",
                        }
                    ]
                ),
            },
        )

        self.assertRedirects(
            response,
            reverse("comercial:ficha", args=[self.orcamento.numero]),
        )
        self.orcamento.refresh_from_db()
        item = self.orcamento.itens.get()
        self.assertEqual(
            self.orcamento.cliente_nome,
            "Cliente Edição Atualizado",
        )
        self.assertEqual(self.orcamento.subtotal, Decimal("150.00"))
        self.assertEqual(self.orcamento.total, Decimal("140.00"))
        self.assertEqual(item.quantidade, 3)
        self.assertEqual(item.total, Decimal("145.00"))


class CompartilhamentoOrcamentoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user(
            username="compartilhamento-orcamento",
            password="senha-teste",
        )
        hoje = date.today()
        cls.orcamento = Orcamento.objects.create(
            cliente_nome="Cliente Compartilhamento",
            vendedor=cls.usuario,
            data_emissao=hoje,
            data_validade=hoje + timedelta(days=10),
            status=Orcamento.Status.RASCUNHO,
            total=Decimal("100.00"),
        )

    @patch(
        "comercial.services.compartilhamento_service."
        "gerar_pdf_orcamento_bytes",
        return_value=b"pdf",
    )
    @patch(
        "comercial.services.compartilhamento_service."
        "enviar_email_com_anexo",
        side_effect=RuntimeError("SMTP indisponível"),
    )
    def test_falha_de_email_permanece_no_historico(
        self,
        enviar_email,
        gerar_pdf,
    ):
        with self.assertRaises(RuntimeError):
            compartilhar_por_email(
                orcamento=self.orcamento,
                email="cliente@teste.com",
                assunto="Orçamento",
                mensagem="Segue orçamento",
                usuario=self.usuario,
            )

        historico = CompartilhamentoOrcamento.objects.get()
        self.assertEqual(
            historico.resultado,
            CompartilhamentoOrcamento.Resultado.FALHA,
        )
        self.assertEqual(
            historico.canal,
            CompartilhamentoOrcamento.Canal.EMAIL,
        )

    def test_whatsapp_preparado_nao_marca_orcamento_como_enviado(self):
        resultado = compartilhar_por_whatsapp(
            orcamento=self.orcamento,
            telefone="11999999999",
            mensagem="Segue orçamento",
            usuario=self.usuario,
            marcar_enviado=True,
        )

        self.orcamento.refresh_from_db()
        historico = CompartilhamentoOrcamento.objects.get()
        self.assertTrue(resultado.sucesso)
        self.assertEqual(
            self.orcamento.status,
            Orcamento.Status.RASCUNHO,
        )
        self.assertEqual(
            historico.resultado,
            CompartilhamentoOrcamento.Resultado.PREPARADO,
        )
