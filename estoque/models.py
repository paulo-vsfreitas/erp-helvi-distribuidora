from django.db import models
from produtos.models import Produto


class MovimentacaoEstoque(models.Model):
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('saida', 'Saída'),
        ('ajuste', 'Ajuste'),
    ]

    MOTIVO_CHOICES = [
        ('compra', 'Compra'),
        ('venda', 'Venda'),
        ('devolucao', 'Devolução'),
        ('troca', 'Troca'),
        ('avaria', 'Avaria'),
        ('inventario', 'Inventário'),
        ('outro', 'Outro'),
    ]

    produto = models.ForeignKey(
        Produto,
        on_delete=models.CASCADE,
        related_name='movimentacoes'
    )

    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    motivo = models.CharField(max_length=20, choices=MOTIVO_CHOICES)
    quantidade = models.IntegerField()

    observacao = models.TextField(blank=True, null=True)
    data_movimentacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Movimentação de Estoque"
        verbose_name_plural = "Movimentações de Estoque"
        ordering = ['-data_movimentacao']

    def __str__(self):
        return f"{self.produto} | {self.tipo} | {self.quantidade}"