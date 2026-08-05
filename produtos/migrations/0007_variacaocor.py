from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("produtos", "0006_produto_regras_nao_negativas")]
    operations = [
        migrations.CreateModel(
            name="VariacaoCor",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome", models.CharField(max_length=100, verbose_name="Cor")),
                ("codigo", models.CharField(max_length=50, verbose_name="Código da cor")),
                ("estoque", models.PositiveIntegerField(default=0, verbose_name="Estoque")),
                ("produto", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="variacoes_cor", to="produtos.produto")),
            ],
            options={"verbose_name": "Variação de cor", "verbose_name_plural": "Variações de cor", "ordering": ["nome", "codigo"]},
        ),
        migrations.AddConstraint(model_name="variacaocor", constraint=models.UniqueConstraint(fields=("produto", "codigo"), name="produto_codigo_cor_unico")),
    ]
