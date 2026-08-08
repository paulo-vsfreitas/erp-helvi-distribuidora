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
        ]

    def __str__(self):
        identificacao = " - ".join(
            valor for valor in (self.codigo, self.modelo) if valor
        )
        return identificacao or f"Produto #{self.pk or 'novo'}"

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
