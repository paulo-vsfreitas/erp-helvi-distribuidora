from django.db import migrations


def criar_categoria(apps, schema_editor):
    CategoriaFinanceira = apps.get_model("financeiro", "CategoriaFinanceira")
    CategoriaFinanceira.objects.get_or_create(
        nome="Vendas e serviços",
        tipo="receita",
        defaults={"descricao": "Receitas gerais da Use Helvi.", "ativo": True},
    )


class Migration(migrations.Migration):
    dependencies = [("eventos", "0009_receitaevento")]
    operations = [migrations.RunPython(criar_categoria, migrations.RunPython.noop)]
