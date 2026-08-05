from django.core.exceptions import ValidationError
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TestCase, TransactionTestCase
from django.template.loader import get_template

from configuracoes.forms import EmpresaForm
from configuracoes.mensagens_padrao import (
    ASSUNTO_PADRAO_EMAIL,
    MENSAGEM_PADRAO_EMAIL,
    MENSAGEM_PADRAO_WHATSAPP,
)
from configuracoes.models import Empresa
from configuracoes.services import (
    CONTEXTO_EXEMPLO_MENSAGEM,
    renderizar_modelo_mensagem,
)


class ModelosMensagemTests(TestCase):
    def test_configuracao_define_canais_exibidos_nos_pdfs(self):
        empresa = Empresa(
            instagram="@helvi",
            facebook="facebook.com/helvi",
            exibir_instagram_pdf=True,
            exibir_facebook_pdf=False,
        )
        self.assertTrue(empresa.exibir_instagram_pdf)
        self.assertFalse(empresa.exibir_facebook_pdf)

    def test_nova_empresa_recebe_modelos_padrao_aprovados(self):
        empresa = Empresa()

        self.assertEqual(empresa.assunto_padrao_email, ASSUNTO_PADRAO_EMAIL)
        self.assertEqual(empresa.mensagem_padrao_email, MENSAGEM_PADRAO_EMAIL)
        self.assertEqual(
            empresa.mensagem_padrao_whatsapp,
            MENSAGEM_PADRAO_WHATSAPP,
        )

    def test_renderiza_todas_as_variaveis_permitidas(self):
        modelo = (
            "{CLIENTE}|{ORCAMENTO}|{TOTAL}|{VALIDADE}|"
            "{VENDEDOR}|{EMPRESA}"
        )
        contexto = {
            "CLIENTE": "Ótica Central",
            "ORCAMENTO": "ORC-000001",
            "TOTAL": "R$ 100,00",
            "VALIDADE": "14/08/2026",
            "VENDEDOR": "Paulo",
            "EMPRESA": "Helvi",
        }

        self.assertEqual(
            renderizar_modelo_mensagem(modelo, contexto),
            "Ótica Central|ORC-000001|R$ 100,00|14/08/2026|Paulo|Helvi",
        )

    def test_formulario_rejeita_variavel_desconhecida(self):
        form = EmpresaForm(
            data={
                "nome_fantasia": "Helvi Distribuidora",
                "razao_social": "Helvi Distribuidora",
                "mensagem_padrao_whatsapp": "Olá, {CONTATO}!",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("mensagem_padrao_whatsapp", form.errors)

    def test_renderizador_rejeita_chaves_invalidas(self):
        with self.assertRaises(ValidationError):
            renderizar_modelo_mensagem("Olá, {CLIENTE", {})

    def test_contexto_de_exemplo_renderiza_modelo(self):
        self.assertEqual(
            renderizar_modelo_mensagem(
                "Olá, {CLIENTE}! Orçamento {ORCAMENTO}.",
                CONTEXTO_EXEMPLO_MENSAGEM,
            ),
            "Olá, Ótica Central! Orçamento ORC-000123.",
        )

    def test_tela_carrega_contrato_do_editor_guiado(self):
        source = get_template(
            "configuracoes/dados_empresa.html"
        ).template.source

        self.assertIn("data-mensagem-variavel", source)
        self.assertIn("data-mensagem-previa", source)
        self.assertIn("editor_mensagens.js", source)


class ModelosMensagemMigrationTests(TransactionTestCase):
    migrate_from = [("configuracoes", "0002_empresa_modelos_mensagem")]
    migrate_to = [("configuracoes", "0004_empresa_redes_sociais_pdf")]

    def test_preenche_somente_campos_vazios(self):
        executor = MigrationExecutor(connection)
        executor.migrate(self.migrate_from)
        apps = executor.loader.project_state(self.migrate_from).apps
        EmpresaAnterior = apps.get_model("configuracoes", "Empresa")
        empresa = EmpresaAnterior.objects.create(
            nome_fantasia="Helvi",
            razao_social="Helvi Distribuidora",
            assunto_padrao_email="Assunto personalizado",
            mensagem_padrao_email="Mensagem personalizada",
            mensagem_padrao_whatsapp="",
        )

        executor = MigrationExecutor(connection)
        executor.migrate(self.migrate_to)
        apps = executor.loader.project_state(self.migrate_to).apps
        EmpresaMigrada = apps.get_model("configuracoes", "Empresa")
        empresa = EmpresaMigrada.objects.get(pk=empresa.pk)

        self.assertEqual(
            empresa.assunto_padrao_email,
            "Assunto personalizado",
        )
        self.assertEqual(
            empresa.mensagem_padrao_email,
            "Mensagem personalizada",
        )
        self.assertEqual(
            empresa.mensagem_padrao_whatsapp,
            MENSAGEM_PADRAO_WHATSAPP,
        )
