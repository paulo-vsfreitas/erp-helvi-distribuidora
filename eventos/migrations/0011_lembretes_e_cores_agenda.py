from django.core.validators import MaxValueValidator, RegexValidator
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("eventos", "0010_categoria_receita_use_helvi")]

    operations = [
        migrations.AddField(
            model_name="pessoaequipe", name="cor_agenda",
            field=models.CharField(default="#743f76", max_length=7, verbose_name="Cor na agenda", validators=[RegexValidator("^#[0-9A-Fa-f]{6}$", "Informe uma cor válida.")]),
        ),
        migrations.AddField(
            model_name="evento", name="lembrete_ativo",
            field=models.BooleanField(default=False, verbose_name="Exibir lembrete na agenda"),
        ),
        migrations.AddField(
            model_name="evento", name="lembrete_dias_antes",
            field=models.PositiveSmallIntegerField(default=1, validators=[MaxValueValidator(365)], verbose_name="Avisar com quantos dias de antecedência"),
        ),
        migrations.AddField(
            model_name="evento", name="lembrete_mensagem",
            field=models.CharField(blank=True, help_text="Se ficar vazio, o sistema usará uma mensagem automática.", max_length=240, verbose_name="Mensagem do lembrete"),
        ),
    ]
