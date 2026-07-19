from django import forms
from django.utils import timezone

from financeiro.models import CategoriaFinanceira, ContaPagar
from fornecedores.models import Fornecedor


class ContaPagarForm(forms.ModelForm):
    quantidade_parcelas = forms.IntegerField(
        label="Quantidade de parcelas",
        min_value=1,
        initial=1,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "min": "1",
                "step": "1",
            }
        ),
    )

    primeiro_vencimento = forms.DateField(
        label="Primeiro vencimento",
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "type": "date",
            }
        ),
    )

    class Meta:
        model = ContaPagar
        fields = [
            "descricao",
            "fornecedor",
            "categoria",
            "data_emissao",
            "data_competencia",
            "valor_total",
            "observacoes",
        ]

        widgets = {
            "descricao": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex.: Aluguel da sala comercial",
                }
            ),
            "fornecedor": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "categoria": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "data_emissao": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "data_competencia": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "valor_total": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0.01",
                    "step": "0.01",
                    "placeholder": "0,00",
                }
            ),
            "observacoes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Informações adicionais sobre a conta.",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["data_emissao"].initial = timezone.localdate()
        self.fields["primeiro_vencimento"].initial = timezone.localdate()

        self.fields["fornecedor"].required = False
        self.fields["data_competencia"].required = False
        self.fields["observacoes"].required = False

        self.fields["categoria"].queryset = (
            CategoriaFinanceira.objects
            .filter(
                tipo=CategoriaFinanceira.TIPO_DESPESA,
                ativo=True,
            )
            .order_by("nome")
        )

        self.fields["fornecedor"].queryset = (
            Fornecedor.objects
            .filter(ativo=True)
            .order_by("nome_razao_social")
        )

        self.fields["fornecedor"].empty_label = "Sem fornecedor vinculado"
        self.fields["categoria"].empty_label = "Selecione uma categoria"

    def clean_valor_total(self):
        valor_total = self.cleaned_data["valor_total"]

        if valor_total <= 0:
            raise forms.ValidationError(
                "O valor total deve ser maior que zero."
            )

        return valor_total