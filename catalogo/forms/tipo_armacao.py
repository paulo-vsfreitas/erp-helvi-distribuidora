from django import forms

from catalogo.models import TipoArmacao


class TipoArmacaoForm(forms.ModelForm):
    class Meta:
        model = TipoArmacao
        fields = [
            "nome",
            "descricao",
            "ativo",
        ]

        widgets = {
            "nome": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex: Acetato, Metal, Nylon, Parafusada",
            }),
            "descricao": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Descrição do tipo de armação",
            }),
            "ativo": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }

        labels = {
            "nome": "Nome",
            "descricao": "Descrição",
            "ativo": "Tipo ativo",
        }

    def clean_nome(self):
        nome = self.cleaned_data.get("nome")

        if nome:
            nome = nome.strip().upper()

        return nome