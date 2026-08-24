from datetime import timedelta
from decimal import Decimal

from django.test import TestCase, override_settings
from django.core import mail
from django.urls import reverse
from django.utils import timezone

from financeiro.models import CategoriaFinanceira, ContaFinanceira
from usuarios.models import Usuario

from .forms import EventoForm, PessoaEquipeForm, VendaEventoForm
from .models import DespesaEvento, EquipeEvento, Evento, PessoaEquipe, ReceitaEvento, TipoProdutoEvento


class EventosUseHelviTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = Usuario.objects.create_user(
            username="eventos-adm", password="senha-forte", perfil="ADM",
            first_name="Paulo",
        )
        cls.categoria, _ = CategoriaFinanceira.objects.get_or_create(
            nome="Combustível", tipo=CategoriaFinanceira.TIPO_DESPESA,
        )
        cls.categoria_receita, _ = CategoriaFinanceira.objects.get_or_create(
            nome="Vendas e serviços", tipo=CategoriaFinanceira.TIPO_RECEITA,
        )
        cls.conta_financeira = ContaFinanceira.objects.create(
            nome="Conta Use Helvi", conta_padrao=True, operacao="use-helvi",
        )
        cls.tipo_produto, _ = TipoProdutoEvento.objects.get_or_create(nome="Casual feminino")

    def setUp(self):
        self.client.force_login(self.usuario)
        sessao = self.client.session
        sessao["operacao_ativa"] = "use-helvi"
        sessao.save()

    def criar_evento(self):
        agora = timezone.now() + timedelta(days=2)
        return Evento.objects.create(
            nome="Stand Feira Óptica", inicio=agora, fim=agora + timedelta(hours=8),
            responsavel=self.usuario, criado_por=self.usuario,
        )

    def test_agenda_e_cadastro_de_evento(self):
        resposta = self.client.post(
            reverse("eventos:novo"),
            {
                "nome": "Stand Feira Óptica", "status": "confirmado",
                "inicio": "2026-09-10T09:00", "fim": "2026-09-10T18:00",
                "local": "Centro de Eventos", "cidade": "São Paulo", "estado": "SP",
                "responsavel": self.usuario.pk, "participantes": [self.usuario.pk],
            },
        )
        evento = Evento.objects.get()
        self.assertRedirects(resposta, reverse("eventos:ficha", args=[evento.pk]))
        self.assertEqual(list(evento.participantes.all()), [self.usuario])
        self.assertContains(self.client.get(reverse("eventos:agenda")), "Stand Feira Óptica")

    def test_despesa_paga_integra_conta_e_baixa(self):
        evento = self.criar_evento()
        resposta = self.client.post(
            reverse("eventos:lancar_despesa", args=[evento.pk]),
            {
                "descricao": "Gasolina", "categoria": self.categoria.pk,
                "valor": "250.00", "ja_pago": "on", "data": "2026-08-24",
                "conta_financeira": self.conta_financeira.pk, "forma_pagamento": "pix",
            },
        )
        self.assertRedirects(resposta, reverse("eventos:ficha", args=[evento.pk]))
        conta = evento.despesas.get().conta_pagar
        self.assertEqual(conta.status, "paga")
        self.assertEqual(conta.valor_pago, Decimal("250.00"))
        self.assertEqual(conta.parcelas.get().baixas.count(), 1)

    def test_lucro_considera_venda_custo_e_despesa_pendente(self):
        evento = self.criar_evento()
        self.client.post(
            reverse("eventos:lancar_despesa", args=[evento.pk]),
            {
                "descricao": "Aluguel do carro", "categoria": self.categoria.pk,
                "valor": "900.00", "data": "2026-08-24", "vencimento": "2026-08-30",
            },
        )
        self.client.post(
            reverse("eventos:lancar_venda", args=[evento.pk]),
            {
                "data": "2026-08-24", "descricao": "Vendas do stand",
                "valor_venda": "5000.00", "custo_produtos": "1500.00",
                "valor_recebido": "4000.00", "forma_recebimento": "pix",
                "tipo_produto": self.tipo_produto.pk, "quantidade": 4,
            },
        )
        totais = Evento.objects.get(pk=evento.pk).totais
        self.assertEqual(totais["lucro"], Decimal("2600.00"))
        self.assertEqual(totais["a_receber"], Decimal("1000.00"))
        self.assertEqual(totais["gasto_pendente"], Decimal("900.00"))

    def test_despesa_geral_nao_entra_no_lucro_de_evento(self):
        evento = self.criar_evento()
        resposta = self.client.post(
            reverse("eventos:despesas_gerais"),
            {
                "descricao": "Expositores novos", "categoria": self.categoria.pk,
                "valor": "1200.00", "data": "2026-08-24", "vencimento": "2026-08-30",
            },
        )
        self.assertRedirects(resposta, reverse("eventos:despesas_gerais"))
        despesa = DespesaEvento.objects.get(evento__isnull=True)
        self.assertEqual(despesa.conta_pagar.operacao, "use-helvi")
        self.assertEqual(evento.totais["gasto"], Decimal("0.00"))

    def test_financeiro_filtra_contas_pela_operacao_ativa(self):
        use = self.criar_evento()
        self.client.post(
            reverse("eventos:lancar_despesa", args=[use.pk]),
            {
                "descricao": "Despesa Use", "categoria": self.categoria.pk,
                "valor": "100.00", "data": "2026-08-24", "vencimento": "2026-08-30",
            },
        )
        resposta = self.client.get(reverse("financeiro:lista_contas_pagar"))
        self.assertContains(resposta, "Despesa Use")
        sessao = self.client.session
        sessao["operacao_ativa"] = "distribuidora"
        sessao.save()
        self.assertNotContains(
            self.client.get(reverse("financeiro:lista_contas_pagar")), "Despesa Use"
        )

    def test_eventos_nao_abrem_na_operacao_distribuidora(self):
        sessao = self.client.session
        sessao["operacao_ativa"] = "distribuidora"
        sessao.save()
        self.assertRedirects(
            self.client.get(reverse("eventos:agenda")),
            reverse("dashboard"),
        )

    def test_cancelamento_exige_motivo_e_preserva_evento(self):
        evento = self.criar_evento()
        resposta = self.client.post(
            reverse("eventos:cancelar", args=[evento.pk]),
            {"motivo": "Organizador cancelou a feira."},
        )
        self.assertRedirects(resposta, reverse("eventos:ficha", args=[evento.pk]))
        evento.refresh_from_db()
        self.assertEqual(evento.status, Evento.STATUS_CANCELADO)
        self.assertEqual(evento.cancelado_por, self.usuario)
        self.assertEqual(evento.motivo_cancelamento, "Organizador cancelou a feira.")
        self.assertIsNotNone(evento.cancelado_em)
        agenda = self.client.get(reverse("eventos:agenda"))
        self.assertContains(agenda, "calendario-evento--cancelado")

    def test_cancelamento_sem_motivo_nao_altera_evento(self):
        evento = self.criar_evento()
        self.client.post(reverse("eventos:cancelar", args=[evento.pk]), {"motivo": ""})
        evento.refresh_from_db()
        self.assertNotEqual(evento.status, Evento.STATUS_CANCELADO)

    def test_cadastra_pessoa_e_equipe_e_inclui_integrantes_no_evento(self):
        self.client.post(reverse("eventos:equipes"), {
            "acao": "pessoa", "pessoa-nome": "Helen",
            "pessoa-tipo_contato": "whatsapp", "pessoa-contato": "11012345678",
        })
        pessoa = PessoaEquipe.objects.get(nome="Helen")
        self.assertEqual(pessoa.contato, "(11) 01234-5678")
        self.assertNotIn("instagram", PessoaEquipeForm().fields)
        self.client.post(reverse("eventos:equipes"), {
            "acao": "equipe", "equipe-nome": "Equipe principal",
            "equipe-pessoas": [pessoa.pk],
        })
        equipe = EquipeEvento.objects.get(nome="Equipe principal")
        agora = timezone.localtime(timezone.now() + timedelta(days=3))
        resposta = self.client.post(reverse("eventos:novo"), {
            "nome": "Evento com equipe", "status": "planejado",
            "inicio": agora.strftime("%Y-%m-%dT%H:%M"),
            "fim": (agora + timedelta(hours=4)).strftime("%Y-%m-%dT%H:%M"),
            "responsavel": self.usuario.pk, "equipe": equipe.pk,
        })
        self.assertEqual(resposta.status_code, 302)
        evento = Evento.objects.get(nome="Evento com equipe")
        self.assertEqual(list(evento.pessoas_equipe.all()), [pessoa])

    def test_cor_e_cadastrada_com_pessoa_e_combinada_na_agenda(self):
        paulo = PessoaEquipe.objects.create(nome="Paulo agenda", cor_agenda="#198754")
        helen = PessoaEquipe.objects.create(nome="Helen agenda", cor_agenda="#e78fba")
        evento = self.criar_evento()
        evento.pessoas_equipe.add(paulo, helen)

        resposta = self.client.get(reverse("eventos:agenda"))

        self.assertContains(resposta, "#198754")
        self.assertContains(resposta, "#e78fba")
        self.assertContains(resposta, "linear-gradient")

    def test_lembrete_aparece_em_popup_e_oferece_edicao(self):
        evento = self.criar_evento()
        evento.lembrete_ativo = True
        evento.lembrete_dias_antes = 3
        evento.lembrete_mensagem = "Separar produtos e conferir o expositor."
        evento.save(update_fields=[
            "lembrete_ativo", "lembrete_dias_antes", "lembrete_mensagem",
        ])

        resposta = self.client.get(reverse("eventos:agenda"))

        self.assertContains(resposta, "Você tem evento chegando")
        self.assertContains(resposta, evento.lembrete_mensagem)
        self.assertContains(resposta, reverse("eventos:editar", args=[evento.pk]))

    def test_lembrete_nao_aparece_antes_da_antecedencia(self):
        evento = self.criar_evento()
        evento.inicio = timezone.now() + timedelta(days=10)
        evento.fim = evento.inicio + timedelta(hours=8)
        evento.lembrete_ativo = True
        evento.lembrete_dias_antes = 2
        evento.save()

        resposta = self.client.get(reverse("eventos:agenda"))

        self.assertNotContains(resposta, "Você tem evento chegando")

    def test_contato_do_evento_e_formatado_no_backend(self):
        agora = timezone.localtime(timezone.now() + timedelta(days=3))
        form = EventoForm(data={
            "nome": "Contato formatado", "status": "planejado",
            "inicio": agora.strftime("%Y-%m-%dT%H:%M"),
            "fim": (agora + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M"),
            "responsavel": self.usuario.pk, "tipo_contato_responsavel": "telefone",
            "contato_responsavel": "11012345678",
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["contato_responsavel"], "(11) 01234-5678")

    def test_categoria_outros_existe_e_categoria_pode_ser_inativada(self):
        outros, _ = CategoriaFinanceira.objects.get_or_create(nome="Outros", tipo="despesa")
        resposta = self.client.post(reverse("eventos:alternar_categoria_despesa", args=[outros.pk]))
        self.assertRedirects(resposta, reverse("eventos:categorias_despesa"))
        outros.refresh_from_db()
        self.assertFalse(outros.ativo)

    def test_tipo_produto_pode_ser_editado_inativado_e_reativado(self):
        resposta = self.client.post(
            reverse("eventos:editar_tipo_produto", args=[self.tipo_produto.pk]),
            {"nome": "Casual feminino premium"},
        )
        self.assertRedirects(resposta, reverse("eventos:tipos_produto"))
        self.tipo_produto.refresh_from_db()
        self.assertEqual(self.tipo_produto.nome, "Casual feminino premium")

        url = reverse("eventos:alternar_tipo_produto", args=[self.tipo_produto.pk])
        self.client.post(url)
        self.tipo_produto.refresh_from_db()
        self.assertFalse(self.tipo_produto.ativo)
        self.assertFalse(
            VendaEventoForm().fields["tipo_produto"].queryset.filter(
                pk=self.tipo_produto.pk
            ).exists()
        )

        self.client.post(url)
        self.tipo_produto.refresh_from_db()
        self.assertTrue(self.tipo_produto.ativo)

    def test_receita_recebida_integra_conta_receber_e_caixa(self):
        resposta = self.client.post(reverse("eventos:financeiro"), {
            "acao": "receita", "receita-descricao": "Patrocínio",
            "receita-categoria": self.categoria_receita.pk, "receita-valor": "800.00",
            "receita-ja_recebido": "on", "receita-data": "2026-08-24",
            "receita-conta_financeira": self.conta_financeira.pk,
            "receita-forma_recebimento": "pix",
        })
        self.assertRedirects(resposta, reverse("eventos:financeiro"))
        conta = ReceitaEvento.objects.get().conta_receber
        self.assertEqual(conta.operacao, "use-helvi")
        self.assertEqual(conta.valor_recebido, Decimal("800.00"))

    def test_relatorio_financeiro_filtra_evento_e_gera_pdf(self):
        evento = self.criar_evento()
        parametros = {"inicio": "2026-01-01", "fim": "2026-12-31", "evento": evento.pk}
        resposta = self.client.get(reverse("eventos:relatorio_financeiro"), parametros)
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, evento.nome)
        parametros["exportar"] = "pdf"
        pdf = self.client.get(reverse("eventos:relatorio_financeiro"), parametros)
        self.assertEqual(pdf.status_code, 200)
        self.assertTrue(pdf.content.startswith(b"%PDF"))

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_relatorio_financeiro_envia_pdf_por_email(self):
        url = reverse("eventos:relatorio_financeiro") + "?inicio=2026-01-01&fim=2026-12-31"
        resposta = self.client.post(url, {"email": "gestao@example.com", "whatsapp": ""})
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].attachments[0][2], "application/pdf")

    def test_financeiro_unificado_tambem_lanca_despesa(self):
        resposta = self.client.post(reverse("eventos:financeiro"), {
            "acao": "despesa", "despesa-descricao": "Material do stand",
            "despesa-categoria": self.categoria.pk, "despesa-valor": "90.00",
            "despesa-data": "2026-08-24", "despesa-vencimento": "2026-08-30",
        })
        self.assertRedirects(resposta, reverse("eventos:financeiro"))
        self.assertTrue(DespesaEvento.objects.filter(conta_pagar__descricao="Material do stand").exists())

    def test_bloqueia_evento_duplicado_no_mesmo_dia(self):
        evento = self.criar_evento()
        inicio = timezone.localtime(evento.inicio)
        resposta = self.client.post(reverse("eventos:novo"), {
            "nome": evento.nome, "status": "planejado",
            "inicio": inicio.strftime("%Y-%m-%dT%H:%M"),
            "fim": (inicio + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M"),
            "responsavel": self.usuario.pk,
        })
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Já existe o evento")
        self.assertEqual(Evento.objects.filter(nome=evento.nome).count(), 1)

    def test_bloqueia_pessoa_em_dois_eventos_no_mesmo_dia(self):
        pessoa = PessoaEquipe.objects.create(nome="Helen", contato="11999999999")
        primeiro = self.criar_evento()
        primeiro.pessoas_equipe.add(pessoa)
        inicio = timezone.localtime(primeiro.inicio) + timedelta(hours=1)
        resposta = self.client.post(reverse("eventos:novo"), {
            "nome": "Outro stand", "status": "planejado",
            "inicio": inicio.strftime("%Y-%m-%dT%H:%M"),
            "fim": (inicio + timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M"),
            "responsavel": self.usuario.pk, "pessoas_equipe": [pessoa.pk],
        })
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "já está alocado")
        self.assertFalse(Evento.objects.filter(nome="Outro stand").exists())
