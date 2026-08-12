import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("produtos", "0011_importacao_catalogo"),
    ]

    operations = [
        migrations.AddField(
            model_name="itemimportacaocatalogo",
            name="arquivo_principal",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="itens_como_principal",
                to="produtos.arquivoimportacaocatalogo",
            ),
        ),
    ]
