from django import forms
from django.core.exceptions import ValidationError

from financeiro.models import ContaFinanceira


class ContaFinanceiraForm(forms.ModelForm):
    class Meta:
        model = ContaFinanceira

        fields = [
            "nome",
            "tipo",
            "instituicao",
            "agencia",
            "numero_conta",
            "identificador",
            "saldo_inicial",
            "data_saldo_inicial",
            "conta_padrao",
            "observacoes",
            "ativo",
        ]

        widgets = {
            "nome": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex.: Banco Inter, Caixa Geral ou InfinitePay",
                    "autofocus": True,
                }
            ),
            "tipo": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "instituicao": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex.: Banco Inter, InfinitePay ou Mercado Pago",
                }
            ),
            "agencia": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Agência",
                }
            ),
            "numero_conta": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Número da conta",
                }
            ),
            "identificador": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": (
                        "Chave Pix, código da carteira, terminal "
                        "ou outro identificador"
                    ),
                }
            ),
            "saldo_inicial": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "0,00",
                }
            ),
            "data_saldo_inicial": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                },
                format="%Y-%m-%d",
            ),
            "conta_padrao": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
            "observacoes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Observações opcionais",
                }
            ),
            "ativo": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["data_saldo_inicial"].input_formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
        ]

    def clean_nome(self):
        nome = self.cleaned_data["nome"].strip()

        contas = ContaFinanceira.objects.filter(
            nome__iexact=nome,
        )

        if self.instance.pk:
            contas = contas.exclude(pk=self.instance.pk)

        if contas.exists():
            raise ValidationError(
                "Já existe uma conta financeira com este nome."
            )

        return nome

    def clean(self):
        cleaned_data = super().clean()

        tipo = cleaned_data.get("tipo")
        saldo_inicial = cleaned_data.get("saldo_inicial")
        conta_padrao = cleaned_data.get("conta_padrao")
        ativo = cleaned_data.get("ativo")

        if saldo_inicial is not None and saldo_inicial < 0:
            self.add_error(
                "saldo_inicial",
                "O saldo inicial não pode ser negativo.",
            )

        if conta_padrao and not ativo:
            raise ValidationError(
                "Esta conta não pode ser inativada. "
                "Defina outra conta financeira como padrão antes de inativá-la."
            )

        if tipo == ContaFinanceira.TIPO_CAIXA:
            cleaned_data["agencia"] = ""
            cleaned_data["numero_conta"] = ""

        return cleaned_data