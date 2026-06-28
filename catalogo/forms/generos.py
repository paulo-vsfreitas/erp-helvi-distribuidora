from django import forms

from catalogo.models import Genero


class GeneroForm(forms.ModelForm):
    class Meta:
        model = Genero
        fields = [
            "nome",
            "descricao",
        ]

        widgets = {
            "nome": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Digite o nome do gênero",
                    "autofocus": True,
                }
            ),
            "descricao": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Descrição (opcional)",
                }
            ),
        }