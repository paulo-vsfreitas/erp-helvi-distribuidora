from decimal import Decimal

from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator


class Compra(models.Model):
    STATUS_RASCUNHO = "rascunho"
    STATUS_EM_ABERTO = "em_aberto"
    STATUS_AGUARDANDO_ENTREGA = "aguardando_entrega"
    STATUS_RECEBIDA = "recebida"
    STATUS_CANCELADA = "cancelada"

    STATUS_CHOICES = [
        (STATUS_RASCUNHO, "Rascunho"),
        (STATUS_EM_ABERTO, "Em aberto"),
        (STATUS_AGUARDANDO_ENTREGA, "Aguardando entrega"),
        (STATUS_RECEBIDA, "Recebida"),
        (STATUS_CANCELADA, "Cancelada"),
    ]

    STATUS_PAGAMENTO_PENDENTE = "pendente"
    STATUS_PAGAMENTO_PARCIAL = "parcial"
    STATUS_PAGAMENTO_PAGO = "pago"

    STATUS_PAGAMENTO_CHOICES = [
        (STATUS_PAGAMENTO_PENDENTE, "Pendente"),
        (STATUS_PAGAMENTO_PARCIAL, "Parcial"),
        (STATUS_PAGAMENTO_PAGO, "Pago"),
    ]
    status_pagamento = models.CharField(
    max_length=20,
    choices=STATUS_PAGAMENTO_CHOICES,
    default=STATUS_PAGAMENTO_PENDENTE,
    verbose_name="Status do pagamento",
    )

    numero = models.PositiveIntegerField(
        unique=True,
        editable=False,
        verbose_name="Número da compra",
    )

    fornecedor_nome = models.CharField(
        max_length=150,
        verbose_name="Fornecedor",
    )

    fornecedor_documento = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="CPF/CNPJ",
    )

    fornecedor_telefone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Telefone",
    )

    data_compra = models.DateField(
        verbose_name="Data da compra",
    )

    previsao_entrega = models.DateField(
        null=True,
        blank=True,
        verbose_name="Previsão de entrega",
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default=STATUS_RASCUNHO,
        verbose_name="Status",
    )

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Subtotal",
    )

    desconto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Desconto",
    )

    frete = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Frete",
    )

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Total",
    )

    observacoes = models.TextField(
        blank=True,
        verbose_name="Observações",
    )

    entrada_estoque_realizada = models.BooleanField(
        default=False,
        verbose_name="Entrada no estoque realizada",
    )

    financeiro_gerado = models.BooleanField(
        default=False,
        verbose_name="Financeiro gerado",
    )

    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="compras_criadas",
        verbose_name="Criado por",
    )

    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em",
    )

    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em",
    )

    class Meta:
        verbose_name = "Compra"
        verbose_name_plural = "Compras"
        ordering = ["-data_compra", "-id"]

    def __str__(self):
        return f"Compra #{self.numero} - {self.fornecedor_nome}"

    def save(self, *args, **kwargs):
        if not self.numero:
            ultima_compra = Compra.objects.order_by("-numero").first()
            self.numero = (ultima_compra.numero + 1) if ultima_compra else 1

        self.total = (self.subtotal - self.desconto) + self.frete

        super().save(*args, **kwargs)


class ItemCompra(models.Model):
    compra = models.ForeignKey(
        Compra,
        on_delete=models.CASCADE,
        related_name="itens",
        verbose_name="Compra",
    )

    produto = models.ForeignKey(
        "produtos.Produto",
        on_delete=models.PROTECT,
        related_name="itens_compra",
        verbose_name="Produto",
    )

    quantidade = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Quantidade",
    )

    custo_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="Custo unitário",
    )

    desconto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Desconto",
    )

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Total",
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Item da compra"
        verbose_name_plural = "Itens da compra"
        ordering = ["id"]

    def __str__(self):
        return f"{self.produto} - {self.quantidade} un."

    def save(self, *args, **kwargs):
        self.total = (self.quantidade * self.custo_unitario) - self.desconto
        super().save(*args, **kwargs)