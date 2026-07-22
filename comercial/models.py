from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from clientes.models import Cliente
from produtos.models import Produto


class Orcamento(models.Model):
    class Status(models.TextChoices):
        RASCUNHO = "rascunho", "Rascunho"
        ENVIADO = "enviado", "Enviado"
        APROVADO = "aprovado", "Aprovado"
        REJEITADO = "rejeitado", "Rejeitado"
        CANCELADO = "cancelado", "Cancelado"
        CONVERTIDO = "convertido", "Convertido em venda"

    numero = models.BigAutoField(
        primary_key=True,
        verbose_name="Número",
    )

    cliente = models.ForeignKey(
        "clientes.Cliente",
        on_delete=models.PROTECT,
        related_name="orcamentos",
        null=True,
        blank=True,
        verbose_name="Cliente cadastrado",
    )

    cliente_nome = models.CharField(
        max_length=150,
        verbose_name="Cliente / interessado",
    )

    cliente_documento = models.CharField(
        max_length=18,
        blank=True,
        verbose_name="CPF / CNPJ",
    )

    cliente_telefone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Telefone / WhatsApp",
    )

    cliente_email = models.EmailField(
        blank=True,
        verbose_name="E-mail",
    )

    vendedor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orcamentos_criados",
        verbose_name="Vendedor",
    )

    data_emissao = models.DateField(
        verbose_name="Data de emissão",
    )

    data_validade = models.DateField(
        verbose_name="Validade",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.RASCUNHO,
        db_index=True,
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

    condicoes_comerciais = models.TextField(
        blank=True,
        verbose_name="Condições comerciais",
    )

    observacoes = models.TextField(
        blank=True,
        verbose_name="Observações",
    )

    enviado_em = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Enviado em",
    )

    aprovado_em = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Aprovado em",
    )

    rejeitado_em = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Rejeitado em",
    )

    cancelado_em = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Cancelado em",
    )

    convertido_em = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Convertido em",
    )

    venda_gerada = models.OneToOneField(
        "vendas.Venda",
        on_delete=models.PROTECT,
        related_name="orcamento_origem",
        null=True,
        blank=True,
        verbose_name="Venda gerada",
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
        verbose_name = "Orçamento"
        verbose_name_plural = "Orçamentos"
        ordering = ["-numero"]
        indexes = [
            models.Index(
                fields=["cliente", "status"],
                name="orc_cliente_status_idx",
            ),
            models.Index(
                fields=["data_emissao"],
                name="orc_data_emissao_idx",
            ),
        ]

    def __str__(self):
        return f"{self.codigo} - {self.cliente}"

    @property
    def codigo(self):
        return f"ORC-{self.numero:06d}"

    @property
    def quantidade_itens(self):
        return self.itens.count()

    @property
    def quantidade_pecas(self):
        return sum(item.quantidade for item in self.itens.all())


class ItemOrcamento(models.Model):
    orcamento = models.ForeignKey(
        Orcamento,
        on_delete=models.CASCADE,
        related_name="itens",
        verbose_name="Orçamento",
    )

    produto = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT,
        related_name="itens_orcamento",
        verbose_name="Produto",
    )

    quantidade = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Quantidade",
    )

    valor_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="Valor unitário",
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

    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em",
    )

    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em",
    )

    class Meta:
        verbose_name = "Item do orçamento"
        verbose_name_plural = "Itens do orçamento"
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["orcamento", "produto"],
                name="orcamento_produto_unico",
            ),
        ]

    def __str__(self):
        return (
            f"{self.orcamento.codigo} — "
            f"{self.produto} × {self.quantidade}"
        )