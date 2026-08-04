from django import forms
from django.contrib.auth import get_user_model


Usuario = get_user_model()


def aplicar_estilos_formulario_usuario(form):
    configuracoes = {
        "username": {
            "class": "form-control",
            "placeholder": "Nome usado para entrar no sistema",
            "autocomplete": "username",
        },
        "first_name": {
            "class": "form-control",
            "placeholder": "Nome",
            "autocomplete": "given-name",
        },
        "last_name": {
            "class": "form-control",
            "placeholder": "Sobrenome",
            "autocomplete": "family-name",
        },
        "email": {
            "class": "form-control",
            "placeholder": "usuario@empresa.com",
            "autocomplete": "email",
        },
        "telefone": {
            "class": "form-control",
            "placeholder": "(00) 00000-0000",
            "autocomplete": "tel",
        },
        "perfil": {
            "class": "form-select",
        },
        "foto": {
            "class": "hui-user-photo-input visually-hidden",
            "accept": "image/png,image/jpeg,image/webp",
        },
        "is_active": {
            "class": "hui-user-switch-input visually-hidden",
            "role": "switch",
        },
    }

    for nome, atributos in configuracoes.items():
        form.fields[nome].widget.attrs.update(atributos)


class UsuarioForm(forms.ModelForm):
    senha = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Digite uma senha segura",
                "autocomplete": "new-password",
            },
        ),
        required=True,
    )

    confirmar_senha = forms.CharField(
        label="Confirmar senha",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Repita a senha",
                "autocomplete": "new-password",
            },
        ),
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
            "perfil",
            "foto",
            "is_active",
        ]

        widgets = {
            "foto": forms.FileInput,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        aplicar_estilos_formulario_usuario(self)

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
        usuario.primeiro_acesso = True

        if usuario.perfil in (
            Usuario.Perfil.ADMINISTRADOR,
            Usuario.Perfil.GERENTE,
        ):
            usuario.is_staff = True
        else:
            usuario.is_staff = False

        if commit:
            usuario.save()

        return usuario


class UsuarioUpdateForm(forms.ModelForm):
    senha = forms.CharField(
        label="Nova senha",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Digite a nova senha",
                "autocomplete": "new-password",
            },
        ),
        required=False,
        help_text="Preencha apenas se quiser alterar a senha.",
    )

    confirmar_senha = forms.CharField(
        label="Confirmar nova senha",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Repita a nova senha",
                "autocomplete": "new-password",
            },
        ),
        required=False,
    )

    class Meta:
        model = Usuario
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "telefone",
            "perfil",
            "foto",
            "is_active",
        ]

        widgets = {
            "foto": forms.FileInput,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        aplicar_estilos_formulario_usuario(self)

    def clean(self):
        cleaned_data = super().clean()

        senha = cleaned_data.get("senha")
        confirmar_senha = cleaned_data.get("confirmar_senha")

        if senha or confirmar_senha:
            if senha != confirmar_senha:
                self.add_error(
                    "confirmar_senha",
                    "As senhas não conferem.",
                )

        return cleaned_data

    def save(self, commit=True):
        usuario = super().save(commit=False)

        senha = self.cleaned_data.get("senha")
        if senha:
            usuario.set_password(senha)
            usuario.primeiro_acesso = True

        if usuario.perfil in (
            Usuario.Perfil.ADMINISTRADOR,
            Usuario.Perfil.GERENTE,
        ):
            usuario.is_staff = True
        else:
            usuario.is_staff = False

        if commit:
            usuario.save()

        return usuario
