from django.conf import settings
from django.db import models

from catalogo.models import Colecao, Genero, Marca, TipoArmacao
from fornecedores.models import Fornecedor


class Produto(models.Model):
    class CategoriaComercial(models.TextChoices):
        ARMACAO = "armacao", "Armação"
        ACESSORIO = "acessorio", "Acessório"


    categoria_comercial = models.CharField(
        max_length=20,
        choices=CategoriaComercial.choices,
        default=CategoriaComercial.ARMACAO,
        verbose_name="Categoria Comercial",
    )
    codigo = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Código",
    )

    fornecedor = models.ForeignKey(
        Fornecedor,
        on_delete=models.SET_NULL,
        related_name="produtos",
        blank=True,
        null=True,
        verbose_name="Fornecedor principal",
    )

    codigo_fornecedor = models.CharField(
        max_length=80,
        blank=True,
        null=True,
        verbose_name="Código do fornecedor",
    )


    modelo = models.CharField(
        max_length=100,
        blank=True,
    )

    marca = models.ForeignKey(
        Marca,
        on_delete=models.PROTECT,
        related_name="produtos",
        blank=True,
        null=True,
    )

    colecao = models.ForeignKey(
        Colecao,
        on_delete=models.PROTECT,
        related_name="produtos",
        verbose_name="Coleção",
        blank=True,
        null=True,
    )

    genero = models.ForeignKey(
        Genero,
        on_delete=models.PROTECT,
        related_name="produtos",
        verbose_name="Gênero",
        blank=True,
        null=True,
    )

    tipo_armacao = models.ForeignKey(
        TipoArmacao,
        on_delete=models.PROTECT,
        related_name="produtos",
        verbose_name="Tipo de Armação",
        blank=True,
        null=True,
    )

    cores_disponiveis = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Cores Disponíveis",
    )

    preco_custo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Preço de Custo",
    )

    preco_venda = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Preço de Venda",
    )

    estoque_atual = models.IntegerField(
        default=0,
        verbose_name="Estoque Atual",
    )

    estoque_minimo = models.IntegerField(
        default=0,
        verbose_name="Estoque Mínimo",
    )

    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações",
    )

    foto = models.ImageField(
        upload_to="produtos/",
        blank=True,
        null=True,
        verbose_name="Foto Principal",
    )

    ativo = models.BooleanField(
        default=True,
    )

    data_cadastro = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Produto / Armação"
        verbose_name_plural = "Produtos / Armações"
        ordering = ["modelo"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(preco_custo__gte=0),
                name="produto_preco_custo_nao_negativo",
            ),
            models.CheckConstraint(
                condition=models.Q(preco_venda__gte=0),
                name="produto_preco_venda_nao_negativo",
            ),
            models.CheckConstraint(
                condition=models.Q(estoque_atual__gte=0),
                name="produto_estoque_atual_nao_negativo",
            ),
            models.CheckConstraint(
                condition=models.Q(estoque_minimo__gte=0),
                name="produto_estoque_minimo_nao_negativo",
            ),
            models.UniqueConstraint(
                fields=["fornecedor", "codigo_fornecedor"],
                condition=(
                    models.Q(fornecedor__isnull=False)
                    & models.Q(codigo_fornecedor__isnull=False)
                    & ~models.Q(codigo_fornecedor="")
                ),
                name="produto_fornecedor_codigo_fornecedor_unico",
            ),
        ]

    def __str__(self):
        partes = []

        if self.codigo:
            partes.append(self.codigo)

        if self.codigo_fornecedor:
            partes.append(self.codigo_fornecedor)

        if self.modelo:
            partes.append(self.modelo)

        return " — ".join(partes) or f"Produto #{self.pk or 'novo'}"

    @property
    def lucro_unitario(self):
        return self.preco_venda - self.preco_custo

    @property
    def margem_lucro(self):
        if self.preco_custo == 0:
            return 0

        return (self.lucro_unitario / self.preco_custo) * 100


class VariacaoCor(models.Model):
    produto = models.ForeignKey(
        Produto, on_delete=models.CASCADE, related_name="variacoes_cor"
    )
    nome = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Cor",
    )
    codigo = models.CharField(max_length=50, verbose_name="Código da cor")
    estoque = models.PositiveIntegerField(default=0, verbose_name="Estoque")

    class Meta:
        verbose_name = "Variação de cor"
        verbose_name_plural = "Variações de cor"
        ordering = ["nome", "codigo"]
        constraints = [
            models.UniqueConstraint(
                fields=["produto", "codigo"],
                name="produto_codigo_cor_unico",
            )
        ]

    def __str__(self):
        if self.nome:
            return f"{self.nome} ({self.codigo})"
        return self.codigo


