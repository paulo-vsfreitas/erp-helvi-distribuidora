from decimal import Decimal

from django import forms
from django.utils import timezone

from financeiro.models import ContaFinanceira, RecebimentoConta


class RecebimentoContaForm(forms.ModelForm):
    class Meta:
        model = RecebimentoConta

        fields = [
            "conta_financeira",
            "data_recebimento",
            "valor",
            "juros",
            "multa",
            "desconto",
            "forma_recebimento",
            "observacao",
        ]

        labels = {
            "conta_financeira": "Conta financeira",
            "data_recebimento": "Data do recebimento",
            "valor": "Valor recebido",
            "juros": "Juros",
            "multa": "Multa",
            "desconto": "Desconto",
            "forma_recebimento": "Forma de recebimento",
            "observacao": "Observação",
        }

        widgets = {
            "conta_financeira": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "data_recebimento": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "class": "form-control",
                    "type": "date",
                },
            ),
            "valor": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0.01",
                    "placeholder": "0,00",
                    "autocomplete": "off",
                }
            ),
            "juros": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "0,00",
                    "autocomplete": "off",
                }
            ),
            "multa": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "0,00",
                    "autocomplete": "off",
                }
            ),
            "desconto": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "0,00",
                    "autocomplete": "off",
                }
            ),
            "forma_recebimento": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "observacao": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": (
                        "Informações adicionais sobre o recebimento..."
                    ),
                }
            ),
        }

    def __init__(self, *args, parcela=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.parcela = parcela

        self.fields["conta_financeira"].queryset = (
            ContaFinanceira.objects
            .filter(ativo=True)
            .order_by("nome")
        )

        self.fields["conta_financeira"].empty_label = (
            "Selecione a conta financeira"
        )

        self.fields["forma_recebimento"].empty_label = (
            "Selecione a forma de recebimento"
        )

        self.fields["data_recebimento"].input_formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
        ]

        if not self.is_bound:
            self.fields["data_recebimento"].initial = (
                timezone.localdate()
            )

            self.fields["juros"].initial = Decimal("0.00")
            self.fields["multa"].initial = Decimal("0.00")
            self.fields["desconto"].initial = Decimal("0.00")

            if parcela is not None:
                self.fields["valor"].initial = parcela.saldo

    def clean_valor(self):
        valor = self.cleaned_data.get("valor")

        if valor is None:
            return valor

        if valor <= 0:
            raise forms.ValidationError(
                "O valor recebido deve ser maior que zero."
            )

        if self.parcela is not None and valor > self.parcela.saldo:
            raise forms.ValidationError(
                (
                    "O valor recebido não pode ser maior que "
                    f"o saldo da parcela, de R$ "
                    f"{self.parcela.saldo:.2f}."
                )
            )

        return valor

    def clean_juros(self):
        juros = self.cleaned_data.get("juros")

        if juros is None:
            return Decimal("0.00")

        if juros < 0:
            raise forms.ValidationError(
                "Os juros não podem ser negativos."
            )

        return juros

    def clean_multa(self):
        multa = self.cleaned_data.get("multa")

        if multa is None:
            return Decimal("0.00")

        if multa < 0:
            raise forms.ValidationError(
                "A multa não pode ser negativa."
            )

        return multa

    def clean_desconto(self):
        desconto = self.cleaned_data.get("desconto")

        if desconto is None:
            return Decimal("0.00")

        if desconto < 0:
            raise forms.ValidationError(
                "O desconto não pode ser negativo."
            )

        return desconto

    def clean(self):
        cleaned_data = super().clean()

        valor = cleaned_data.get("valor") or Decimal("0.00")
        juros = cleaned_data.get("juros") or Decimal("0.00")
        multa = cleaned_data.get("multa") or Decimal("0.00")
        desconto = cleaned_data.get("desconto") or Decimal("0.00")

        valor_movimentado = valor + juros + multa - desconto

        if valor_movimentado <= 0:
            self.add_error(
                "desconto",
                (
                    "O desconto não pode resultar em um valor "
                    "movimentado igual ou menor que zero."
                ),
            )

        return cleaned_data