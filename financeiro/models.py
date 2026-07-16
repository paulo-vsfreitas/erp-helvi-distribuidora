from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone

from core.base.models import CadastroBase


class CategoriaFinanceira(CadastroBase):
    TIPO_RECEITA = "receita"
    TIPO_DESPESA = "despesa"

    TIPO_CHOICES = [
        (TIPO_RECEITA, "Receita"),
        (TIPO_DESPESA, "Despesa"),
    ]

    tipo = models.CharField(
        "Tipo",
        max_length=10,
        choices=TIPO_CHOICES,
        default=TIPO_DESPESA,
    )

    class Meta:
        verbose_name = "Categoria financeira"
        verbose_name_plural = "Categorias financeiras"
        ordering = ["tipo", "nome"]
        constraints = [
            models.UniqueConstraint(
                fields=["nome", "tipo"],
                name="financeiro_categoria_nome_tipo_unicos",
            ),
        ]

    def __str__(self):
        return f"{self.nome} — {self.get_tipo_display()}"


class ContaFinanceira(models.Model):
    TIPO_CAIXA = "caixa"
    TIPO_CONTA_CORRENTE = "conta_corrente"
    TIPO_CONTA_POUPANCA = "conta_poupanca"
    TIPO_CARTEIRA_DIGITAL = "carteira_digital"
    TIPO_ADQUIRENTE = "adquirente"
    TIPO_INVESTIMENTO = "investimento"
    TIPO_OUTRA = "outra"

    TIPO_CHOICES = [
        (TIPO_CAIXA, "Caixa"),
        (TIPO_CONTA_CORRENTE, "Conta corrente"),
        (TIPO_CONTA_POUPANCA, "Conta poupança"),
        (TIPO_CARTEIRA_DIGITAL, "Carteira digital"),
        (TIPO_ADQUIRENTE, "Adquirente"),
        (TIPO_INVESTIMENTO, "Investimento"),
        (TIPO_OUTRA, "Outra"),
    ]

    nome = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nome",
    )

    tipo = models.CharField(
        max_length=30,
        choices=TIPO_CHOICES,
        default=TIPO_CONTA_CORRENTE,
        verbose_name="Tipo",
    )

    instituicao = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Instituição",
    )

    agencia = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Agência",
    )

    numero_conta = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Número da conta",
    )

    identificador = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Identificador",
        help_text=(
            "Chave Pix, código da carteira, terminal, "
            "apelido ou outro identificador."
        ),
    )

    saldo_inicial = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Saldo inicial",
    )

    data_saldo_inicial = models.DateField(
        default=timezone.localdate,
        verbose_name="Data do saldo inicial",
    )

    conta_padrao = models.BooleanField(
        default=False,
        verbose_name="Conta padrão",
    )

    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativa",
    )

    observacoes = models.TextField(
        blank=True,
        verbose_name="Observações",
    )

    data_cadastro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de cadastro",
    )

    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Data de atualização",
    )

    class Meta:
        verbose_name = "Conta financeira"
        verbose_name_plural = "Contas financeiras"
        ordering = ["-conta_padrao", "nome"]

    def __str__(self):
        return self.nome

    @property
    def saldo_atual(self):
        totais = self.movimentacoes.filter(
            estornada=False,
        ).aggregate(
            entradas=models.Sum(
                "valor",
                filter=Q(
                    tipo__in=[
                        MovimentacaoFinanceira.TIPO_ENTRADA,
                        MovimentacaoFinanceira.TIPO_ESTORNO_SAIDA,
                    ]
                ),
            ),
            saidas=models.Sum(
                "valor",
                filter=Q(
                    tipo__in=[
                        MovimentacaoFinanceira.TIPO_SAIDA,
                        MovimentacaoFinanceira.TIPO_ESTORNO_ENTRADA,
                    ]
                ),
            ),
        )

        entradas = totais["entradas"] or Decimal("0.00")
        saidas = totais["saidas"] or Decimal("0.00")

        return self.saldo_inicial + entradas - saidas


