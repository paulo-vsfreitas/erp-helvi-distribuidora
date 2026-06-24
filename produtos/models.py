from django.db import models


class Produto(models.Model):
    GENERO_CHOICES = [
        ('unissex', 'Unissex'),
        ('masculino', 'Masculino'),
        ('feminino', 'Feminino'),
        ('infantil', 'Infantil'),
    ]

    codigo = models.CharField(max_length=50, unique=True, verbose_name="Código")
    marca = models.CharField(max_length=100, blank=True, null=True)
    modelo = models.CharField(max_length=100)
    cor = models.CharField(max_length=80, blank=True, null=True)
    material = models.CharField(max_length=100, blank=True, null=True)
    genero = models.CharField(max_length=20, choices=GENERO_CHOICES, default='unissex')

    preco_custo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    preco_venda = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    estoque_atual = models.IntegerField(default=0)
    estoque_minimo = models.IntegerField(default=0)

    ativo = models.BooleanField(default=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Produto / Armação"
        verbose_name_plural = "Produtos / Armações"

    def __str__(self):
        return f"{self.codigo} - {self.modelo} - {self.cor}"