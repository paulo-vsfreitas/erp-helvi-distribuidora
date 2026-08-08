from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from datetime import timedelta

from usuarios.forms import UsuarioForm
from usuarios.models import ControleTentativaLogin, EventoLogin


class FormularioUsuarioTests(TestCase):
    def setUp(self):
        Usuario = get_user_model()
        self.administrador = Usuario.objects.create_superuser(
            username="administrador_teste",
            password="senha-admin-segura",
            perfil=Usuario.Perfil.ADMINISTRADOR,
        )
        self.usuario = Usuario.objects.create_user(
            username="usuario_teste",
            password="senha-original-segura",
            first_name="Usuário",
            last_name="Teste",
            email="usuario@teste.com",
            telefone="11999999999",
            perfil=Usuario.Perfil.VENDEDOR,
        )
        self.client.force_login(self.administrador)
        self.url = reverse(
            "usuarios:editar_usuario",
            kwargs={"pk": self.usuario.pk},
        )

    def test_tela_edicao_renderiza_layout_helvi_ui(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "hui-user-form-layout")
        self.assertContains(response, "Identificação do usuário")
        self.assertContains(response, "Segurança da conta")
        self.assertContains(response, "Acesso e permissões")
        self.assertContains(response, "Salvar alterações")
        html = response.content.decode()

        self.assertRegex(
            html,
            r"/static/css/usuarios(?:\.[0-9a-f]+)?\.css(?:\?v=[^\"']+)?",
        )

        self.assertRegex(
            html,
            r"/static/js/usuarios/form_usuario(?:\.[0-9a-f]+)?\.js(?:\?v=[^\"']+)?",
        )

        form = response.context["form"]
        self.assertEqual(
            form.fields["foto"].widget.input_type,
            "file",
        )
        self.assertIn(
            "hui-user-photo-input",
            form.fields["foto"].widget.attrs["class"],
        )
        self.assertIn(
            "hui-user-switch-input",
            form.fields["is_active"].widget.attrs["class"],
        )

    def test_edicao_sem_nova_senha_preserva_senha_atual(self):
        senha_anterior = self.usuario.password

        response = self.client.post(
            self.url,
            {
                "username": "usuario_atualizado",
                "first_name": "Nome",
                "last_name": "Atualizado",
                "email": "atualizado@teste.com",
                "telefone": "11988887777",
                "perfil": get_user_model().Perfil.GERENTE,
                "is_active": "on",
                "senha": "",
                "confirmar_senha": "",
            },
        )

        self.assertRedirects(
            response,
            reverse("usuarios:lista_usuarios"),
        )
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.username, "usuario_atualizado")
        self.assertEqual(
            self.usuario.perfil,
            get_user_model().Perfil.GERENTE,
        )
        self.assertTrue(self.usuario.is_active)
        self.assertTrue(self.usuario.is_staff)
        self.assertEqual(self.usuario.password, senha_anterior)
        self.assertTrue(
            self.usuario.check_password("senha-original-segura")
        )

    def test_senhas_diferentes_mantem_formulario_com_erro(self):
        response = self.client.post(
            self.url,
            {
                "username": self.usuario.username,
                "first_name": self.usuario.first_name,
                "last_name": self.usuario.last_name,
                "email": self.usuario.email,
                "telefone": self.usuario.telefone,
                "perfil": self.usuario.perfil,
                "is_active": "on",
                "senha": "nova-senha-segura",
                "confirmar_senha": "outra-senha-segura",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "confirmar_senha",
            "As senhas não conferem.",
        )
        self.assertContains(response, "As senhas não conferem.")


class PermissoesModulosTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Usuario = get_user_model()
        cls.vendedor = Usuario.objects.create_user(
            username="permissao-vendedor",
            password="senha-segura",
            perfil=Usuario.Perfil.VENDEDOR,
        )
        cls.financeiro = Usuario.objects.create_user(
            username="permissao-financeiro",
            password="senha-segura",
            perfil=Usuario.Perfil.FINANCEIRO,
        )
        cls.gerente = Usuario.objects.create_user(
            username="permissao-gerente",
            password="senha-segura",
            perfil=Usuario.Perfil.GERENTE,
        )

    def test_vendedor_nao_acessa_financeiro_por_url_direta(self):
        self.client.force_login(self.vendedor)

        response = self.client.get(
            reverse("financeiro:dashboard")
        )

        self.assertRedirects(response, reverse("dashboard"))

    def test_vendedor_consulta_produtos_mas_nao_cadastra_por_url(self):
        self.client.force_login(self.vendedor)

        consulta = self.client.get(reverse("produtos:lista_produtos"))
        cadastro = self.client.get(reverse("produtos:novo_produto"))

        self.assertEqual(consulta.status_code, 200)
        self.assertEqual(cadastro.status_code, 403)

    def test_vendedor_consulta_estoque_mas_nao_movimenta_por_url(self):
        self.client.force_login(self.vendedor)

        consulta = self.client.get(reverse("estoque:lista_movimentacoes"))
        entrada = self.client.get(reverse("estoque:nova_entrada"))
        inventario = self.client.get(reverse("estoque:novo_inventario"))

        self.assertEqual(consulta.status_code, 200)
        self.assertEqual(entrada.status_code, 403)
        self.assertEqual(inventario.status_code, 403)

    def test_vendedor_consulta_catalogo_mas_nao_edita_por_url(self):
        self.client.force_login(self.vendedor)

        consulta = self.client.get(reverse("catalogo:lista_marcas"))
        cadastro = self.client.get(reverse("catalogo:nova_marca"))

        self.assertEqual(consulta.status_code, 200)
        self.assertEqual(cadastro.status_code, 403)

    def test_gerente_pode_executar_acoes_operacionais(self):
        self.client.force_login(self.gerente)

        self.assertEqual(
            self.client.get(reverse("produtos:novo_produto")).status_code,
            200,
        )
        self.assertEqual(
            self.client.get(reverse("estoque:nova_entrada")).status_code,
            200,
        )
        self.assertEqual(
            self.client.get(reverse("catalogo:nova_marca")).status_code,
            200,
        )

    def test_rota_de_modulo_sem_decorator_exige_login(self):
        response = self.client.get(
            reverse("comercial:vincular_cliente", args=[999999])
        )

        self.assertRedirects(
            response,
            f'{reverse("login")}?next='
            f'{reverse("comercial:vincular_cliente", args=[999999])}',
        )

    def test_financeiro_nao_acessa_vendas_por_url_direta(self):
        self.client.force_login(self.financeiro)

        response = self.client.get(reverse("vendas:lista"))

        self.assertRedirects(response, reverse("dashboard"))

    def test_financeiro_acessa_central_de_relatorios(self):
        self.client.force_login(self.financeiro)

        response = self.client.get(
            reverse("central_relatorios")
        )

        self.assertEqual(response.status_code, 200)

    def test_sidebar_do_vendedor_exibe_apenas_dominios_permitidos(self):
        self.client.force_login(self.vendedor)

        response = self.client.get(reverse("dashboard"))
        sidebar = response.content.decode().split(
            '<nav class="menu"', 1
        )[1].split("</nav>", 1)[0]

        self.assertIn(reverse("vendas:nova"), sidebar)
        self.assertIn(reverse("estoque:dashboard_estoque"), sidebar)
        self.assertNotIn(reverse("compras:lista"), sidebar)
        self.assertNotIn(reverse("financeiro:dashboard"), sidebar)
        self.assertNotIn(reverse("usuarios:lista_usuarios"), sidebar)

    def test_sidebar_do_financeiro_oculta_comercial_e_operacao(self):
        self.client.force_login(self.financeiro)

        response = self.client.get(reverse("dashboard"))
        sidebar = response.content.decode().split(
            '<nav class="menu"', 1
        )[1].split("</nav>", 1)[0]

        self.assertIn(reverse("financeiro:dashboard"), sidebar)
        self.assertIn(reverse("central_relatorios"), sidebar)
        self.assertNotIn(reverse("vendas:nova"), sidebar)
        self.assertNotIn(reverse("estoque:dashboard_estoque"), sidebar)
        self.assertNotIn(reverse("compras:lista"), sidebar)


class AcoesUsuarioTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Usuario = get_user_model()
        cls.administrador = Usuario.objects.create_superuser(
            username="acoes-administrador",
            password="senha-segura",
            perfil=Usuario.Perfil.ADMINISTRADOR,
        )
        cls.usuario = Usuario.objects.create_user(
            username="acoes-usuario",
            password="senha-segura",
            perfil=Usuario.Perfil.VENDEDOR,
        )

    def setUp(self):
        self.client.force_login(self.administrador)

    def test_get_nao_inativa_usuario(self):
        response = self.client.get(
            reverse(
                "usuarios:inativar_usuario",
                args=[self.usuario.pk],
            )
        )

        self.assertEqual(response.status_code, 405)
        self.usuario.refresh_from_db()
        self.assertTrue(self.usuario.is_active)

    def test_administrador_nao_inativa_a_si_mesmo(self):
        response = self.client.post(
            reverse(
                "usuarios:inativar_usuario",
                args=[self.administrador.pk],
            )
        )

        self.assertRedirects(
            response,
            reverse("usuarios:lista_usuarios"),
        )
        self.administrador.refresh_from_db()
        self.assertTrue(self.administrador.is_active)

    def test_post_inativa_outro_usuario(self):
        self.client.post(
            reverse(
                "usuarios:inativar_usuario",
                args=[self.usuario.pk],
            )
        )

        self.usuario.refresh_from_db()
        self.assertFalse(self.usuario.is_active)


@override_settings(LOGIN_MAX_TENTATIVAS=5, LOGIN_BLOQUEIO_SEGUNDOS=900)
class SegurancaLoginTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user(
            username="login-protegido",
            password="senha-correta-segura",
            perfil="VEN",
        )

    def _login(self, senha, *, ip="192.0.2.10"):
        return self.client.post(
            reverse("login"),
            {
                "username": self.usuario.username,
                "password": senha,
            },
            REMOTE_ADDR=ip,
            HTTP_USER_AGENT="Navegador de teste",
        )

    def test_bloqueia_depois_de_cinco_falhas_no_mesmo_usuario_e_ip(self):
        for _ in range(5):
            resposta = self._login("senha-incorreta")
            self.assertEqual(resposta.status_code, 200)

        controle = ControleTentativaLogin.objects.get(
            username=self.usuario.username,
            endereco_ip="192.0.2.10",
        )
        self.assertEqual(controle.falhas, 5)
        self.assertGreater(controle.bloqueado_ate, timezone.now())

        resposta = self._login("senha-correta-segura")
        self.assertEqual(resposta.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertEqual(
            EventoLogin.objects.filter(
                resultado=EventoLogin.BLOQUEADO
            ).count(),
            1,
        )

    def test_bloqueio_nao_revela_se_usuario_ou_senha_estao_incorretos(self):
        resposta = self.client.post(
            reverse("login"),
            {"username": "usuario-inexistente", "password": "qualquer"},
            REMOTE_ADDR="192.0.2.20",
        )

        self.assertContains(
            resposta,
            "Usuário ou senha inválidos. Verifique os dados e tente novamente.",
        )

    def test_outro_ip_nao_herda_o_bloqueio(self):
        for _ in range(5):
            self._login("senha-incorreta", ip="192.0.2.30")

        resposta = self._login("senha-correta-segura", ip="192.0.2.31")

        self.assertRedirects(resposta, reverse("selecionar_operacao"))

    def test_login_correto_apos_expiracao_zerar_contador(self):
        for _ in range(5):
            self._login("senha-incorreta", ip="192.0.2.40")

        ControleTentativaLogin.objects.filter(
            username=self.usuario.username,
            endereco_ip="192.0.2.40",
        ).update(bloqueado_ate=timezone.now() - timedelta(seconds=1))

        resposta = self._login("senha-correta-segura", ip="192.0.2.40")

        self.assertRedirects(resposta, reverse("selecionar_operacao"))
        controle = ControleTentativaLogin.objects.get(
            username=self.usuario.username,
            endereco_ip="192.0.2.40",
        )
        self.assertEqual(controle.falhas, 0)
        self.assertIsNone(controle.bloqueado_ate)
        self.assertTrue(
            EventoLogin.objects.filter(
                resultado=EventoLogin.SUCESSO,
                usuario=self.usuario,
            ).exists()
        )

class PrimeiroAcessoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Usuario = get_user_model()
        cls.usuario = Usuario.objects.create_user(
            username="primeiro-acesso",
            password="senha-temporaria-segura",
            primeiro_acesso=True,
        )

    def setUp(self):
        self.client.force_login(self.usuario)

    def test_usuario_e_redirecionado_ate_definir_nova_senha(self):
        response = self.client.get(reverse("dashboard"))

        self.assertRedirects(
            response,
            reverse("usuarios:primeiro_acesso"),
        )

    def test_alteracao_de_senha_libera_o_acesso(self):
        response = self.client.post(
            reverse("usuarios:primeiro_acesso"),
            {
                "old_password": "senha-temporaria-segura",
                "new_password1": "nova-senha-muito-segura-2026",
                "new_password2": "nova-senha-muito-segura-2026",
            },
        )

        self.assertRedirects(response, reverse("selecionar_operacao"))
        self.usuario.refresh_from_db()
        self.assertFalse(self.usuario.primeiro_acesso)
        self.assertTrue(
            self.usuario.check_password(
                "nova-senha-muito-segura-2026"
            )
        )

    def test_cadastro_pelo_erp_exige_primeiro_acesso(self):
        form = UsuarioForm(
            data={
                "username": "novo-primeiro-acesso",
                "first_name": "Novo",
                "last_name": "Usuário",
                "email": "novo@teste.com",
                "telefone": "",
                "perfil": get_user_model().Perfil.VENDEDOR,
                "is_active": "on",
                "senha": "senha-temporaria-forte",
                "confirmar_senha": "senha-temporaria-forte",
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        usuario = form.save()
        self.assertTrue(usuario.primeiro_acesso)
