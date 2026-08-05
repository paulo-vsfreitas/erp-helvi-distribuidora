from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("usuarios", "0004_primeiro_acesso_controlado"),
    ]

    operations = [
        migrations.CreateModel(
            name="ControleTentativaLogin",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("username", models.CharField(max_length=150)),
                ("endereco_ip", models.GenericIPAddressField()),
                ("falhas", models.PositiveSmallIntegerField(default=0)),
                ("bloqueado_ate", models.DateTimeField(blank=True, null=True)),
                ("ultima_tentativa", models.DateTimeField(auto_now=True)),
            ],
            options={
                "indexes": [models.Index(fields=["bloqueado_ate"], name="login_bloqueado_ate_idx")],
                "constraints": [models.UniqueConstraint(fields=("username", "endereco_ip"), name="login_controle_usuario_ip_unico")],
            },
        ),
        migrations.CreateModel(
            name="EventoLogin",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("username", models.CharField(db_index=True, max_length=150)),
                ("endereco_ip", models.GenericIPAddressField()),
                ("resultado", models.CharField(choices=[("sucesso", "Sucesso"), ("falha", "Falha"), ("bloqueado", "Bloqueado")], max_length=10)),
                ("user_agent", models.CharField(blank=True, max_length=300)),
                ("criado_em", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("usuario", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="eventos_login", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-criado_em", "-id"],
                "indexes": [models.Index(fields=["endereco_ip", "criado_em"], name="login_ip_criado_idx")],
            },
        ),
    ]
