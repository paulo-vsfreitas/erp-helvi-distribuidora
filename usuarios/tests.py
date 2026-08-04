from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from usuarios.forms import UsuarioForm


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
        self.assertContains(response, "css/usuarios.css")
        self.assertContains(response, "js/usuarios/form_usuario.js")

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

    def test_vendedor_nao_acessa_financeiro_por_url_direta(self):
        self.client.force_login(self.vendedor)

        response = self.client.get(
            reverse("financeiro:dashboard")
        )

        self.assertRedirects(response, reverse("dashboard"))

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

        self.assertRedirects(response, reverse("dashboard"))
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