class ContaPagar(models.Model):
    STATUS_PENDENTE = "pendente"
    STATUS_PARCIAL = "parcial"
    STATUS_PAGA = "paga"
    STATUS_CANCELADA = "cancelada"

    STATUS_CHOICES = [
        (STATUS_PENDENTE, "Pendente"),
        (STATUS_PARCIAL, "Parcial"),
        (STATUS_PAGA, "Paga"),
        (STATUS_CANCELADA, "Cancelada"),
    ]

    numero = models.PositiveIntegerField(
        unique=True,
        editable=False,
        verbose_name="Número",
    )

    descricao = models.CharField(
        max_length=200,
        verbose_name="Descrição",
    )

    fornecedor = models.ForeignKey(
        "fornecedores.Fornecedor",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="contas_pagar",
        verbose_name="Fornecedor",
    )

    compra = models.OneToOneField(
        "compras.Compra",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="conta_pagar",
        verbose_name="Compra de origem",
    )

    categoria = models.ForeignKey(
        CategoriaFinanceira,
        on_delete=models.PROTECT,
        related_name="contas_pagar",
        limit_choices_to={"tipo": CategoriaFinanceira.TIPO_DESPESA},
        verbose_name="Categoria",
    )

    data_emissao = models.DateField(
        default=timezone.localdate,
        verbose_name="Data de emissão",
    )

    data_competencia = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de competência",
    )

    valor_total = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="Valor total",
    )

    valor_pago = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Valor pago",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDENTE,
        verbose_name="Status",
    )

    observacoes = models.TextField(
        blank=True,
        verbose_name="Observações",
    )

    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="contas_pagar_criadas",
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

    cancelado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="contas_pagar_canceladas",
        verbose_name="Cancelado por",
    )

    cancelado_em = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Cancelado em",
    )

    motivo_cancelamento = models.TextField(
        blank=True,
        verbose_name="Motivo do cancelamento",
    )

    class Meta:
        verbose_name = "Conta a pagar"
        verbose_name_plural = "Contas a pagar"
        ordering = ["-data_emissao", "-numero"]
        constraints = [
            models.CheckConstraint(
                condition=Q(valor_total__gt=0),
                name="financeiro_conta_pagar_valor_total_positivo",
            ),
            models.CheckConstraint(
                condition=Q(valor_pago__gte=0),
                name="financeiro_conta_pagar_valor_pago_nao_negativo",
            ),
            models.CheckConstraint(
                condition=Q(valor_pago__lte=models.F("valor_total")),
                name="financeiro_conta_pagar_pago_nao_supera_total",
            ),
        ]

    def __str__(self):
        return f"Conta #{self.numero} — {self.descricao}"

    def save(self, *args, **kwargs):
        if not self.numero:
            ultima_conta = ContaPagar.objects.order_by("-numero").first()
            self.numero = (ultima_conta.numero + 1) if ultima_conta else 1

        self.atualizar_status()
        super().save(*args, **kwargs)

    @property
    def saldo(self):
        return max(
            self.valor_total - self.valor_pago,
            Decimal("0.00"),
        )

    @property
    def esta_paga(self):
        return self.status == self.STATUS_PAGA

    @property
    def esta_cancelada(self):
        return self.status == self.STATUS_CANCELADA

    @property
    def possui_parcela_vencida(self):
        hoje = timezone.localdate()

        return self.parcelas.filter(
            data_vencimento__lt=hoje,
            status__in=[
                ParcelaPagar.STATUS_PENDENTE,
                ParcelaPagar.STATUS_PARCIAL,
            ],
        ).exists()

    def atualizar_status(self):
        if self.status == self.STATUS_CANCELADA:
            return

        if self.valor_pago <= 0:
            self.status = self.STATUS_PENDENTE
        elif self.valor_pago < self.valor_total:
            self.status = self.STATUS_PARCIAL
        else:
            self.status = self.STATUS_PAGA


class HistoricoContaPagar(models.Model):
    EVENTO_CRIACAO = "criacao"
    EVENTO_EDICAO = "edicao"
    EVENTO_PARCELA_CRIADA = "parcela_criada"
    EVENTO_PARCELA_EDITADA = "parcela_editada"
    EVENTO_BAIXA = "baixa"
    EVENTO_ESTORNO = "estorno"
    EVENTO_CANCELAMENTO = "cancelamento"
    EVENTO_REATIVACAO = "reativacao"
    EVENTO_INTEGRACAO_COMPRA = "integracao_compra"
    EVENTO_OUTRO = "outro"

    EVENTO_CHOICES = [
        (EVENTO_CRIACAO, "Criação"),
        (EVENTO_EDICAO, "Edição"),
        (EVENTO_PARCELA_CRIADA, "Parcela criada"),
        (EVENTO_PARCELA_EDITADA, "Parcela editada"),
        (EVENTO_BAIXA, "Baixa registrada"),
        (EVENTO_ESTORNO, "Baixa estornada"),
        (EVENTO_CANCELAMENTO, "Cancelamento"),
        (EVENTO_REATIVACAO, "Reativação"),
        (EVENTO_INTEGRACAO_COMPRA, "Integração com compra"),
        (EVENTO_OUTRO, "Outro"),
    ]

    conta_pagar = models.ForeignKey(
        ContaPagar,
        on_delete=models.CASCADE,
        related_name="historicos",
        verbose_name="Conta a pagar",
    )

    tipo_evento = models.CharField(
        max_length=30,
        choices=EVENTO_CHOICES,
        verbose_name="Tipo de evento",
    )

    descricao = models.TextField(
        verbose_name="Descrição",
    )

    dados = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Dados do evento",
    )

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="historicos_contas_pagar",
        verbose_name="Usuário",
    )

    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em",
    )

    class Meta:
        verbose_name = "Histórico da conta a pagar"
        verbose_name_plural = "Históricos das contas a pagar"
        ordering = ["-criado_em", "-id"]
        indexes = [
            models.Index(
                fields=["conta_pagar", "-criado_em"],
                name="fin_hist_conta_data_idx",
            ),
            models.Index(
                fields=["tipo_evento"],
                name="fin_hist_evento_idx",
            ),
        ]

    def __str__(self):
        return (
            f"Conta #{self.conta_pagar.numero} — "
            f"{self.get_tipo_evento_display()}"
        )

