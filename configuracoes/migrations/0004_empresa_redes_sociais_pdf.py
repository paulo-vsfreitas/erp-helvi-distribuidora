from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("configuracoes", "0003_preencher_modelos_mensagem_padrao")]

    operations = [
        migrations.AddField(model_name="empresa", name="instagram", field=models.CharField(blank=True, max_length=150, verbose_name="Instagram")),
        migrations.AddField(model_name="empresa", name="facebook", field=models.CharField(blank=True, max_length=200, verbose_name="Facebook")),
        migrations.AddField(model_name="empresa", name="exibir_whatsapp_pdf", field=models.BooleanField(default=True, verbose_name="Exibir WhatsApp nos PDFs")),
        migrations.AddField(model_name="empresa", name="exibir_instagram_pdf", field=models.BooleanField(default=False, verbose_name="Exibir Instagram nos PDFs")),
        migrations.AddField(model_name="empresa", name="exibir_facebook_pdf", field=models.BooleanField(default=False, verbose_name="Exibir Facebook nos PDFs")),
        migrations.AddField(model_name="empresa", name="exibir_site_pdf", field=models.BooleanField(default=True, verbose_name="Exibir site nos PDFs")),
    ]
