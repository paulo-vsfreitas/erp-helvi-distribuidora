from django import forms

from produtos.models import Produto, VariacaoCor


class AjusteEstoqueForm(forms.Form):
    produto = forms.ModelChoiceField(
        queryset=Produto.objects.filter(
            ativo=True
        ).order_by("modelo"),
        label="Produto",
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    variacao_cor = forms.ModelChoiceField(
        queryset=VariacaoCor.objects.none(),
        required=False,
        label="Cor / Variação",
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    quantidade_correta = forms.IntegerField(
        label="Quantidade correta",
        min_value=0,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": (
                    "Informe a quantidade física correta"
                ),
            }
        ),
    )

    motivo = forms.CharField(
        label="Motivo do ajuste",
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": (
                    "Ex: conferência, perda, divergência, "
                    "erro de lançamento"
                ),
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
                "placeholder": (
                    "Detalhes adicionais sobre o ajuste"
                ),
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
            try:
                produto_id = int(produto_id)
            except (TypeError, ValueError):
                return

            self.fields["variacao_cor"].queryset = (
                VariacaoCor.objects
                .filter(produto_id=produto_id)
                .order_by("codigo", "nome")
            )