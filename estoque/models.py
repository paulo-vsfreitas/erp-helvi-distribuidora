from django.conf import settings
from django.db import models

from produtos.models import Produto


class MovimentacaoEstoque(models.Model):
    TIPO_CHOICES = [
        ("entrada", "Entrada"),
        ("saida", "Saída"),
        ("ajuste_positivo", "Ajuste Positivo"),
        ("ajuste_negativo", "Ajuste Negativo"),
        ("inventario", "Inventário"),
        ("transferencia", "Transferência"),
        ("venda", "Venda"),
        ("compra", "Compra"),
        ("cancelamento_venda", "Cancelamento de Venda"),
        ("cancelamento_compra", "Cancelamento de Compra"),
    ]

    produto = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT,
        related_name="movimentacoes_estoque",
    )

    tipo = models.CharField(
        max_length=30,
        choices=TIPO_CHOICES,
    )

    quantidade = models.IntegerField()

    saldo_anterior = models.IntegerField()
    saldo_atual = models.IntegerField()

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="movimentacoes_estoque",
        blank=True,
        null=True,
    )

    origem = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    local = models.CharField(
        max_length=100,
        default="Estoque Principal",
    )

    observacao = models.TextField(
        blank=True,
        null=True,
    )

    data_movimentacao = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Movimentação de Estoque"
        verbose_name_plural = "Movimentações de Estoque"
        ordering = ["-data_movimentacao"]

    def __str__(self):
        return f"{self.produto} | {self.get_tipo_display()} | {self.quantidade}"


class Inventario(models.Model):
    STATUS_CHOICES = [
        ("em_andamento", "Em andamento"),
        ("finalizado", "Finalizado"),
        ("cancelado", "Cancelado"),
    ]

    codigo = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="em_andamento",
    )

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="inventarios_estoque",
    )

    observacao = models.TextField(
        blank=True,
        null=True,
    )

    data_criacao = models.DateTimeField(auto_now_add=True)
    data_finalizacao = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Inventário"
        verbose_name_plural = "Inventários"
        ordering = ["-data_criacao"]

    def __str__(self):
        return f"Inventário {self.codigo or self.pk}"


class InventarioItem(models.Model):
    inventario = models.ForeignKey(
        Inventario,
        on_delete=models.CASCADE,
        related_name="itens",
    )

    produto = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT,
        related_name="itens_inventario",
    )

    estoque_sistema = models.IntegerField()
    quantidade_fisica = models.IntegerField(blank=True, null=True)
    diferenca = models.IntegerField(default=0)

    ajustado = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Item de Inventário"
        verbose_name_plural = "Itens de Inventário"
        ordering = ["produto__modelo"]

    def __str__(self):
        return f"{self.inventario} | {self.produto}"