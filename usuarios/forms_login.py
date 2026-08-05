from django import forms
from django.contrib.auth.forms import AuthenticationForm

from usuarios.services.seguranca_login import (
    esta_bloqueado,
    identificar_ip,
    registrar_bloqueio,
    registrar_falha,
    registrar_sucesso,
)


MENSAGEM_LOGIN_INVALIDO = (
    "Não foi possível entrar. Verifique os dados e tente novamente mais tarde."
)


class LoginSeguroForm(AuthenticationForm):
    error_messages = {
        "invalid_login": MENSAGEM_LOGIN_INVALIDO,
        "inactive": MENSAGEM_LOGIN_INVALIDO,
    }

    def clean(self):
        username = self.data.get("username", "")
        endereco_ip = identificar_ip(self.request)

        if esta_bloqueado(username=username, endereco_ip=endereco_ip):
            registrar_bloqueio(request=self.request, username=username)
            raise forms.ValidationError(
                MENSAGEM_LOGIN_INVALIDO,
                code="invalid_login",
            )

        try:
            dados = super().clean()
        except forms.ValidationError:
            registrar_falha(request=self.request, username=username)
            raise forms.ValidationError(
                MENSAGEM_LOGIN_INVALIDO,
                code="invalid_login",
            )

        usuario = self.get_user()
        if usuario is None:
            registrar_falha(request=self.request, username=username)
            raise forms.ValidationError(
                MENSAGEM_LOGIN_INVALIDO,
                code="invalid_login",
            )

        registrar_sucesso(
            request=self.request,
            username=username,
            usuario=usuario,
        )
        return dados
