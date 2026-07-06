from django import forms

from compras.models import Compra


class CompraForm(forms.ModelForm):
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
            "data_compra": forms.DateInput(attrs={"type": "date"}),
            "previsao_entrega": forms.DateInput(attrs={"type": "date"}),
            "observacoes": forms.Textarea(attrs={"rows": 4}),
        }