class ImagemProduto(models.Model):
    produto = models.ForeignKey(
        Produto,
        on_delete=models.CASCADE,
        related_name="imagens",
    )

    imagem = models.ImageField(
        upload_to="produtos/galeria/",
        verbose_name="Imagem",
    )

    descricao = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Descrição",
    )

    principal = models.BooleanField(
        default=False,
        verbose_name="Imagem Principal",
    )

    data_cadastro = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Imagem do Produto"
        verbose_name_plural = "Imagens dos Produtos"
        ordering = ["-principal", "data_cadastro"]

    def __str__(self):
        return f"Imagem de {self.produto}"


class ImportacaoCatalogo(models.Model):
    class Status(models.TextChoices):
        RASCUNHO = "rascunho", "Rascunho"
        ANALISADO = "analisado", "Analisado"
        IMPORTADO = "importado", "Importado"
        CANCELADO = "cancelado", "Cancelado"

    fornecedor = models.ForeignKey(
        Fornecedor, on_delete=models.PROTECT, related_name="importacoes_catalogo"
    )
    tipo_armacao = models.ForeignKey(
        TipoArmacao, on_delete=models.PROTECT, related_name="importacoes_catalogo"
    )
    preco_custo_padrao = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    preco_venda_padrao = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estoque_inicial_padrao = models.PositiveIntegerField(default=1)
    estoque_minimo_padrao = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.RASCUNHO)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="importacoes_catalogo_produtos"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    confirmado_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-criado_em"]

    def __str__(self):
        return f"Catálogo #{self.pk} - {self.fornecedor}"


class ArquivoImportacaoCatalogo(models.Model):
    class Tipo(models.TextChoices):
        PDF = "pdf", "PDF"
        IMAGEM = "imagem", "Imagem"

    lote = models.ForeignKey(ImportacaoCatalogo, on_delete=models.CASCADE, related_name="arquivos")
    arquivo = models.FileField(upload_to="importacoes_catalogo/%Y/%m/")
    preview = models.ImageField(upload_to="importacoes_catalogo/previews/%Y/%m/", blank=True, null=True)
    nome_original = models.CharField(max_length=255)
    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    texto_extraido = models.TextField(blank=True)
    aviso_analise = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome_original


class RecorteImportacaoCatalogo(models.Model):
    class Tipo(models.TextChoices):
        HERO = "hero", "Hero"
        VARIACAO = "variacao", "Variação"

    arquivo = models.ForeignKey(
        ArquivoImportacaoCatalogo,
        on_delete=models.CASCADE,
        related_name="recortes",
    )
    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    indice = models.PositiveIntegerField(default=0)
    imagem = models.ImageField(upload_to="importacoes_catalogo/recortes/%Y/%m/")
    nome_cor = models.CharField(max_length=100, blank=True)
    cor_hex = models.CharField(max_length=7, default="#6c757d")
    texto_hex = models.CharField(max_length=7, default="#ffffff")
    layout = models.JSONField(default=dict, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["tipo", "indice", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["arquivo", "tipo", "indice"],
                name="recorte_catalogo_arquivo_tipo_indice_unico",
            )
        ]

    def __str__(self):
        return f"{self.arquivo} - {self.tipo} {self.indice}"


class ItemImportacaoCatalogo(models.Model):
    class Duplicidade(models.TextChoices):
        NENHUMA = "nenhuma", "Nenhuma"
        POSSIVEL = "possivel", "Possível"
        EXATA = "exata", "Exata"

    lote = models.ForeignKey(ImportacaoCatalogo, on_delete=models.CASCADE, related_name="itens")
    arquivos = models.ManyToManyField(ArquivoImportacaoCatalogo, related_name="itens", blank=True)
    arquivo_principal = models.ForeignKey(
        ArquivoImportacaoCatalogo, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="itens_como_principal"
    )
    codigo_fornecedor = models.CharField(max_length=80, blank=True)
    modelo = models.CharField(max_length=100, blank=True)
    preco_custo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    preco_venda = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estoque_minimo = models.PositiveIntegerField(default=0)
    estoque_sem_variacao = models.PositiveIntegerField(default=0)
    incluir = models.BooleanField(default=True)
    duplicidade = models.CharField(
        max_length=20, choices=Duplicidade.choices, default=Duplicidade.NENHUMA
    )
    produto_duplicado = models.ForeignKey(
        Produto, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="sugestoes_importacao_catalogo"
    )
    observacoes = models.TextField(blank=True)
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["ordem", "id"]

    def __str__(self):
        return self.codigo_fornecedor or self.modelo or f"Item #{self.pk}"


class VariacaoImportacaoCatalogo(models.Model):
    item = models.ForeignKey(ItemImportacaoCatalogo, on_delete=models.CASCADE, related_name="variacoes")
    nome = models.CharField(max_length=100, blank=True)
    codigo = models.CharField(max_length=50, blank=True)
    estoque = models.PositiveIntegerField(default=0)
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["ordem", "id"]

    def __str__(self):
        return self.codigo or self.nome or f"Variação #{self.pk}"
