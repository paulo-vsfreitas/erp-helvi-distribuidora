from django import forms
from decimal import Decimal

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
            "tipo_entrega",
            "entrega_cep",
            "entrega_logradouro",
            "entrega_numero",
            "entrega_complemento",
            "entrega_bairro",
            "entrega_cidade",
            "entrega_estado",
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
            "tipo_entrega": forms.Select(attrs={"class": "form-select"}),
            "entrega_cep": forms.TextInput(attrs={
                "class": "form-control", "placeholder": "00000-000",
                "data-mask": "cep", "data-cep-autocomplete": "true",
                "data-logradouro-target": "id_entrega_logradouro",
                "data-bairro-target": "id_entrega_bairro",
                "data-cidade-target": "id_entrega_cidade",
                "data-estado-target": "id_entrega_estado",
                "data-complemento-target": "id_entrega_complemento",
                "data-numero-target": "id_entrega_numero",
            }),
            "entrega_logradouro": forms.TextInput(attrs={"class": "form-control"}),
            "entrega_numero": forms.TextInput(attrs={"class": "form-control"}),
            "entrega_complemento": forms.TextInput(attrs={"class": "form-control"}),
            "entrega_bairro": forms.TextInput(attrs={"class": "form-control"}),
            "entrega_cidade": forms.TextInput(attrs={"class": "form-control"}),
            "entrega_estado": forms.TextInput(attrs={"class": "form-control", "maxlength": 2}),
            "observacoes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),
    }

    def __init__(self, *args, **kwargs):
        if args and args[0] is not None:
            dados = args[0].copy()
            for nome in ("desconto", "frete"):
                valor = str(dados.get(nome, "")).strip()
                if "," in valor:
                    dados[nome] = valor.replace(".", "").replace(",", ".")
            args = (dados, *args[1:])
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
        self.fields["desconto"].localize = True
        self.fields["frete"].localize = True
        self.fields["observacoes"].required = False
        self.fields["tipo_entrega"].required = False
        for nome in (
            "entrega_cep", "entrega_logradouro", "entrega_numero",
            "entrega_complemento", "entrega_bairro", "entrega_cidade",
            "entrega_estado",
        ):
            self.fields[nome].required = False

    def clean(self):
        dados = super().clean()
        dados["tipo_entrega"] = dados.get("tipo_entrega") or Venda.ENTREGA_RETIRADA
        if dados.get("tipo_entrega") == Venda.ENTREGA_ENVIO:
            for campo in ("entrega_logradouro", "entrega_numero", "entrega_cidade", "entrega_estado"):
                if not dados.get(campo):
                    self.add_error(campo, "Informe este dado para a entrega.")
        else:
            dados["frete"] = Decimal("0.00")
        return dados
