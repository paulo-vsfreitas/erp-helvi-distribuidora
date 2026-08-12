import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("fornecedores", "0001_initial"),
        ("produtos", "0009_produto_categoria_comercial"),
    ]

    operations = [
        migrations.AddField(
            model_name="produto",
            name="fornecedor",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="produtos",
                to="fornecedores.fornecedor",
                verbose_name="Fornecedor principal",
            ),
        ),
        migrations.AddConstraint(
            model_name="produto",
            constraint=models.UniqueConstraint(
                condition=(
                    models.Q(("fornecedor__isnull", False))
                    & models.Q(("codigo_fornecedor__isnull", False))
                    & ~models.Q(("codigo_fornecedor", ""))
                ),
                fields=("fornecedor", "codigo_fornecedor"),
                name="produto_fornecedor_codigo_fornecedor_unico",
            ),
        ),
    ]
