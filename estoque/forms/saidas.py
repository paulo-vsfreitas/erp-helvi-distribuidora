from django import forms

from produtos.models import Produto


class SaidaEstoqueForm(forms.Form):
    produto = forms.ModelChoiceField(
        queryset=Produto.objects.filter(ativo=True).order_by("modelo"),
        label="Produto",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    quantidade = forms.IntegerField(
        min_value=1,
        label="Quantidade",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )

    origem = forms.CharField(
        required=False,
        label="Origem",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ex: Venda, perda, devolução...",
            }
        ),
    )

    local = forms.CharField(
        required=False,
        initial="Estoque Principal",
        label="Local",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    observacao = forms.CharField(
        required=False,
        label="Observação",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
            }
        ),
    )