class ParcelaPagar(models.Model):
    STATUS_PENDENTE = "pendente"
    STATUS_PARCIAL = "parcial"
    STATUS_PAGA = "paga"
    STATUS_CANCELADA = "cancelada"

    STATUS_CHOICES = [
        (STATUS_PENDENTE, "Pendente"),
        (STATUS_PARCIAL, "Parcial"),
        (STATUS_PAGA, "Paga"),
        (STATUS_CANCELADA, "Cancelada"),
    ]

    conta_pagar = models.ForeignKey(
        ContaPagar,
        on_delete=models.CASCADE,
        related_name="parcelas",
        verbose_name="Conta a pagar",
    )

    numero = models.PositiveIntegerField(
        verbose_name="Número da parcela",
    )

    data_vencimento = models.DateField(
        verbose_name="Data de vencimento",
    )

    valor_original = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="Valor original",
    )

    valor_pago = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Valor pago",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDENTE,
        verbose_name="Status",
    )

    observacoes = models.TextField(
        blank=True,
        verbose_name="Observações",
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
        verbose_name = "Parcela a pagar"
        verbose_name_plural = "Parcelas a pagar"
        ordering = ["data_vencimento", "numero"]
        constraints = [
            models.UniqueConstraint(
                fields=["conta_pagar", "numero"],
                name="financeiro_parcela_numero_unico_por_conta",
            ),
            models.CheckConstraint(
                condition=Q(valor_original__gt=0),
                name="financeiro_parcela_valor_original_positivo",
            ),
            models.CheckConstraint(
                condition=Q(valor_pago__gte=0),
                name="financeiro_parcela_valor_pago_nao_negativo",
            ),
            models.CheckConstraint(
                condition=Q(valor_pago__lte=models.F("valor_original")),
                name="financeiro_parcela_pago_nao_supera_original",
            ),
        ]

    def __str__(self):
        return (
            f"Conta #{self.conta_pagar.numero} — "
            f"Parcela {self.numero}"
        )

    def save(self, *args, **kwargs):
        self.atualizar_status()
        super().save(*args, **kwargs)

    @property
    def saldo(self):
        return max(
            self.valor_original - self.valor_pago,
            Decimal("0.00"),
        )

    @property
    def esta_vencida(self):
        return (
            self.status
            in [
                self.STATUS_PENDENTE,
                self.STATUS_PARCIAL,
            ]
            and self.data_vencimento < timezone.localdate()
        )

    @property
    def vence_hoje(self):
        return (
            self.status
            in [
                self.STATUS_PENDENTE,
                self.STATUS_PARCIAL,
            ]
            and self.data_vencimento == timezone.localdate()
        )

    def atualizar_status(self):
        if self.status == self.STATUS_CANCELADA:
            return

        if self.valor_pago <= 0:
            self.status = self.STATUS_PENDENTE
        elif self.valor_pago < self.valor_original:
            self.status = self.STATUS_PARCIAL
        else:
            self.status = self.STATUS_PAGA


class BaixaPagar(models.Model):
    FORMA_PIX = "pix"
    FORMA_DINHEIRO = "dinheiro"
    FORMA_CARTAO = "cartao"
    FORMA_BOLETO = "boleto"
    FORMA_TRANSFERENCIA = "transferencia"
    FORMA_OUTRA = "outra"

    FORMA_CHOICES = [
        (FORMA_PIX, "Pix"),
        (FORMA_DINHEIRO, "Dinheiro"),
        (FORMA_CARTAO, "Cartão"),
        (FORMA_BOLETO, "Boleto"),
        (FORMA_TRANSFERENCIA, "Transferência"),
        (FORMA_OUTRA, "Outra"),
    ]

    parcela = models.ForeignKey(
        ParcelaPagar,
        on_delete=models.PROTECT,
        related_name="baixas",
        verbose_name="Parcela",
    )

    conta_financeira = models.ForeignKey(
        ContaFinanceira,
        on_delete=models.PROTECT,
        related_name="baixas_pagar",
        verbose_name="Conta financeira",
    )

    data_pagamento = models.DateField(
        default=timezone.localdate,
        verbose_name="Data do pagamento",
    )

    valor = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="Valor principal",
    )

    juros = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Juros",
    )

    multa = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Multa",
    )

    desconto = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Desconto financeiro",
    )

    valor_movimentado = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        editable=False,
        verbose_name="Valor movimentado",
    )

    forma_pagamento = models.CharField(
        max_length=30,
        choices=FORMA_CHOICES,
        default=FORMA_PIX,
        verbose_name="Forma de pagamento",
    )

    observacao = models.TextField(
        blank=True,
        verbose_name="Observação",
    )

    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="baixas_pagar_registradas",
        verbose_name="Registrado por",
    )

    registrado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Registrado em",
    )

    estornada = models.BooleanField(
        default=False,
        verbose_name="Estornada",
    )

    estornada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="baixas_pagar_estornadas",
        verbose_name="Estornada por",
    )

    estornada_em = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Estornada em",
    )

    motivo_estorno = models.TextField(
        blank=True,
        verbose_name="Motivo do estorno",
    )

    class Meta:
        verbose_name = "Baixa de conta a pagar"
        verbose_name_plural = "Baixas de contas a pagar"
        ordering = ["-data_pagamento", "-registrado_em"]
        constraints = [
            models.CheckConstraint(
                condition=Q(valor__gt=0),
                name="financeiro_baixa_valor_positivo",
            ),
            models.CheckConstraint(
                condition=Q(juros__gte=0),
                name="financeiro_baixa_juros_nao_negativo",
            ),
            models.CheckConstraint(
                condition=Q(multa__gte=0),
                name="financeiro_baixa_multa_nao_negativa",
            ),
            models.CheckConstraint(
                condition=Q(desconto__gte=0),
                name="financeiro_baixa_desconto_nao_negativo",
            ),
        ]

    def __str__(self):
        return (
            f"Baixa da conta #{self.parcela.conta_pagar.numero} — "
            f"R$ {self.valor_movimentado}"
        )

    def save(self, *args, **kwargs):
        self.valor_movimentado = (
            self.valor
            + self.juros
            + self.multa
            - self.desconto
        )

        super().save(*args, **kwargs)


