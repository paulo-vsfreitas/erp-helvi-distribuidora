from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class Usuario(AbstractUser):

    class Perfil(models.TextChoices):
        ADMINISTRADOR = "ADM", "Administrador"
        GERENTE = "GER", "Gerente"
        VENDEDOR = "VEN", "Vendedor"
        FINANCEIRO = "FIN", "Financeiro"

    telefone = models.CharField(
        "Telefone",
        max_length=20,
        blank=True,
    )

    perfil = models.CharField(
        "Perfil",
        max_length=3,
        choices=Perfil.choices,
        default=Perfil.VENDEDOR,
    )

    primeiro_acesso = models.BooleanField(
        "Primeiro acesso",
        default=False,
    )

    foto = models.ImageField(
        "Foto",
        upload_to="usuarios/",
        blank=True,
        null=True,
    )

    groups = models.ManyToManyField(
        Group,
        verbose_name="grupos",
        blank=True,
        related_name="usuarios_set",
        related_query_name="usuario",
    )

    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name="permissões do usuário",
        blank=True,
        related_name="usuarios_set",
        related_query_name="usuario",
    )

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"

    @property
    def eh_administrador(self):
        return self.perfil == self.Perfil.ADMINISTRADOR

    @property
    def eh_gerente(self):
        return self.perfil == self.Perfil.GERENTE

    @property
    def eh_vendedor(self):
        return self.perfil == self.Perfil.VENDEDOR

    @property
    def eh_financeiro(self):
        return self.perfil == self.Perfil.FINANCEIRO
    def __str__(self):
        return self.get_full_name() or self.username


class ControleTentativaLogin(models.Model):
    username = models.CharField(max_length=150)
    endereco_ip = models.GenericIPAddressField()
    falhas = models.PositiveSmallIntegerField(default=0)
    bloqueado_ate = models.DateTimeField(blank=True, null=True)
    ultima_tentativa = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["username", "endereco_ip"],
                name="login_controle_usuario_ip_unico",
            ),
        ]
        indexes = [
            models.Index(
                fields=["bloqueado_ate"],
                name="login_bloqueado_ate_idx",
            ),
        ]


class EventoLogin(models.Model):
    SUCESSO = "sucesso"
    FALHA = "falha"
    BLOQUEADO = "bloqueado"
    RESULTADOS = [
        (SUCESSO, "Sucesso"),
        (FALHA, "Falha"),
        (BLOQUEADO, "Bloqueado"),
    ]

    username = models.CharField(max_length=150, db_index=True)
    endereco_ip = models.GenericIPAddressField()
    resultado = models.CharField(max_length=10, choices=RESULTADOS)
    usuario = models.ForeignKey(
        "usuarios.Usuario",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="eventos_login",
    )
    user_agent = models.CharField(max_length=300, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-criado_em", "-id"]
        indexes = [
            models.Index(
                fields=["endereco_ip", "criado_em"],
                name="login_ip_criado_idx",
            ),
        ]
