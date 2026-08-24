from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("eventos", "0011_lembretes_e_cores_agenda")]

    operations = [
        migrations.RemoveField(model_name="pessoaequipe", name="instagram"),
        migrations.AlterField(
            model_name="evento", name="instagram",
            field=models.CharField(blank=True, max_length=80, verbose_name="Instagram do organizador/local"),
        ),
    ]
