from django import forms
from django.core.exceptions import ValidationError

from catalogo.models import Marca


class MarcaForm(forms.ModelForm):

    class Meta:
        model = Marca

        fields = [
            "nome",
            "descricao",
            "ativo",
        ]

        widgets = {
            "nome": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Digite o nome da marca"
            }),

            "descricao": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Descrição opcional"
            }),
        }

    def clean_nome(self):
        nome = self.cleaned_data["nome"].strip()

        existe = Marca.objects.filter(nome__iexact=nome)

        if self.instance.pk:
            existe = existe.exclude(pk=self.instance.pk)

        if existe.exists():
            raise ValidationError("Já existe uma marca com este nome.")

        return nome