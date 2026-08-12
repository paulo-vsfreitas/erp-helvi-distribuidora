import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("catalogo", "0004_genero_data_atualizacao_alter_genero_ativo_and_more"),
        ("fornecedores", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("produtos", "0010_produto_fornecedor"),
    ]

    operations = [
        migrations.CreateModel(
            name="ImportacaoCatalogo",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("preco_custo_padrao", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("preco_venda_padrao", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("estoque_inicial_padrao", models.PositiveIntegerField(default=1)),
                ("estoque_minimo_padrao", models.PositiveIntegerField(default=0)),
                ("status", models.CharField(choices=[("rascunho", "Rascunho"), ("analisado", "Analisado"), ("importado", "Importado"), ("cancelado", "Cancelado")], default="rascunho", max_length=20)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
                ("confirmado_em", models.DateTimeField(blank=True, null=True)),
                ("fornecedor", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="importacoes_catalogo", to="fornecedores.fornecedor")),
                ("tipo_armacao", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="importacoes_catalogo", to="catalogo.tipoarmacao")),
                ("usuario", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="importacoes_catalogo_produtos", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-criado_em"]},
        ),
        migrations.CreateModel(
            name="ArquivoImportacaoCatalogo",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("arquivo", models.FileField(upload_to="importacoes_catalogo/%Y/%m/")),
                ("preview", models.ImageField(blank=True, null=True, upload_to="importacoes_catalogo/previews/%Y/%m/")),
                ("nome_original", models.CharField(max_length=255)),
                ("tipo", models.CharField(choices=[("pdf", "PDF"), ("imagem", "Imagem")], max_length=20)),
                ("texto_extraido", models.TextField(blank=True)),
                ("aviso_analise", models.TextField(blank=True)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("lote", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="arquivos", to="produtos.importacaocatalogo")),
            ],
        ),
        migrations.CreateModel(
            name="ItemImportacaoCatalogo",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("codigo_fornecedor", models.CharField(blank=True, max_length=80)),
                ("modelo", models.CharField(blank=True, max_length=100)),
                ("preco_custo", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("preco_venda", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("estoque_minimo", models.PositiveIntegerField(default=0)),
                ("estoque_sem_variacao", models.PositiveIntegerField(default=0)),
                ("incluir", models.BooleanField(default=True)),
                ("duplicidade", models.CharField(choices=[("nenhuma", "Nenhuma"), ("possivel", "Possível"), ("exata", "Exata")], default="nenhuma", max_length=20)),
                ("observacoes", models.TextField(blank=True)),
                ("ordem", models.PositiveIntegerField(default=0)),
                ("arquivos", models.ManyToManyField(blank=True, related_name="itens", to="produtos.arquivoimportacaocatalogo")),
                ("lote", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="itens", to="produtos.importacaocatalogo")),
                ("produto_duplicado", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="sugestoes_importacao_catalogo", to="produtos.produto")),
            ],
            options={"ordering": ["ordem", "id"]},
        ),
        migrations.CreateModel(
            name="VariacaoImportacaoCatalogo",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome", models.CharField(blank=True, max_length=100)),
                ("codigo", models.CharField(blank=True, max_length=50)),
                ("estoque", models.PositiveIntegerField(default=0)),
                ("ordem", models.PositiveIntegerField(default=0)),
                ("item", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="variacoes", to="produtos.itemimportacaocatalogo")),
            ],
            options={"ordering": ["ordem", "id"]},
        ),
    ]
