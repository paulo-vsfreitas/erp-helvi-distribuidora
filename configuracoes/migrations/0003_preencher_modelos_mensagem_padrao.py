from django.db import migrations, models


ASSUNTO_EMAIL = "{EMPRESA} • Orçamento {ORCAMENTO}"

MENSAGEM_EMAIL = """Olá, {CLIENTE}!

Agradecemos pelo seu interesse em nossos produtos.

Encaminhamos o orçamento {ORCAMENTO}, no valor total de {TOTAL}, com validade até {VALIDADE}.

O documento completo segue anexo para sua conferência. Caso tenha alguma dúvida ou queira solicitar ajustes, permanecemos à disposição.

Atenciosamente,

{VENDEDOR}
{EMPRESA}"""

MENSAGEM_WHATSAPP = """Olá, {CLIENTE}! Tudo bem?

Sou {VENDEDOR}, da {EMPRESA}.

Preparei o orçamento {ORCAMENTO}, no valor total de {TOTAL}, válido até {VALIDADE}.

Estou enviando o documento para sua conferência. Se tiver alguma dúvida ou precisar de algum ajuste, fico à disposição!"""


def preencher_campos_vazios(apps, schema_editor):
    Empresa = apps.get_model("configuracoes", "Empresa")
    Empresa.objects.filter(assunto_padrao_email="").update(
        assunto_padrao_email=ASSUNTO_EMAIL
    )
    Empresa.objects.filter(mensagem_padrao_email="").update(
        mensagem_padrao_email=MENSAGEM_EMAIL
    )
    Empresa.objects.filter(mensagem_padrao_whatsapp="").update(
        mensagem_padrao_whatsapp=MENSAGEM_WHATSAPP
    )


class Migration(migrations.Migration):
    dependencies = [
        ("configuracoes", "0002_empresa_modelos_mensagem"),
    ]

    operations = [
        migrations.AlterField(
            model_name="empresa",
            name="assunto_padrao_email",
            field=models.CharField(
                blank=True,
                default=ASSUNTO_EMAIL,
                help_text="Aceita as variáveis de comunicação do ERP.",
                max_length=200,
                verbose_name="Assunto padrão de e-mail",
            ),
        ),
        migrations.AlterField(
            model_name="empresa",
            name="mensagem_padrao_email",
            field=models.TextField(
                blank=True,
                default=MENSAGEM_EMAIL,
                help_text="Aceita as variáveis de comunicação do ERP.",
                verbose_name="Mensagem padrão de e-mail",
            ),
        ),
        migrations.AlterField(
            model_name="empresa",
            name="mensagem_padrao_whatsapp",
            field=models.TextField(
                blank=True,
                default=MENSAGEM_WHATSAPP,
                help_text="Aceita as variáveis de comunicação do ERP.",
                verbose_name="Mensagem padrão de WhatsApp",
            ),
        ),
        migrations.RunPython(
            preencher_campos_vazios,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
