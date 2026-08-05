from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("produtos", "0007_variacaocor")]

    operations = [
        migrations.AlterField(
            model_name="produto",
            name="codigo",
            field=models.CharField(
                blank=True,
                max_length=50,
                null=True,
                unique=True,
                verbose_name="Código",
            ),
        ),
        migrations.AlterField(
            model_name="produto",
            name="modelo",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="variacaocor",
            name="nome",
            field=models.CharField(blank=True, max_length=100, verbose_name="Cor"),
        ),
    ]
