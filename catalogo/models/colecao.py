from django.db import models


class Colecao(models.Model):

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
        default=True
    )

    data_cadastro = models.DateTimeField(
        auto_now_add=True
    )

    data_atualizacao = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "Coleção"
        verbose_name_plural = "Coleções"
        ordering = ["nome"]

    def __str__(self):
        return self.nome