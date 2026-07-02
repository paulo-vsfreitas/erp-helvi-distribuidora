from django import forms

from produtos.models import Produto


class AjusteEstoqueForm(forms.Form):
    produto = forms.ModelChoiceField(
        queryset=Produto.objects.filter(ativo=True).order_by("modelo"),
        label="Produto",
        widget=forms.Select(
            attrs={
                "class": "form-control",
            }
        ),
    )

    quantidade_correta = forms.IntegerField(
        label="Quantidade correta",
        min_value=0,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "Informe a quantidade física correta",
            }
        ),
    )

    motivo = forms.CharField(
        label="Motivo do ajuste",
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ex: conferência, perda, divergência, erro de lançamento",
            }
        ),
    )

    observacao = forms.CharField(
        label="Observação",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Detalhes adicionais sobre o ajuste",
            }
        ),
    )