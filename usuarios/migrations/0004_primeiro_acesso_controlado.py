from django.db import migrations, models


def marcar_usuarios_existentes_como_configurados(apps, schema_editor):
    Usuario = apps.get_model("usuarios", "Usuario")
    Usuario.objects.update(primeiro_acesso=False)


class Migration(migrations.Migration):
    dependencies = [
        ("usuarios", "0003_usuario_perfil"),
    ]

    operations = [
        migrations.AlterField(
            model_name="usuario",
            name="primeiro_acesso",
            field=models.BooleanField(
                default=False,
                verbose_name="Primeiro acesso",
            ),
        ),
        migrations.RunPython(
            marcar_usuarios_existentes_como_configurados,
            migrations.RunPython.noop,
        ),
    ]
