from django import forms
from django.utils import timezone

from clientes.models import Cliente
from financeiro.models import CategoriaFinanceira, ContaReceber


class ContaReceberForm(forms.ModelForm):
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
        model = ContaReceber
        fields = [
            "descricao",
            "cliente",
            "nome_devedor",
            "documento_devedor",
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
                    "placeholder": (
                        "Ex.: Venda de mercadorias, prestação de serviço"
                    ),
                }
            ),
            "cliente": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "nome_devedor": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": (
                        "Informe quando não houver cliente vinculado"
                    ),
                }
            ),
            "documento_devedor": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "CPF ou CNPJ",
                    "inputmode": "numeric",
                    "autocomplete": "off",
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
                    "placeholder": (
                        "Informações adicionais sobre a conta."
                    ),
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        hoje = timezone.localdate()

        self.fields["data_emissao"].initial = hoje
        self.fields["primeiro_vencimento"].initial = hoje

        self.fields["cliente"].required = False
        self.fields["nome_devedor"].required = False
        self.fields["documento_devedor"].required = False
        self.fields["data_competencia"].required = False
        self.fields["observacoes"].required = False

        self.fields["categoria"].queryset = (
            CategoriaFinanceira.objects
            .filter(
                tipo=CategoriaFinanceira.TIPO_RECEITA,
                ativo=True,
            )
            .order_by("nome")
        )

        self.fields["cliente"].queryset = (
            Cliente.objects
            .filter(ativo=True)
            .order_by("pk")
        )

        self.fields["cliente"].empty_label = (
            "Sem cliente vinculado"
        )

        self.fields["categoria"].empty_label = (
            "Selecione uma categoria"
        )

    def clean_valor_total(self):
        valor_total = self.cleaned_data["valor_total"]

        if valor_total <= 0:
            raise forms.ValidationError(
                "O valor total deve ser maior que zero."
            )

        return valor_total

    def clean_documento_devedor(self):
        documento = self.cleaned_data.get(
            "documento_devedor",
            "",
        )

        return "".join(
            caractere
            for caractere in documento
            if caractere.isdigit()
        )

    def clean(self):
        cleaned_data = super().clean()

        cliente = cleaned_data.get("cliente")
        nome_devedor = (
            cleaned_data.get("nome_devedor") or ""
        ).strip()

        if not cliente and not nome_devedor:
            self.add_error(
                "nome_devedor",
                (
                    "Selecione um cliente ou informe "
                    "o nome do devedor."
                ),
            )

        if cliente and not nome_devedor:
            cleaned_data["nome_devedor"] = str(cliente)

        return cleaned_data