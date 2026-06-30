from django import forms
from django.contrib.auth import get_user_model


Usuario = get_user_model()


class UsuarioForm(forms.ModelForm):
    senha = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput,
        required=True,
    )

    confirmar_senha = forms.CharField(
        label="Confirmar senha",
        widget=forms.PasswordInput,
        required=True,
    )

    class Meta:
        model = Usuario
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "telefone",
            "foto",
            "is_active",
            "is_staff",
        ]

    def clean(self):
        cleaned_data = super().clean()

        senha = cleaned_data.get("senha")
        confirmar_senha = cleaned_data.get("confirmar_senha")

        if senha and confirmar_senha and senha != confirmar_senha:
            self.add_error(
                "confirmar_senha",
                "As senhas não conferem.",
            )

        return cleaned_data

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data["senha"])

        if commit:
            usuario.save()

        return usuario


class UsuarioUpdateForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "telefone",
            "foto",
            "is_active",
            "is_staff",
        ]