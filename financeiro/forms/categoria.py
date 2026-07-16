from django import forms
from django.core.exceptions import ValidationError

from financeiro.models import CategoriaFinanceira


class CategoriaFinanceiraForm(forms.ModelForm):
    class Meta:
        model = CategoriaFinanceira

        fields = [
            "nome",
            "tipo",
            "descricao",
            "ativo",
        ]

        widgets = {
            "nome": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Digite o nome da categoria",
                    "autofocus": True,
                }
            ),
            "tipo": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "descricao": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Descrição opcional",
                }
            ),
            "ativo": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }

    def clean_nome(self):
        nome = self.cleaned_data["nome"].strip()

        categorias = CategoriaFinanceira.objects.filter(
            nome__iexact=nome,
        )

        if self.instance.pk:
            categorias = categorias.exclude(pk=self.instance.pk)

        if categorias.exists():
            raise ValidationError(
                "Já existe uma categoria financeira com este nome."
            )

        return nome