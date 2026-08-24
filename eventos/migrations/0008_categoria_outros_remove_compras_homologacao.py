from django.db import migrations


def atualizar_categorias(apps, schema_editor):
    CategoriaFinanceira = apps.get_model("financeiro", "CategoriaFinanceira")
    CategoriaFinanceira.objects.get_or_create(
        nome="Outros",
        tipo="despesa",
        defaults={
            "descricao": "Despesas que não se enquadram nas demais categorias.",
            "ativo": True,
        },
    )
    CategoriaFinanceira.objects.filter(
        nome="Compras Homologação",
        tipo="despesa",
    ).update(ativo=False)


class Migration(migrations.Migration):
    dependencies = [("eventos", "0007_equipeevento_evento_equipe_pessoaequipe_and_more")]
    operations = [migrations.RunPython(atualizar_categorias, migrations.RunPython.noop)]
