from django.db import models


class CadastroBase(models.Model):
    """
    Classe base para todos os cadastros simples do ERP Helvi.
    """

    nome = models.CharField(
        "Nome",
        max_length=50,
        unique=True,
    )

    descricao = models.TextField(
        "Descrição",
        blank=True,
    )

    ativo = models.BooleanField(
        "Ativo",
        default=True,
    )

    data_cadastro = models.DateTimeField(
        "Data de Cadastro",
        auto_now_add=True,
    )

    data_atualizacao = models.DateTimeField(
        "Data de Atualização",
        auto_now=True,
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.nome