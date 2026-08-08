from django import forms

from produtos.models import Produto, VariacaoCor


class EntradaEstoqueForm(forms.Form):
    produto = forms.ModelChoiceField(
        queryset=Produto.objects.filter(
            ativo=True
        ).order_by("modelo"),
        label="Produto",
        widget=forms.Select(
            attrs={"class": "form-select"}
        ),
    )

    variacao_cor = forms.ModelChoiceField(
        queryset=VariacaoCor.objects.none(),
        required=False,
        label="Cor / Variação",
        widget=forms.Select(
            attrs={"class": "form-select"}
        ),
    )

    quantidade = forms.IntegerField(
        min_value=1,
        label="Quantidade",
        widget=forms.NumberInput(
            attrs={"class": "form-control"}
        ),
    )

    origem = forms.CharField(
        required=False,
        label="Origem",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": (
                    "Ex: Compra, ajuste manual, fornecedor..."
                ),
            }
        ),
    )

    local = forms.CharField(
        required=False,
        initial="Estoque Principal",
        label="Local",
        widget=forms.TextInput(
            attrs={"class": "form-control"}
        ),
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        produto_id = (
            self.data.get("produto")
            or self.initial.get("produto")
        )

        if produto_id:
            self.fields["variacao_cor"].queryset = (
                VariacaoCor.objects
                .filter(produto_id=produto_id)
                .order_by("codigo", "nome")
            )