class MovimentacaoFinanceira(models.Model):
    TIPO_ENTRADA = "entrada"
    TIPO_SAIDA = "saida"
    TIPO_ESTORNO_ENTRADA = "estorno_entrada"
    TIPO_ESTORNO_SAIDA = "estorno_saida"
    TIPO_AJUSTE = "ajuste"

    TIPO_CHOICES = [
        (TIPO_ENTRADA, "Entrada"),
        (TIPO_SAIDA, "Saída"),
        (TIPO_ESTORNO_ENTRADA, "Estorno de entrada"),
        (TIPO_ESTORNO_SAIDA, "Estorno de saída"),
        (TIPO_AJUSTE, "Ajuste"),
    ]

    conta_financeira = models.ForeignKey(
        ContaFinanceira,
        on_delete=models.PROTECT,
        related_name="movimentacoes",
        verbose_name="Conta financeira",
    )

    categoria = models.ForeignKey(
        CategoriaFinanceira,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="movimentacoes",
        verbose_name="Categoria",
    )

    baixa_pagar = models.ForeignKey(
        BaixaPagar,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="movimentacoes",
        verbose_name="Baixa de origem",
    )

    tipo = models.CharField(
        max_length=30,
        choices=TIPO_CHOICES,
        verbose_name="Tipo",
    )

    data_movimentacao = models.DateField(
        default=timezone.localdate,
        verbose_name="Data da movimentação",
    )

    valor = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="Valor",
    )

    descricao = models.CharField(
        max_length=255,
        verbose_name="Descrição",
    )

    origem = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Origem",
    )

    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="movimentacoes_financeiras_criadas",
        verbose_name="Criado por",
    )

    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em",
    )

    estornada = models.BooleanField(
        default=False,
        verbose_name="Estornada",
    )

    class Meta:
        verbose_name = "Movimentação financeira"
        verbose_name_plural = "Movimentações financeiras"
        ordering = ["-data_movimentacao", "-criado_em"]
        constraints = [
            models.CheckConstraint(
                condition=Q(valor__gt=0),
                name="financeiro_movimentacao_valor_positivo",
            ),
        ]

    def __str__(self):
        return (
            f"{self.get_tipo_display()} — "
            f"{self.conta_financeira} — "
            f"R$ {self.valor}"
        )