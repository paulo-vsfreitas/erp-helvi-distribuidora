from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("vendas", "0009_venda_conta_financeira_venda_primeiro_vencimento_and_more"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="venda",
            constraint=models.CheckConstraint(
                condition=models.Q(subtotal__gte=0),
                name="venda_subtotal_nao_negativo",
            ),
        ),
        migrations.AddConstraint(
            model_name="venda",
            constraint=models.CheckConstraint(
                condition=models.Q(desconto__gte=0),
                name="venda_desconto_nao_negativo",
            ),
        ),
        migrations.AddConstraint(
            model_name="venda",
            constraint=models.CheckConstraint(
                condition=models.Q(frete__gte=0),
                name="venda_frete_nao_negativo",
            ),
        ),
        migrations.AddConstraint(
            model_name="venda",
            constraint=models.CheckConstraint(
                condition=models.Q(total__gte=0),
                name="venda_total_nao_negativo",
            ),
        ),
        migrations.AddConstraint(
            model_name="venda",
            constraint=models.CheckConstraint(
                condition=models.Q(valor_recebido__gte=0),
                name="venda_recebido_nao_negativo",
            ),
        ),
        migrations.AddConstraint(
            model_name="venda",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    valor_recebido__lte=models.F("total"),
                ),
                name="venda_recebido_ate_total",
            ),
        ),
    ]
