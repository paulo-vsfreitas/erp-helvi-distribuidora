from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.db.models import Q, Sum
from django.utils import timezone


class PessoaEquipe(models.Model):
    CONTATO_WHATSAPP = "whatsapp"
    CONTATO_TELEFONE = "telefone"
    CONTATO_EMAIL = "email"
    CONTATO_CHOICES = [
        (CONTATO_WHATSAPP, "WhatsApp"),
        (CONTATO_TELEFONE, "Telefone"),
        (CONTATO_EMAIL, "E-mail"),
    ]

    nome = models.CharField(max_length=120)
    tipo_contato = models.CharField(max_length=12, choices=CONTATO_CHOICES, default=CONTATO_WHATSAPP)
    contato = models.CharField(max_length=120, blank=True)
    cor_agenda = models.CharField(
        "Cor na agenda", max_length=7, default="#743f76",
        validators=[RegexValidator(r"^#[0-9A-Fa-f]{6}$", "Informe uma cor válida.")],
    )
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nome"]
        constraints = [
            models.UniqueConstraint(fields=["nome", "contato"], name="evento_pessoa_nome_contato_unicos")
        ]

    def __str__(self):
        return self.nome


class EquipeEvento(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    pessoas = models.ManyToManyField(PessoaEquipe, blank=True, related_name="equipes")
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Evento(models.Model):
    CONTATO_WHATSAPP = "whatsapp"
    CONTATO_TELEFONE = "telefone"
    CONTATO_EMAIL = "email"
    CONTATO_CHOICES = [
        (CONTATO_WHATSAPP, "WhatsApp"), (CONTATO_TELEFONE, "Telefone"),
        (CONTATO_EMAIL, "E-mail"),
    ]
    STATUS_PLANEJADO = "planejado"
    STATUS_CONFIRMADO = "confirmado"
    STATUS_PREPARACAO = "preparacao"
    STATUS_ANDAMENTO = "andamento"
    STATUS_CONCLUIDO = "concluido"
    STATUS_CANCELADO = "cancelado"
    STATUS_CHOICES = [
        (STATUS_PLANEJADO, "Planejado"),
        (STATUS_CONFIRMADO, "Confirmado"),
        (STATUS_PREPARACAO, "Em preparação"),
        (STATUS_ANDAMENTO, "Em andamento"),
        (STATUS_CONCLUIDO, "Concluído"),
        (STATUS_CANCELADO, "Cancelado"),
    ]

    nome = models.CharField("Nome do evento", max_length=160)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PLANEJADO)
    inicio = models.DateTimeField("Início")
    fim = models.DateTimeField("Término")
    local = models.CharField(max_length=160, blank=True)
    endereco = models.CharField("Endereço", max_length=255, blank=True)
    cidade = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=2, blank=True)
    publico_alvo = models.CharField("Público-alvo", max_length=160, blank=True)
    expectativa_publico = models.PositiveIntegerField("Expectativa de público", null=True, blank=True)
    responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="eventos_responsaveis"
    )
    contato_responsavel = models.CharField("Contato do responsável", max_length=120, blank=True)
    tipo_contato_responsavel = models.CharField(
        "Tipo de contato", max_length=12, choices=CONTATO_CHOICES,
        default=CONTATO_WHATSAPP, blank=True,
    )
    instagram = models.CharField("Instagram do organizador/local", max_length=80, blank=True)
    participantes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="eventos_participados"
    )
    equipe = models.ForeignKey(
        EquipeEvento, on_delete=models.PROTECT, null=True, blank=True,
        related_name="eventos", verbose_name="Equipe cadastrada",
    )
    pessoas_equipe = models.ManyToManyField(
        PessoaEquipe, blank=True, related_name="eventos", verbose_name="Pessoas cadastradas",
    )
    participantes_externos = models.TextField(
        "Outros participantes", blank=True,
        help_text="Informe um nome por linha quando a pessoa ainda não for usuária do ERP.",
    )
    organizador = models.CharField(max_length=160, blank=True)
    contato_organizador = models.CharField("Contato do organizador", max_length=100, blank=True)
    tipo_contato_organizador = models.CharField(
        "Tipo de contato do organizador", max_length=12, choices=CONTATO_CHOICES,
        default=CONTATO_WHATSAPP, blank=True,
    )
    observacoes = models.TextField("Observações", blank=True)
    lembrete_ativo = models.BooleanField("Exibir lembrete na agenda", default=False)
    lembrete_dias_antes = models.PositiveSmallIntegerField(
        "Avisar com quantos dias de antecedência", default=1,
        validators=[MaxValueValidator(365)],
    )
    lembrete_mensagem = models.CharField(
        "Mensagem do lembrete", max_length=240, blank=True,
        help_text="Se ficar vazio, o sistema usará uma mensagem automática.",
    )
    motivo_cancelamento = models.TextField("Motivo do cancelamento", blank=True)
    cancelado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True,
        related_name="eventos_cancelados",
    )
    cancelado_em = models.DateTimeField(null=True, blank=True)
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="eventos_criados"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["inicio", "nome"]
        indexes = [models.Index(fields=["inicio", "status"], name="evento_inicio_status_idx")]
        constraints = [
            models.CheckConstraint(condition=Q(fim__gte=models.F("inicio")), name="evento_fim_apos_inicio")
        ]

    def __str__(self):
        return self.nome

    @property
    def totais(self):
        vendas = self.vendas.exclude(status=VendaEvento.STATUS_CANCELADA).aggregate(
            vendido=Sum("valor_venda"), recebido=Sum("valor_recebido"), custo=Sum("custo_produtos")
        )
        despesas = self.despesas.exclude(conta_pagar__status="cancelada").aggregate(
            total=Sum("conta_pagar__valor_total"), pago=Sum("conta_pagar__valor_pago")
        )
        vendido = vendas["vendido"] or Decimal("0.00")
        recebido = vendas["recebido"] or Decimal("0.00")
        custo = vendas["custo"] or Decimal("0.00")
        gasto = despesas["total"] or Decimal("0.00")
        gasto_pago = despesas["pago"] or Decimal("0.00")
        lucro = vendido - custo - gasto
        margem = (lucro / vendido * Decimal("100")) if vendido else Decimal("0.00")
        return {
            "vendido": vendido, "recebido": recebido, "a_receber": vendido - recebido,
            "custo": custo, "gasto": gasto, "gasto_pago": gasto_pago,
            "gasto_pendente": gasto - gasto_pago, "lucro": lucro, "margem": margem,
        }


