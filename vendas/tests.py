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
from produtos.models import Produto, VariacaoCor
from core.pdf.documents.venda import VendaPDF
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

    def test_relatorio_exporta_csv_e_pdf(self):
        csv_response = self.client.get(
            reverse("vendas:relatorio"), {"exportar": "csv"}
        )
        pdf_response = self.client.get(
            reverse("vendas:relatorio"), {"exportar": "pdf"}
        )
        self.assertEqual(csv_response["Content-Type"], "text/csv; charset=utf-8")
        self.assertEqual(pdf_response["Content-Type"], "application/pdf")
        self.assertTrue(pdf_response.content.startswith(b"%PDF"))

    def test_venda_em_aberto_possui_resumo_pdf(self):
        documento = VendaPDF(Venda.objects.get(numero=2))
        self.assertFalse(documento.pdf.exibir_data_emissao)

        documento._resumo_quantidades()
        resumo = documento.pdf.story[-1]._content[2]
        self.assertEqual(resumo._cellvalues[0][0].text, "PRODUTOS")
        self.assertEqual(resumo._cellvalues[0][1].text, "ITENS / VARIAÇÕES")
        self.assertEqual(resumo._cellvalues[0][2].text, "PEÇAS")

        response = self.client.get(reverse("vendas:pdf", args=[2]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertTrue(response.content.startswith(b"%PDF"))

    def test_venda_em_aberto_exibe_botao_editar(self):
        response = self.client.get(reverse("vendas:ficha", args=[2]))

        self.assertContains(response, reverse("vendas:editar", args=[2]))

    def test_api_produtos_retorna_variacoes_de_cor(self):
        produto = Produto.objects.create(
            codigo="COR-API", modelo="Produto com cor",
            preco_venda=Decimal("50.00"), estoque_atual=4,
        )
        cor = VariacaoCor.objects.create(
            produto=produto, nome="Azul", codigo="AZ", estoque=4,
        )
        response = self.client.get(reverse("vendas:api_produtos"), {"q": "COR-API"})
        self.assertEqual(response.json()["resultados"][0]["variacoes"][0]["id"], cor.pk)

    def test_relatorio_permite_configurar_paginacao_e_indica_filtros(self):
        response = self.client.get(
            reverse("vendas:relatorio"),
            {"por_pagina": "50", "status": Venda.STATUS_FINALIZADA},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["pagina"].paginator.per_page, 50)
        self.assertEqual(response.context["filtros_ativos"], 1)
        self.assertContains(response, "filtro ativo")


class EdicaoVendaEmAbertoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user(
            username="edicao-venda",
            password="senha-segura",
        )
        cls.cliente = Cliente.objects.create(
            razao_social="Cliente Edição Ltda",
            nome_fantasia="Cliente Edição",
            cnpj="44.444.444/0001-44",
        )
        cls.produto = Produto.objects.create(
            codigo="EDIT-001",
            modelo="Produto Editável",
            preco_venda=Decimal("60.00"),
            estoque_atual=8,
        )
        cls.cor = VariacaoCor.objects.create(
            produto=cls.produto,
            nome="Dourado",
            codigo="DOU",
            estoque=8,
        )

    def setUp(self):
        self.client.force_login(self.usuario)
        self.venda = Venda.objects.create(
            numero=701,
            cliente=self.cliente,
            subtotal=Decimal("60.00"),
            total=Decimal("60.00"),
            criada_por=self.usuario,
        )
        ItemVenda.objects.create(
            venda=self.venda,
            produto=self.produto,
            variacao_cor=self.cor,
            quantidade=1,
            preco_unitario=Decimal("60.00"),
            total=Decimal("60.00"),
        )

    def test_tela_carrega_dados_e_variacao_da_venda(self):
        response = self.client.get(reverse("vendas:editar", args=[self.venda.numero]))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["modo_edicao"])
        self.assertContains(response, "Editar venda nº 701")
        self.assertIn(f'"produto_id": {self.produto.pk}', response.context["itens_json"])
        self.assertIn(f'"variacao_cor_id": {self.cor.pk}', response.context["itens_json"])

    def test_atualiza_itens_totais_e_entrega_sem_processar_integracoes(self):
        response = self.client.post(
            reverse("vendas:editar", args=[self.venda.numero]),
            {
                "tipo_cliente": "cadastrado",
                "cliente": str(self.cliente.pk),
                "forma_pagamento": "",
                "conta_financeira": "",
                "desconto": "5,00",
                "frete": "10,00",
                "tipo_entrega": Venda.ENTREGA_ENVIO,
                "entrega_cep": "01001-000",
                "entrega_logradouro": "Praça da Sé",
                "entrega_numero": "100",
                "entrega_complemento": "",
                "entrega_bairro": "Sé",
                "entrega_cidade": "São Paulo",
                "entrega_estado": "SP",
                "observacoes": "Venda revisada",
                "produto_id[]": [str(self.produto.pk)],
                "variacao_cor_id[]": [str(self.cor.pk)],
                "quantidade[]": ["2"],
                "preco_unitario[]": ["60,00"],
                "desconto_item[]": ["5,00"],
                "acao": "salvar",
            },
        )

        self.assertEqual(
            response.status_code,
            302,
            response.context["form"].errors.as_json() if response.context else "",
        )
        self.assertEqual(
            response.status_code,
            302,
            response.context["form"].errors.as_json() if response.context else "",
        )
        self.assertRedirects(response, reverse("vendas:ficha", args=[701]))
        self.venda.refresh_from_db()
        item = self.venda.itens.get()
        self.assertEqual(self.venda.subtotal, Decimal("120.00"))
        self.assertEqual(self.venda.desconto, Decimal("10.00"))
        self.assertEqual(self.venda.frete, Decimal("10.00"))
        self.assertEqual(self.venda.total, Decimal("120.00"))
        self.assertEqual(self.venda.status, Venda.STATUS_EM_ABERTO)
        self.assertFalse(self.venda.estoque_baixado)
        self.assertFalse(self.venda.financeiro_gerado)
        self.assertEqual(item.quantidade, 2)
        self.assertEqual(item.variacao_cor, self.cor)
        self.assertEqual(item.total, Decimal("115.00"))

    def test_nao_permite_editar_venda_finalizada(self):
        self.venda.status = Venda.STATUS_FINALIZADA
        self.venda.save(update_fields=["status"])

        response = self.client.get(reverse("vendas:editar", args=[self.venda.numero]))

        self.assertRedirects(response, reverse("vendas:ficha", args=[701]))

    def test_permite_mesmo_produto_com_cores_diferentes(self):
        outra_cor = VariacaoCor.objects.create(
            produto=self.produto,
            nome="Preto",
            codigo="PTO",
            estoque=4,
        )
        response = self.client.post(
            reverse("vendas:editar", args=[self.venda.numero]),
            {
                "tipo_cliente": "cadastrado",
                "cliente": str(self.cliente.pk),
                "desconto": "0,00",
                "frete": "0,00",
                "tipo_entrega": Venda.ENTREGA_RETIRADA,
                "produto_id[]": [str(self.produto.pk), str(self.produto.pk)],
                "variacao_cor_id[]": [str(self.cor.pk), str(outra_cor.pk)],
                "quantidade[]": ["1", "2"],
                "preco_unitario[]": ["60,00", "60,00"],
                "desconto_item[]": ["0,00", "0,00"],
            },
        )

        self.assertEqual(
            response.status_code,
            302,
            response.context["form"].errors.as_json() if response.context else "",
        )
        self.assertRedirects(response, reverse("vendas:ficha", args=[701]))
        self.assertEqual(self.venda.itens.count(), 2)
        self.assertSetEqual(
            set(self.venda.itens.values_list("variacao_cor_id", flat=True)),
            {self.cor.pk, outra_cor.pk},
        )

    def test_mantem_alinhamento_entre_produto_sem_cor_e_produto_com_cor(self):
        produto_sem_cor = Produto.objects.create(
            codigo="SEM-COR",
            modelo="Produto sem variação",
            preco_venda=Decimal("30.00"),
            estoque_atual=5,
        )
        response = self.client.post(
            reverse("vendas:editar", args=[self.venda.numero]),
            {
                "tipo_cliente": "cadastrado",
                "cliente": str(self.cliente.pk),
                "desconto": "0,00",
                "frete": "0,00",
                "tipo_entrega": Venda.ENTREGA_RETIRADA,
                "produto_id[]": [str(produto_sem_cor.pk), str(self.produto.pk)],
                "variacao_cor_id[]": ["", str(self.cor.pk)],
                "quantidade[]": ["1", "1"],
                "preco_unitario[]": ["30,00", "60,00"],
                "desconto_item[]": ["0,00", "0,00"],
            },
        )

        self.assertRedirects(response, reverse("vendas:ficha", args=[701]))
        self.assertIsNone(
            self.venda.itens.get(produto=produto_sem_cor).variacao_cor_id
        )
        self.assertEqual(
            self.venda.itens.get(produto=self.produto).variacao_cor_id,
            self.cor.pk,
        )


class AlteracaoVendedorVendaTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Usuario = get_user_model()
        cls.gerente = Usuario.objects.create_user(
            username="gerente-vendas",
            password="senha-segura",
            perfil=Usuario.Perfil.GERENTE,
        )
        cls.vendedor = Usuario.objects.create_user(
            username="vendedor-original",
            password="senha-segura",
            perfil=Usuario.Perfil.VENDEDOR,
        )
        cls.novo_vendedor = Usuario.objects.create_user(
            username="novo-vendedor",
            password="senha-segura",
            perfil=Usuario.Perfil.VENDEDOR,
        )
        cls.financeiro = Usuario.objects.create_user(
            username="financeiro-vendas",
            password="senha-financeiro",
            perfil=Usuario.Perfil.FINANCEIRO,
        )
        cls.venda = Venda.objects.create(
            numero=801,
            status=Venda.STATUS_FINALIZADA,
            criada_por=cls.vendedor,
            total=Decimal("80.00"),
        )

    def test_gerente_altera_vendedor_com_senha_mesmo_finalizada(self):
        self.client.force_login(self.gerente)
        lista = self.client.get(reverse("vendas:lista"))
        self.assertContains(lista, "#alterar-vendedor")

        response = self.client.post(
            reverse("vendas:alterar_vendedor", args=[801]),
            {"vendedor": self.novo_vendedor.pk, "senha_autorizacao": "senha-segura"},
        )

        self.assertRedirects(response, reverse("vendas:ficha", args=[801]))
        self.venda.refresh_from_db()
        self.assertEqual(self.venda.criada_por, self.novo_vendedor)

    def test_vendedor_comum_nao_altera_responsavel(self):
        self.client.force_login(self.vendedor)
        response = self.client.post(
            reverse("vendas:alterar_vendedor", args=[801]),
            {"vendedor": self.novo_vendedor.pk},
        )

        self.assertEqual(response.status_code, 403)
        self.venda.refresh_from_db()
        self.assertEqual(self.venda.criada_por, self.vendedor)

    def test_financeiro_pode_alterar_vendedor_com_a_propria_senha(self):
        self.client.force_login(self.financeiro)
        response = self.client.post(
            reverse("vendas:alterar_vendedor", args=[801]),
            {"vendedor": self.novo_vendedor.pk, "senha_autorizacao": "senha-financeiro"},
        )
        self.assertRedirects(response, reverse("vendas:ficha", args=[801]))
        self.venda.refresh_from_db()
        self.assertEqual(self.venda.criada_por, self.novo_vendedor)

    def test_senha_incorreta_nao_altera_vendedor(self):
        self.client.force_login(self.gerente)
        self.client.post(
            reverse("vendas:alterar_vendedor", args=[801]),
            {"vendedor": self.novo_vendedor.pk, "senha_autorizacao": "incorreta"},
        )
        self.venda.refresh_from_db()
        self.assertEqual(self.venda.criada_por, self.vendedor)


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
        cls.administrador = get_user_model().objects.create_user(
            username="administrador-cancelamento",
            password="senha-administrador",
            perfil="ADM",
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
            autorizado_por=self.administrador,
            motivo="Venda lançada incorretamente",
        )

        venda.refresh_from_db()
        self.produto.refresh_from_db()
        conta = ContaReceber.objects.get(
            origem=ContaReceber.ORIGEM_VENDA,
            origem_id=venda.pk,
        )

        self.assertEqual(venda.status, Venda.STATUS_CANCELADA)
        self.assertEqual(venda.cancelada_por, self.usuario)
        self.assertEqual(
            venda.cancelamento_autorizado_por,
            self.administrador,
        )
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

    def test_finalizacao_preserva_custo_unitario_do_produto(self):
        self.produto.preco_custo = Decimal("22.00")
        self.produto.save(update_fields=["preco_custo"])
        venda = self._criar_venda(
            numero=504,
            forma_pagamento=Venda.FORMA_PRAZO,
        )

        finalizar_venda(venda_id=venda.pk, usuario=self.usuario)
        item = venda.itens.get()
        self.assertEqual(item.custo_unitario, Decimal("22.00"))

        self.produto.preco_custo = Decimal("99.00")
        self.produto.save(update_fields=["preco_custo"])
        item.refresh_from_db()
        self.assertEqual(item.custo_unitario, Decimal("22.00"))

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
            autorizado_por=self.administrador,
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

    def test_cancelamento_por_vendedor_exige_credencial_administrativa(self):
        venda = self._criar_venda(
            numero=505,
            forma_pagamento=Venda.FORMA_PRAZO,
        )
        self.client.force_login(self.usuario)

        response = self.client.post(
            reverse("vendas:cancelar", args=[venda.numero]),
            {
                "administrador_usuario": self.administrador.username,
                "administrador_senha": "senha-incorreta",
                "motivo": "Solicitação do cliente",
            },
        )

        self.assertRedirects(
            response,
            reverse("vendas:ficha", args=[venda.numero]),
        )
        venda.refresh_from_db()
        self.assertEqual(venda.status, Venda.STATUS_EM_ABERTO)
        self.assertIsNone(venda.cancelada_por)

    def test_vendedor_cancela_com_autorizacao_administrativa(self):
        venda = self._criar_venda(
            numero=506,
            forma_pagamento=Venda.FORMA_PRAZO,
        )
        self.client.force_login(self.usuario)

        response = self.client.post(
            reverse("vendas:cancelar", args=[venda.numero]),
            {
                "administrador_usuario": self.administrador.username,
                "administrador_senha": "senha-administrador",
                "motivo": "Solicitação confirmada pelo cliente",
            },
        )

        self.assertRedirects(
            response,
            reverse("vendas:ficha", args=[venda.numero]),
        )
        venda.refresh_from_db()
        self.assertEqual(venda.status, Venda.STATUS_CANCELADA)
        self.assertEqual(venda.cancelada_por, self.usuario)
        self.assertEqual(
            venda.cancelamento_autorizado_por,
            self.administrador,
        )


class FichaVendaApresentacaoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user(
            username="ficha-venda", password="senha-segura"
        )
        cls.cliente = Cliente.objects.create(
            razao_social="Ótica Teste Ltda",
            nome_fantasia="Ótica Teste",
            cnpj="44.444.444/0001-44",
            responsavel="Maria Responsável",
            whatsapp="(35) 99999-0000",
            email="cliente@otica.test",
        )
        cls.produto_com_cor = Produto.objects.create(
            modelo="Produto colorido", preco_custo=Decimal("20.00"),
            preco_venda=Decimal("50.00"), estoque_atual=5,
        )
        cls.cor = VariacaoCor.objects.create(
            produto=cls.produto_com_cor, nome="Azul", codigo="AZ", estoque=2,
        )
        cls.produto_sem_cor = Produto.objects.create(
            modelo="Produto sem cor", preco_custo=Decimal("10.00"),
            preco_venda=Decimal("25.00"), estoque_atual=5,
        )
        cls.venda = Venda.objects.create(
            numero=7001, subtotal=Decimal("100.00"), total=Decimal("100.00"),
            cliente=cls.cliente, criada_por=cls.usuario,
        )
        ItemVenda.objects.create(
            venda=cls.venda, produto=cls.produto_com_cor, variacao_cor=cls.cor,
            quantidade=1, preco_unitario=Decimal("50.00"), total=Decimal("50.00"),
        )
        ItemVenda.objects.create(
            venda=cls.venda, produto=cls.produto_sem_cor,
            quantidade=2, preco_unitario=Decimal("25.00"), total=Decimal("50.00"),
        )

    def test_ficha_exibe_produto_e_cor_nas_colunas_corretas(self):
        self.client.force_login(self.usuario)
        resposta = self.client.get(reverse("vendas:ficha", args=[self.venda.numero]))
        conteudo = resposta.content.decode()

        self.assertEqual(resposta.status_code, 200)
        self.assertLess(conteudo.index("Produto colorido"), conteudo.index("Azul (AZ)"))
        self.assertContains(resposta, "Sem variação")
        self.assertContains(resposta, "Não informado")
        self.assertNotContains(resposta, ">None<")

    def test_resumo_separa_produtos_itens_e_pecas(self):
        self.client.force_login(self.usuario)
        resposta = self.client.get(reverse("vendas:ficha", args=[self.venda.numero]))
        venda = resposta.context["venda"]

        self.assertEqual(venda.quantidade_produtos, 2)
        self.assertEqual(venda.quantidade_itens, 2)
        self.assertEqual(venda.quantidade_pecas, 3)
        self.assertContains(resposta, "Itens / variações")

    def test_cabecalho_exibe_contatos_e_nao_repete_acao_pdf(self):
        self.client.force_login(self.usuario)
        resposta = self.client.get(reverse("vendas:ficha", args=[self.venda.numero]))

        self.assertContains(resposta, "44.444.444/0001-44")
        self.assertContains(resposta, "Maria Responsável")
        self.assertContains(resposta, "(35) 99999-0000")
        self.assertContains(resposta, "cliente@otica.test")
        self.assertNotContains(resposta, ">Resumo em PDF<")
        self.assertContains(resposta, "Abrir resumo em PDF")
        html = resposta.content.decode()

        self.assertRegex(
            html,
            r"/static/css/vendas(?:\.[0-9a-f]+)?\.css\?v=1\.1\.0",
        )
