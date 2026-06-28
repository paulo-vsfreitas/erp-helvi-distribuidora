from django import forms
from django.core.exceptions import ValidationError

from catalogo.models import Colecao


class ColecaoForm(forms.ModelForm):

    class Meta:

        model = Colecao

        fields = [
            "nome",
            "descricao",
            "ativo",
        ]

        widgets = {

            "nome": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Digite o nome da coleção"
                }
            ),

            "descricao": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Descrição opcional"
                }
            ),
        }

    def clean_nome(self):

        nome = self.cleaned_data["nome"].strip()

        existe = Colecao.objects.filter(
            nome__iexact=nome
        )

        if self.instance.pk:
            existe = existe.exclude(
                pk=self.instance.pk
            )

        if existe.exists():
            raise ValidationError(
                "Já existe uma coleção com este nome."
            )

        return nome