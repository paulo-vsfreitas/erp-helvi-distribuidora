from django import forms

from financeiro.models import ContaFinanceira
from vendas.models import Venda


class VendaForm(forms.ModelForm):
    class Meta:
        model = Venda
        fields = [
            "cliente",
            "forma_pagamento",
            "conta_financeira",
            "desconto",
            "frete",
            "observacoes",
        ]

        widgets = {
            "cliente": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "forma_pagamento": forms.Select(
                attrs={
                    "class": "form-select",
                    "id": "id_forma_pagamento",
                }
            ),
            "conta_financeira": forms.Select(
                attrs={
                    "class": "form-select",
                    "id": "id_conta_financeira",
                }
            ),
            "desconto": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "inputmode": "decimal",
                    "placeholder": "0,00",
                    "autocomplete": "off",
                }
            ),
            "frete": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "inputmode": "decimal",
                    "placeholder": "0,00",
                    "autocomplete": "off",
                }
            ),
            "observacoes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["cliente"].required = False
        self.fields["cliente"].empty_label = (
            "Selecione um cliente..."
        )

        self.fields["forma_pagamento"].required = False
        self.fields["forma_pagamento"].empty_label = (
            "Selecione a forma de pagamento..."
        )

        self.fields["conta_financeira"].required = False
        self.fields["conta_financeira"].empty_label = (
            "Selecione a conta financeira..."
        )
        self.fields["conta_financeira"].queryset = (
            ContaFinanceira.objects
            .filter(ativo=True)
            .order_by(
                "-conta_padrao",
                "nome",
            )
        )

        self.fields["desconto"].required = False
        self.fields["frete"].required = False
        self.fields["observacoes"].required = False