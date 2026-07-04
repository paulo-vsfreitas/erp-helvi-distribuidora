from django import forms


class InventarioForm(forms.Form):
    observacao = forms.CharField(
        label="Observação",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Observações sobre este inventário",
            }
        ),
    )