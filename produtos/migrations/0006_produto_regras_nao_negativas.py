from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("produtos", "0005_remove_produto_fornecedor_and_more"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="produto",
            constraint=models.CheckConstraint(
                condition=models.Q(preco_custo__gte=0),
                name="produto_preco_custo_nao_negativo",
            ),
        ),
        migrations.AddConstraint(
            model_name="produto",
            constraint=models.CheckConstraint(
                condition=models.Q(preco_venda__gte=0),
                name="produto_preco_venda_nao_negativo",
            ),
        ),
        migrations.AddConstraint(
            model_name="produto",
            constraint=models.CheckConstraint(
                condition=models.Q(estoque_atual__gte=0),
                name="produto_estoque_atual_nao_negativo",
            ),
        ),
        migrations.AddConstraint(
            model_name="produto",
            constraint=models.CheckConstraint(
                condition=models.Q(estoque_minimo__gte=0),
                name="produto_estoque_minimo_nao_negativo",
            ),
        ),
    ]
