from django.db import migrations, models
import django.core.validators
from decimal import Decimal


def preencher_custo_historico(apps, schema_editor):
    ItemVenda = apps.get_model("vendas", "ItemVenda")
    for item in ItemVenda.objects.select_related("produto").iterator():
        item.custo_unitario = item.produto.preco_custo or Decimal("0.00")
        item.save(update_fields=["custo_unitario"])


class Migration(migrations.Migration):
    dependencies = [("vendas", "0011_remove_itemvenda_venda_produto_unico_and_more")]

    operations = [
        migrations.AddField(
            model_name="itemvenda",
            name="custo_unitario",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("0.00"),
                help_text="Custo do produto preservado no momento da venda.",
                max_digits=12,
                validators=[django.core.validators.MinValueValidator(Decimal("0.00"))],
            ),
        ),
        migrations.RunPython(preencher_custo_historico, migrations.RunPython.noop),
    ]
