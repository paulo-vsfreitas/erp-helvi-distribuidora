from decimal import Decimal

from django.db import migrations


def normalizar_vendas_existentes(apps, schema_editor):
    Venda = apps.get_model("vendas", "Venda")
    ItemVenda = apps.get_model("vendas", "ItemVenda")

    vendas = Venda.objects.order_by("id")

    for numero, venda in enumerate(vendas, start=1):
        subtotal_venda = Decimal("0.00")

        itens = ItemVenda.objects.filter(venda_id=venda.id).order_by("id")

        for item in itens:
            bruto = item.preco_unitario * item.quantidade
            desconto_item = item.desconto or Decimal("0.00")
            total_item = max(bruto - desconto_item, Decimal("0.00"))

            item.total = total_item
            item.save(update_fields=["total"])

            subtotal_venda += total_item

        desconto_venda = venda.desconto or Decimal("0.00")
        frete_venda = venda.frete or Decimal("0.00")

        total_venda = max(
            subtotal_venda - desconto_venda + frete_venda,
            Decimal("0.00"),
        )

        venda.numero = numero
        venda.subtotal = subtotal_venda
        venda.total = total_venda

        venda.save(
            update_fields=[
                "numero",
                "subtotal",
                "total",
            ]
        )


def reverter_normalizacao(apps, schema_editor):
    Venda = apps.get_model("vendas", "Venda")
    ItemVenda = apps.get_model("vendas", "ItemVenda")

    Venda.objects.update(
        numero=None,
        subtotal=Decimal("0.00"),
        total=Decimal("0.00"),
    )

    ItemVenda.objects.update(
        total=Decimal("0.00"),
    )


class Migration(migrations.Migration):

    dependencies = [
        (
            "vendas",
            "0005_alter_itemvenda_options_alter_venda_options_and_more",
        ),
    ]

    operations = [
        migrations.RunPython(
            normalizar_vendas_existentes,
            reverter_normalizacao,
        ),
    ]