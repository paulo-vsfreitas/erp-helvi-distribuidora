from django.db import models


class TipoArmacao(models.Model):
    nome = models.CharField(
        max_length=100,
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
        verbose_name = "Tipo de Armação"
        verbose_name_plural = "Tipos de Armação"
        ordering = ["nome"]

    def __str__(self):
        return self.nome