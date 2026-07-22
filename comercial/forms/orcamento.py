from datetime import date
from decimal import Decimal, InvalidOperation

from django import forms
from django.db.models import Q

from clientes.models import Cliente
from comercial.models import Orcamento


class OrcamentoForm(forms.ModelForm):
    desconto = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "inputmode": "decimal",
                "placeholder": "0,00",
                "autocomplete": "off",
            }
        ),
    )

    frete = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "inputmode": "decimal",
                "placeholder": "0,00",
                "autocomplete": "off",
            }
        ),
    )

    class Meta:
        model = Orcamento

        fields = [
            "cliente",
            "cliente_nome",
            "cliente_documento",
            "cliente_telefone",
            "cliente_email",
            "data_validade",
            "desconto",
            "frete",
            "condicoes_comerciais",
            "observacoes",
        ]

        widgets = {
            "cliente": forms.HiddenInput(
                attrs={
                    "id": "cliente-id",
                }
            ),
            "cliente_nome": forms.TextInput(
                attrs={
                    "id": "cliente-search",
                    "class": "form-control",
                    "placeholder": (
                        "Digite o nome do cliente, interessado ou ótica..."
                    ),
                    "autocomplete": "off",
                }
            ),
            "cliente_documento": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "CPF ou CNPJ",
                    "autocomplete": "off",
                }
            ),
            "cliente_telefone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Telefone ou WhatsApp",
                    "autocomplete": "off",
                }
            ),
            "cliente_email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "cliente@email.com",
                    "autocomplete": "off",
                }
            ),
            "data_validade": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "type": "date",
                    "class": "form-control",
                },
            ),
            "condicoes_comerciais": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": (
                        "Informe formas de pagamento, prazo de entrega "
                        "e demais condições comerciais."
                    ),
                }
            ),
            "observacoes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": (
                        "Observações internas ou destinadas ao cliente."
                    ),
                }
            ),
        }

        error_messages = {
            "cliente_nome": {
                "required": "Informe o nome do cliente ou interessado.",
            },
            "cliente_email": {
                "invalid": "Informe um endereço de e-mail válido.",
            },
            "data_validade": {
                "required": "Informe a data de validade do orçamento.",
                "invalid": "Informe uma data de validade válida.",
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        cliente_atual_id = getattr(
            self.instance,
            "cliente_id",
            None,
        )

        filtro_clientes = Q(ativo=True)

        if cliente_atual_id:
            filtro_clientes |= Q(pk=cliente_atual_id)

        self.fields["cliente"].queryset = (
            Cliente.objects
            .filter(filtro_clientes)
            .distinct()
            .order_by("nome_fantasia", "razao_social")
        )

        self.fields["cliente"].required = False
        self.fields["cliente_nome"].required = True
        self.fields["cliente_documento"].required = False
        self.fields["cliente_telefone"].required = False
        self.fields["cliente_email"].required = False
        self.fields["condicoes_comerciais"].required = False
        self.fields["observacoes"].required = False

        self.fields["data_validade"].input_formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
        ]

        for campo in self.fields.values():
            if not isinstance(campo.widget, forms.HiddenInput):
                campo.widget.attrs.setdefault("class", "form-control")

    @staticmethod
    def limpar_decimal(valor):
        if valor in [None, ""]:
            return Decimal("0.00")

        valor_normalizado = str(valor).strip().replace(" ", "")

        if "," in valor_normalizado:
            valor_normalizado = (
                valor_normalizado
                .replace(".", "")
                .replace(",", ".")
            )

        try:
            return Decimal(valor_normalizado)
        except (InvalidOperation, ValueError, TypeError):
            raise forms.ValidationError(
                "Informe um valor válido."
            )

    def clean_cliente(self):
        cliente = self.cleaned_data.get("cliente")

        if not cliente:
            return None

        cliente_atual_id = getattr(
            self.instance,
            "cliente_id",
            None,
        )

        if not cliente.ativo and cliente.pk != cliente_atual_id:
            raise forms.ValidationError(
                "O cliente selecionado está inativo."
            )

        return cliente

    def clean_cliente_nome(self):
        cliente_nome = (
            self.cleaned_data.get("cliente_nome") or ""
        ).strip()

        if not cliente_nome:
            raise forms.ValidationError(
                "Informe o nome do cliente ou interessado."
            )

        return cliente_nome

    def clean_cliente_documento(self):
        return (
            self.cleaned_data.get("cliente_documento") or ""
        ).strip()

    def clean_cliente_telefone(self):
        return (
            self.cleaned_data.get("cliente_telefone") or ""
        ).strip()

    def clean_cliente_email(self):
        return (
            self.cleaned_data.get("cliente_email") or ""
        ).strip().lower()

    def clean_data_validade(self):
        data_validade = self.cleaned_data.get("data_validade")

        if not data_validade:
            raise forms.ValidationError(
                "Informe a data de validade do orçamento."
            )

        if not self.instance.pk and data_validade < date.today():
            raise forms.ValidationError(
                "A validade do orçamento não pode ser anterior à data atual."
            )

        return data_validade

    def clean_desconto(self):
        desconto = self.limpar_decimal(
            self.cleaned_data.get("desconto")
        )

        if desconto < 0:
            raise forms.ValidationError(
                "O desconto não pode ser negativo."
            )

        return desconto

    def clean_frete(self):
        frete = self.limpar_decimal(
            self.cleaned_data.get("frete")
        )

        if frete < 0:
            raise forms.ValidationError(
                "O frete não pode ser negativo."
            )

        return frete