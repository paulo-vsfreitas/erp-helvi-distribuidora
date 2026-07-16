from decimal import Decimal

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from financeiro.models import (
    BaixaPagar,
    ContaFinanceira,
)


class BaixaPagarForm(forms.ModelForm):
    class Meta:
        model = BaixaPagar

        fields = [
            "conta_financeira",
            "data_pagamento",
            "valor",
            "juros",
            "multa",
            "desconto",
            "forma_pagamento",
            "observacao",
        ]

        widgets = {
            "conta_financeira": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "data_pagamento": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                },
                format="%Y-%m-%d",
            ),
            "valor": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0.01",
                    "placeholder": "0,00",
                }
            ),
            "juros": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "0,00",
                }
            ),
            "multa": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "0,00",
                }
            ),
            "desconto": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "0,00",
                }
            ),
            "forma_pagamento": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "observacao": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Observação opcional",
                }
            ),
        }

    def __init__(self, *args, parcela=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.parcela = parcela

        self.fields["conta_financeira"].queryset = (
            ContaFinanceira.objects
            .filter(ativo=True)
            .order_by("-conta_padrao", "nome")
        )

        conta_padrao = (
            ContaFinanceira.objects
            .filter(
                ativo=True,
                conta_padrao=True,
            )
            .first()
        )

        if conta_padrao and not self.is_bound:
            self.fields["conta_financeira"].initial = conta_padrao

        if not self.is_bound:
            self.fields["data_pagamento"].initial = timezone.localdate()

            self.fields["juros"].initial = Decimal("0.00")
            self.fields["multa"].initial = Decimal("0.00")
            self.fields["desconto"].initial = Decimal("0.00")

            if parcela:
                self.fields["valor"].initial = parcela.saldo

        self.fields["data_pagamento"].input_formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
        ]

    def clean_conta_financeira(self):
        conta_financeira = self.cleaned_data["conta_financeira"]

        if not conta_financeira.ativo:
            raise ValidationError(
                "A conta financeira selecionada está inativa."
            )

        return conta_financeira

    def clean_data_pagamento(self):
        data_pagamento = self.cleaned_data["data_pagamento"]

        if data_pagamento > timezone.localdate():
            raise ValidationError(
                "A data do pagamento não pode estar no futuro."
            )

        return data_pagamento

    def clean(self):
        cleaned_data = super().clean()

        valor = cleaned_data.get("valor")
        juros = cleaned_data.get("juros") or Decimal("0.00")
        multa = cleaned_data.get("multa") or Decimal("0.00")
        desconto = cleaned_data.get("desconto") or Decimal("0.00")

        if valor is None:
            return cleaned_data

        if valor <= 0:
            self.add_error(
                "valor",
                "O valor principal deve ser maior que zero.",
            )

        if juros < 0:
            self.add_error(
                "juros",
                "O valor dos juros não pode ser negativo.",
            )

        if multa < 0:
            self.add_error(
                "multa",
                "O valor da multa não pode ser negativo.",
            )

        if desconto < 0:
            self.add_error(
                "desconto",
                "O desconto não pode ser negativo.",
            )

        if desconto > valor + juros + multa:
            self.add_error(
                "desconto",
                (
                    "O desconto não pode ser maior que a soma "
                    "do valor principal, juros e multa."
                ),
            )

        if self.parcela:
            if self.parcela.status == self.parcela.STATUS_CANCELADA:
                raise ValidationError(
                    "Não é possível registrar pagamento "
                    "em uma parcela cancelada."
                )

            if self.parcela.status == self.parcela.STATUS_PAGA:
                raise ValidationError(
                    "Esta parcela já está totalmente paga."
                )

            if valor > self.parcela.saldo:
                self.add_error(
                    "valor",
                    (
                        "O valor principal informado é maior "
                        "que o saldo da parcela."
                    ),
                )

        valor_movimentado = (
            valor
            + juros
            + multa
            - desconto
        )

        if valor_movimentado <= 0:
            raise ValidationError(
                "O valor efetivamente movimentado deve ser maior que zero."
            )

        return cleaned_data