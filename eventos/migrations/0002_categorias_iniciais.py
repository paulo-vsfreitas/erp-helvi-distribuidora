from django.db import migrations


CATEGORIAS = (
    ("Taxa de exposição", "Taxas de participação, inscrição e exposição em eventos."),
    ("Combustível", "Gasolina, etanol e demais combustíveis usados em eventos."),
    ("Alimentação", "Refeições e alimentação da equipe durante eventos."),
    ("Locação de veículos", "Aluguel de carros e outros veículos para eventos."),
    ("Hospedagem", "Hospedagem da equipe em eventos e viagens."),
    ("Pedágio e estacionamento", "Pedágios e estacionamentos vinculados a deslocamentos."),
    ("Materiais para stand", "Materiais, montagem e itens de apoio do stand."),
)


def criar_categorias(apps, schema_editor):
    CategoriaFinanceira = apps.get_model("financeiro", "CategoriaFinanceira")
    for nome, descricao in CATEGORIAS:
        CategoriaFinanceira.objects.get_or_create(
            nome=nome,
            tipo="despesa",
            defaults={"descricao": descricao, "ativo": True},
        )


class Migration(migrations.Migration):
    dependencies = [("eventos", "0001_initial")]
    operations = [migrations.RunPython(criar_categorias, migrations.RunPython.noop)]
