from django.db import models


class Fornecedor(models.Model):
    TIPO_PESSOA_FISICA = "PF"
    TIPO_PESSOA_JURIDICA = "PJ"

    TIPO_PESSOA_CHOICES = [
        (TIPO_PESSOA_FISICA, "Pessoa Física"),
        (TIPO_PESSOA_JURIDICA, "Pessoa Jurídica"),
    ]

    ESTADOS_CHOICES = [
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

    codigo = models.CharField(
        max_length=15,
        unique=True,
        null=True,
        blank=True,
        editable=False,
        verbose_name="Código",
    )

    tipo_pessoa = models.CharField(
        max_length=2,
        choices=TIPO_PESSOA_CHOICES,
        default=TIPO_PESSOA_JURIDICA,
        verbose_name="Tipo de pessoa",
    )

    razao_social = models.CharField(
        max_length=180,
        verbose_name="Razão social / Nome",
    )

    nome_fantasia = models.CharField(
        max_length=180,
        blank=True,
        verbose_name="Nome fantasia",
    )

    cpf_cnpj = models.CharField(
        max_length=18,
        unique=True,
        verbose_name="CPF/CNPJ",
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

    contato_principal = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Contato principal",
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
        choices=ESTADOS_CHOICES,
        blank=True,
        verbose_name="Estado",
    )

    prazo_medio_entrega = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Prazo médio de entrega",
        help_text="Informe o prazo médio em dias.",
    )

    condicao_pagamento_padrao = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Condição de pagamento padrão",
    )

    observacoes = models.TextField(
        blank=True,
        verbose_name="Observações",
    )

    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo",
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
        verbose_name = "Fornecedor"
        verbose_name_plural = "Fornecedores"
        ordering = ["razao_social"]
        indexes = [
            models.Index(fields=["codigo"]),
            models.Index(fields=["razao_social"]),
            models.Index(fields=["nome_fantasia"]),
            models.Index(fields=["cpf_cnpj"]),
            models.Index(fields=["ativo"]),
        ]

    def save(self, *args, **kwargs):
        """
        Gera o código definitivo após o banco atribuir o ID do fornecedor.

        Exemplo:
        ID 1   -> FOR000001
        ID 25  -> FOR000025
        """
        fornecedor_novo = self.pk is None

        super().save(*args, **kwargs)

        if fornecedor_novo and not self.codigo:
            self.codigo = f"FOR{self.pk:06d}"

            type(self).objects.filter(pk=self.pk).update(
                codigo=self.codigo
            )

    def __str__(self):
        nome = self.nome_fantasia or self.razao_social

        if self.codigo:
            return f"{self.codigo} - {nome}"

        return nome