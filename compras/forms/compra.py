from decimal import Decimal, InvalidOperation

from django import forms
from django.db.models import Q

from compras.models import Compra
from fornecedores.models import Fornecedor


class CompraForm(forms.ModelForm):
    frete = forms.CharField(required=False)

    class Meta:
        model = Compra

        fields = [
            "fornecedor",
            "data_compra",
            "previsao_entrega",
            "frete",
            "observacoes",
        ]

        widgets = {
            "fornecedor": forms.Select(
                attrs={
                    "class": "form-select",
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

        fornecedor_atual_id = getattr(
            self.instance,
            "fornecedor_id",
            None,
        )

        filtro_fornecedores = Q(ativo=True)

        # Mantém disponível um fornecedor que tenha sido inativado
        # depois de ter sido vinculado à compra.
        if fornecedor_atual_id:
            filtro_fornecedores |= Q(
                pk=fornecedor_atual_id
            )

        self.fields["fornecedor"].queryset = (
            Fornecedor.objects
            .filter(filtro_fornecedores)
            .distinct()
            .order_by(
                "nome_fantasia",
                "razao_social",
            )
        )

        self.fields["fornecedor"].empty_label = (
            "Selecione um fornecedor"
        )

        self.fields["data_compra"].input_formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
        ]

        self.fields["previsao_entrega"].input_formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
        ]

        self.fields["previsao_entrega"].required = False
        self.fields["observacoes"].required = False

        for campo in self.fields.values():
            campo.widget.attrs.setdefault(
                "class",
                "form-control",
            )

    def clean_fornecedor(self):
        fornecedor = self.cleaned_data.get(
            "fornecedor"
        )

        # Uma compra nova sempre precisa usar o cadastro oficial.
        if not self.instance.pk and not fornecedor:
            raise forms.ValidationError(
                "Selecione o fornecedor da compra."
            )

        # Compras antigas, criadas antes da integração, podem continuar
        # sem vínculo até que sejam associadas manualmente.
        return fornecedor

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

    def clean_frete(self):
        frete = self.limpar_decimal(
            self.cleaned_data.get("frete")
        )

        if frete < 0:
            raise forms.ValidationError(
                "O frete não pode ser negativo."
            )

        return frete