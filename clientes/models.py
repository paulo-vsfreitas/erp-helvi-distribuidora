from django.db import models


class Cliente(models.Model):
    razao_social = models.CharField(max_length=200, verbose_name="Razão Social")
    nome_fantasia = models.CharField(max_length=200, verbose_name="Nome Fantasia")
    cnpj = models.CharField(max_length=18, unique=True, blank=True, null=True)

    responsavel = models.CharField(max_length=150, blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    whatsapp = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    cidade = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=2, blank=True, null=True)
    endereco = models.CharField(max_length=250, blank=True, null=True)

    limite_credito = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Limite de Crédito"
    )

    condicao_pagamento = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Condição de Pagamento"
    )

    observacoes = models.TextField(blank=True, null=True)
    ativo = models.BooleanField(default=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Cliente / Ótica"
        verbose_name_plural = "Clientes / Óticas"

    def __str__(self):
        return self.nome_fantasia