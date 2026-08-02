from django.core.exceptions import ValidationError
from django.db import models


class Empresa(models.Model):
    """
    Dados institucionais utilizados em documentos, relatórios,
    e-mails e demais comunicações emitidas pelo ERP Helvi.

    O sistema permite apenas um registro de Empresa.
    """

    ESTADOS = [
        ("AC", "Acre"),
        ("AL", "Alagoas"),
        ("AP", "Amapá"),
        ("AM", "Amazonas"),
        ("BA", "Bahia"),
        ("CE", "Ceará"),
        ("DF", "Distrito Federal"),
        ("ES", "Espírito Santo"),
        ("GO", "Goiás"),
        ("MA", "Maranhão"),
        ("MT", "Mato Grosso"),
        ("MS", "Mato Grosso do Sul"),
        ("MG", "Minas Gerais"),
        ("PA", "Pará"),
        ("PB", "Paraíba"),
        ("PR", "Paraná"),
        ("PE", "Pernambuco"),
        ("PI", "Piauí"),
        ("RJ", "Rio de Janeiro"),
        ("RN", "Rio Grande do Norte"),
        ("RS", "Rio Grande do Sul"),
        ("RO", "Rondônia"),
        ("RR", "Roraima"),
        ("SC", "Santa Catarina"),
        ("SP", "São Paulo"),
        ("SE", "Sergipe"),
        ("TO", "Tocantins"),
    ]

    # Campo técnico que garante apenas um registro no banco.
    singleton = models.BooleanField(
        default=True,
        unique=True,
        editable=False,
    )

    nome_fantasia = models.CharField(
        max_length=150,
        verbose_name="Nome fantasia",
    )

    razao_social = models.CharField(
        max_length=200,
        verbose_name="Razão social",
    )

    cnpj = models.CharField(
        max_length=18,
        blank=True,
        verbose_name="CNPJ",
    )

    inscricao_estadual = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Inscrição estadual",
    )

    inscricao_municipal = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Inscrição municipal",
    )

    telefone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Telefone",
    )

    whatsapp = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="WhatsApp",
    )

    email = models.EmailField(
        blank=True,
        verbose_name="E-mail",
    )

    site = models.URLField(
        blank=True,
        verbose_name="Site",
    )

    cep = models.CharField(
        max_length=9,
        blank=True,
        verbose_name="CEP",
    )

    logradouro = models.CharField(
        max_length=180,
        blank=True,
        verbose_name="Logradouro",
    )

    numero = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Número",
    )

    complemento = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Complemento",
    )

    bairro = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Bairro",
    )

    cidade = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Cidade",
    )

    estado = models.CharField(
        max_length=2,
        choices=ESTADOS,
        blank=True,
        verbose_name="Estado",
    )

    logo = models.ImageField(
        upload_to="empresa/",
        blank=True,
        null=True,
        verbose_name="Logo institucional",
    )

    rodape_documentos = models.TextField(
        blank=True,
        verbose_name="Rodapé dos documentos",
        help_text=(
            "Texto exibido no rodapé de orçamentos, vendas, "
            "comprovantes e relatórios."
        ),
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
        verbose_name = "Dados da empresa"
        verbose_name_plural = "Dados da empresa"

    def __str__(self):
        return self.nome_fantasia or self.razao_social

    def clean(self):
        super().clean()

        outra_empresa = Empresa.objects.exclude(pk=self.pk).exists()

        if outra_empresa:
            raise ValidationError(
                "O ERP Helvi permite apenas um cadastro institucional."
            )

    def save(self, *args, **kwargs):
        self.singleton = True
        self.full_clean()
        return super().save(*args, **kwargs)

    @property
    def endereco_completo(self):
        """
        Monta uma representação legível do endereço para documentos.
        """
        partes = []

        if self.logradouro:
            endereco = self.logradouro

            if self.numero:
                endereco += f", {self.numero}"

            partes.append(endereco)

        if self.complemento:
            partes.append(self.complemento)

        if self.bairro:
            partes.append(self.bairro)

        localidade = " - ".join(
            parte
            for parte in [self.cidade, self.estado]
            if parte
        )

        if localidade:
            partes.append(localidade)

        if self.cep:
            partes.append(f"CEP {self.cep}")

        return " | ".join(partes)