from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from clientes.models import Cliente
from produtos.models import Produto


class Venda(models.Model):
    STATUS_EM_ABERTO = "aberta"
    STATUS_FINALIZADA = "finalizada"
    STATUS_CANCELADA = "cancelada"

    STATUS_CHOICES = [
        (STATUS_EM_ABERTO, "Em aberto"),
        (STATUS_FINALIZADA, "Finalizada"),
        (STATUS_CANCELADA, "Cancelada"),
    ]

    PAGAMENTO_PENDENTE = "pendente"
    PAGAMENTO_PARCIAL = "parcial"
    PAGAMENTO_PAGO = "pago"

    STATUS_PAGAMENTO_CHOICES = [
        (PAGAMENTO_PENDENTE, "Pendente"),
        (PAGAMENTO_PARCIAL, "Parcial"),
        (PAGAMENTO_PAGO, "Pago"),
    ]

    FORMA_PIX = "pix"
    FORMA_DINHEIRO = "dinheiro"
    FORMA_CARTAO_DEBITO = "cartao_debito"
    FORMA_CARTAO_CREDITO = "cartao_credito"
    FORMA_TRANSFERENCIA = "transferencia"
    FORMA_BOLETO = "boleto"
    FORMA_PRAZO = "prazo"

    FORMA_PAGAMENTO_CHOICES = [
        (FORMA_PIX, "Pix"),
        (FORMA_DINHEIRO, "Dinheiro"),
        (FORMA_CARTAO_DEBITO, "Cartão de Débito"),
        (FORMA_CARTAO_CREDITO, "Cartão de Crédito"),
        (FORMA_TRANSFERENCIA, "Transferência"),
        (FORMA_BOLETO, "Boleto"),
        (FORMA_PRAZO, "A Prazo"),
    ]

    numero = models.PositiveIntegerField(
        unique=True,
        editable=False,
        blank=True,
        null=True,
        verbose_name="Número",
    )

    cliente = models.ForeignKey(
        "clientes.Cliente",
        on_delete=models.PROTECT,
        related_name="vendas",
        null=True,
        blank=True,
    )

    data_venda = models.DateTimeField(
        auto_now_add=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_EM_ABERTO,
    )

    status_pagamento = models.CharField(
        max_length=20,
        choices=STATUS_PAGAMENTO_CHOICES,
        default=PAGAMENTO_PENDENTE,
    )

    forma_pagamento = models.CharField(
        max_length=20,
        choices=FORMA_PAGAMENTO_CHOICES,
        blank=True,
        null=True,
    )

    conta_financeira = models.ForeignKey(
    "financeiro.ContaFinanceira",
    on_delete=models.PROTECT,
    null=True,
    blank=True,
    related_name="vendas",
    )

    valor_entrada = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    valor_troco = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    quantidade_parcelas = models.PositiveIntegerField(
        default=1,
    )

    primeiro_vencimento = models.DateField(
        null=True,
        blank=True,
    )

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    desconto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    frete = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    valor_recebido = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    observacoes = models.TextField(
        blank=True,
        null=True,
    )

    estoque_baixado = models.BooleanField(
        default=False,
    )

    financeiro_gerado = models.BooleanField(
        default=False,
    )

    criada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="vendas_criadas",
        blank=True,
        null=True,
    )

    finalizada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="vendas_finalizadas",
        blank=True,
        null=True,
    )

    finalizada_em = models.DateTimeField(
        blank=True,
        null=True,
    )

    cancelada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="vendas_canceladas",
        blank=True,
        null=True,
    )

    cancelada_em = models.DateTimeField(
        blank=True,
        null=True,
    )

    motivo_cancelamento = models.TextField(
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Venda"
        verbose_name_plural = "Vendas"
        ordering = ["-data_venda", "-id"]

    def __str__(self):
        identificador = self.numero or self.pk
        cliente = self.cliente or "Consumidor Final"

        return f"Venda #{identificador} - {cliente}"

    @property
    def saldo_receber(self):
        saldo = self.total - self.valor_recebido
        return max(saldo, Decimal("0.00"))

    @property
    def quantidade_itens(self):
        return self.itens.count()

    @property
    def quantidade_pecas(self):
        return sum(item.quantidade for item in self.itens.all())

class SequenciaDocumento(models.Model):
    TIPO_VENDA = "venda"
    TIPO_COMPRA = "compra"
    TIPO_ORCAMENTO = "orcamento"

    TIPO_CHOICES = [
        (TIPO_VENDA, "Venda"),
        (TIPO_COMPRA, "Compra"),
        (TIPO_ORCAMENTO, "Orçamento"),
    ]

    tipo = models.CharField(
        max_length=30,
        unique=True,
        choices=TIPO_CHOICES,
        verbose_name="Tipo de documento",
    )

    ultimo_numero = models.PositiveIntegerField(
        default=0,
        verbose_name="Último número utilizado",
    )

    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em",
    )

    class Meta:
        verbose_name = "Sequência de documento"
        verbose_name_plural = "Sequências de documentos"
        ordering = ["tipo"]

    def __str__(self):
        return f"{self.get_tipo_display()}: {self.ultimo_numero}"


class ItemVenda(models.Model):
    venda = models.ForeignKey(
        Venda,
        on_delete=models.CASCADE,
        related_name="itens",
    )

    produto = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT,
        related_name="itens_venda",
    )

    quantidade = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
    )

    preco_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )

    desconto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    class Meta:
        verbose_name = "Item da Venda"
        verbose_name_plural = "Itens da Venda"
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["venda", "produto"],
                name="venda_produto_unico",
            ),
        ]

    def __str__(self):
        return f"{self.produto} x {self.quantidade}"

    def calcular_total(self):
        bruto = self.preco_unitario * self.quantidade
        return max(bruto - self.desconto, Decimal("0.00"))