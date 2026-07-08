from decimal import Decimal, InvalidOperation

from django import forms

from compras.models import PagamentoCompra


class PagamentoCompraForm(forms.ModelForm):
    valor = forms.CharField(required=True)

    class Meta:
        model = PagamentoCompra
        fields = [
            "valor",
            "forma_pagamento",
            "observacao",
        ]

        widgets = {
            "forma_pagamento": forms.Select(attrs={"class": "form-select"}),
            "observacao": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        self.compra = kwargs.pop("compra", None)
        super().__init__(*args, **kwargs)

        self.fields["valor"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Ex: 150,00",
            "inputmode": "decimal",
        })

    def clean_valor(self):
        valor = self.cleaned_data.get("valor")

        try:
            valor = Decimal(str(valor).replace(".", "").replace(",", "."))
        except InvalidOperation:
            raise forms.ValidationError("Informe um valor válido.")

        if valor <= 0:
            raise forms.ValidationError("O valor deve ser maior que zero.")

        if self.compra and valor > self.compra.saldo_a_pagar:
            raise forms.ValidationError("O valor informado é maior que o saldo a pagar.")

        return valor