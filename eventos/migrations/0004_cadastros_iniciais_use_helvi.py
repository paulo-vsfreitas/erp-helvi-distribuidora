from django.db import migrations


TIPOS = (
    "Casual feminino",
    "Casual masculino",
    "Esportivo feminino",
    "Esportivo masculino",
    "Estojo",
    "Outro",
)


def criar_cadastros(apps, schema_editor):
    TipoProdutoEvento = apps.get_model("eventos", "TipoProdutoEvento")
    CategoriaFinanceira = apps.get_model("financeiro", "CategoriaFinanceira")
    VendaEvento = apps.get_model("eventos", "VendaEvento")

    tipos = {}
    for nome in TIPOS:
        tipos[nome], _ = TipoProdutoEvento.objects.get_or_create(nome=nome)
    VendaEvento.objects.filter(tipo_produto__isnull=True).update(
        tipo_produto=tipos["Outro"]
    )
    CategoriaFinanceira.objects.get_or_create(
        nome="Equipamentos e expositores",
        tipo="despesa",
        defaults={
            "descricao": "Expositores, mobiliário e equipamentos da Use Helvi.",
            "ativo": True,
        },
    )


class Migration(migrations.Migration):
    dependencies = [
        ("eventos", "0003_tipoprodutoevento_evento_instagram_and_more"),
    ]
    operations = [migrations.RunPython(criar_cadastros, migrations.RunPython.noop)]
