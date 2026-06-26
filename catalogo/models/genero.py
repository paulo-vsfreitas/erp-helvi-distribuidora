from django.db import models


class Genero(models.Model):
    nome = models.CharField(
        max_length=50,
        unique=True
    )

    descricao = models.TextField(
        blank=True,
        null=True
    )

    ativo = models.BooleanField(
        default=True
    )

    data_cadastro = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = "Gênero"
        verbose_name_plural = "Gêneros"
        ordering = ["nome"]

    def __str__(self):
        return self.nome