class VendaEvento(models.Model):
    STATUS_PENDENTE = "pendente"
    STATUS_PARCIAL = "parcial"
    STATUS_RECEBIDA = "recebida"
    STATUS_CANCELADA = "cancelada"
    STATUS_CHOICES = [
        (STATUS_PENDENTE, "Pendente"), (STATUS_PARCIAL, "Parcialmente recebida"),
        (STATUS_RECEBIDA, "Recebida"), (STATUS_CANCELADA, "Cancelada"),
    ]
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name="vendas")
    tipo_produto = models.ForeignKey(
        "TipoProdutoEvento", on_delete=models.PROTECT, related_name="vendas",
        verbose_name="Tipo de produto", null=True, blank=True,
    )
    quantidade = models.PositiveIntegerField(default=1)
    data = models.DateField(default=timezone.localdate)
    descricao = models.CharField("Descrição ou cliente", max_length=200)
    valor_venda = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    custo_produtos = models.DecimalField(max_digits=14, decimal_places=2, default=0, validators=[MinValueValidator(Decimal("0.00"))])
    valor_recebido = models.DecimalField(max_digits=14, decimal_places=2, default=0, validators=[MinValueValidator(Decimal("0.00"))])
    forma_recebimento = models.CharField(max_length=30, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDENTE)
    observacoes = models.TextField(blank=True)
    registrado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    registrado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-data", "-registrado_em"]
        constraints = [
            models.CheckConstraint(condition=Q(valor_venda__gt=0), name="evento_venda_valor_positivo"),
            models.CheckConstraint(condition=Q(custo_produtos__gte=0), name="evento_venda_custo_nao_negativo"),
            models.CheckConstraint(condition=Q(valor_recebido__gte=0) & Q(valor_recebido__lte=models.F("valor_venda")), name="evento_venda_recebido_valido"),
        ]

    def save(self, *args, **kwargs):
        if self.status != self.STATUS_CANCELADA:
            if self.valor_recebido <= 0:
                self.status = self.STATUS_PENDENTE
            elif self.valor_recebido < self.valor_venda:
                self.status = self.STATUS_PARCIAL
            else:
                self.status = self.STATUS_RECEBIDA
        super().save(*args, **kwargs)


class DespesaEvento(models.Model):
    evento = models.ForeignKey(
        Evento, on_delete=models.CASCADE, related_name="despesas", null=True, blank=True,
        help_text="Deixe vazio para uma despesa geral da Use Helvi.",
    )
    conta_pagar = models.OneToOneField(
        "financeiro.ContaPagar", on_delete=models.PROTECT, related_name="despesa_evento"
    )
    registrado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    registrado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-registrado_em"]


class ReceitaEvento(models.Model):
    evento = models.ForeignKey(
        Evento, on_delete=models.CASCADE, related_name="receitas", null=True, blank=True,
        help_text="Deixe vazio para uma receita geral da Use Helvi.",
    )
    conta_receber = models.OneToOneField(
        "financeiro.ContaReceber", on_delete=models.PROTECT, related_name="receita_evento"
    )
    registrado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    registrado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-registrado_em"]


class TipoProdutoEvento(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "Tipo de produto da Use Helvi"

    def __str__(self):
        return self.nome
