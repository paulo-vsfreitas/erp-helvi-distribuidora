from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("configuracoes", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="empresa",
            name="assunto_padrao_email",
            field=models.CharField(
                blank=True,
                help_text="Aceita as variáveis de comunicação do ERP.",
                max_length=200,
                verbose_name="Assunto padrão de e-mail",
            ),
        ),
        migrations.AddField(
            model_name="empresa",
            name="mensagem_padrao_email",
            field=models.TextField(
                blank=True,
                help_text="Aceita as variáveis de comunicação do ERP.",
                verbose_name="Mensagem padrão de e-mail",
            ),
        ),
        migrations.AddField(
            model_name="empresa",
            name="mensagem_padrao_whatsapp",
            field=models.TextField(
                blank=True,
                help_text="Aceita as variáveis de comunicação do ERP.",
                verbose_name="Mensagem padrão de WhatsApp",
            ),
        ),
    ]
