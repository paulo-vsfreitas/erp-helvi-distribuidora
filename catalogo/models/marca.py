from django.db import models


class Marca(models.Model):
    nome = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nome"
    )

    descricao = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descrição"
    )

    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )

    data_cadastro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Cadastro"
    )

    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Atualização"
    )

    class Meta:
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"
        ordering = ["nome"]

    def __str__(self):
        return self.nome