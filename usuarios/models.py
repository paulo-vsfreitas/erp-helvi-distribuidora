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
        default=True,
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

    def __str__(self):
        return self.get_full_name() or self.username