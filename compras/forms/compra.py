from decimal import Decimal, InvalidOperation

from django import forms

from compras.models import Compra


class CompraForm(forms.ModelForm):
    frete = forms.CharField(required=False)

    class Meta:
        model = Compra
        fields = [
            "fornecedor_nome",
            "fornecedor_documento",
            "fornecedor_telefone",
            "data_compra",
            "previsao_entrega",
            "frete",
            "observacoes",
        ]

        widgets = {
            "fornecedor_documento": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "inputmode": "numeric",
                    "autocomplete": "off",
                    "placeholder": "Somente números",
                }
            ),
            "fornecedor_telefone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "inputmode": "numeric",
                    "autocomplete": "off",
                    "placeholder": "(11) 99999-9999",
                }
            ),
            "data_compra": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "type": "date",
                    "class": "form-control",
                },
            ),
            "previsao_entrega": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "type": "date",
                    "class": "form-control",
                },
            ),
            "observacoes": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": "form-control",
                },
            ),
            "frete": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "inputmode": "decimal",
                    "placeholder": "0,00",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["data_compra"].input_formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
        ]
        self.fields["previsao_entrega"].input_formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
        ]

        self.fields["previsao_entrega"].required = False
        self.fields["fornecedor_documento"].required = False
        self.fields["fornecedor_telefone"].required = False
        self.fields["observacoes"].required = False

        for campo in self.fields.values():
            campo.widget.attrs.setdefault(
                "class",
                "form-control",
            )

    def limpar_decimal(self, valor):
        if valor in [None, ""]:
            return Decimal("0.00")

        valor = (
            str(valor)
            .strip()
            .replace(".", "")
            .replace(",", ".")
        )

        try:
            return Decimal(valor)
        except InvalidOperation:
            raise forms.ValidationError(
                "Informe um valor válido."
            )

    def somente_numeros(self, valor):
        return "".join(
            filter(
                str.isdigit,
                str(valor or ""),
            )
        )

    def clean_frete(self):
        frete = self.limpar_decimal(
            self.cleaned_data.get("frete")
        )

        if frete < 0:
            raise forms.ValidationError(
                "O frete não pode ser negativo."
            )

        return frete

    def clean_fornecedor_documento(self):
        return self.somente_numeros(
            self.cleaned_data.get(
                "fornecedor_documento"
            )
        )

    def clean_fornecedor_telefone(self):
        return self.somente_numeros(
            self.cleaned_data.get(
                "fornecedor_telefone"
            )
        )