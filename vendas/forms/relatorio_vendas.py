from django import forms
from django.contrib.auth import get_user_model

from clientes.models import Cliente
from vendas.models import Venda


class RelatorioVendasFiltroForm(forms.Form):
    data_inicial = forms.DateField(
        required=False,
        label="Data inicial",
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "type": "date",
            },
        ),
    )

    data_final = forms.DateField(
        required=False,
        label="Data final",
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "type": "date",
            },
        ),
    )

    cliente = forms.ModelChoiceField(
        required=False,
        label="Cliente",
        queryset=Cliente.objects.none(),
        empty_label="Todos os clientes",
        widget=forms.Select(
            attrs={
                "class": "form-select",
            },
        ),
    )

    vendedor = forms.ModelChoiceField(
        required=False,
        label="Vendedor",
        queryset=get_user_model().objects.none(),
        empty_label="Todos os vendedores",
        widget=forms.Select(
            attrs={
                "class": "form-select",
            },
        ),
    )

    forma_pagamento = forms.ChoiceField(
        required=False,
        label="Forma de pagamento",
        choices=[("", "Todas as formas")]
        + Venda.FORMA_PAGAMENTO_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            },
        ),
    )

    status = forms.ChoiceField(
        required=False,
        label="Status da venda",
        choices=[("", "Todos os status")]
        + Venda.STATUS_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            },
        ),
    )

    status_pagamento = forms.ChoiceField(
        required=False,
        label="Status do pagamento",
        choices=[("", "Todos os pagamentos")]
        + Venda.STATUS_PAGAMENTO_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            },
        ),
    )

    consumidor_final = forms.ChoiceField(
        required=False,
        label="Tipo de cliente",
        choices=[
            ("", "Todos"),
            ("sim", "Consumidor Final"),
            ("nao", "Cliente cadastrado"),
        ],
        widget=forms.Select(
            attrs={
                "class": "form-select",
            },
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["cliente"].queryset = (
            Cliente.objects
            .filter(ativo=True)
            .order_by(
                "nome_fantasia",
                "razao_social",
            )
        )

        self.fields["vendedor"].queryset = (
            get_user_model().objects
            .filter(is_active=True)
            .order_by("first_name", "last_name", "username")
        )

    def clean(self):
        cleaned_data = super().clean()

        data_inicial = cleaned_data.get("data_inicial")
        data_final = cleaned_data.get("data_final")

        if (
            data_inicial
            and data_final
            and data_inicial > data_final
        ):
            raise forms.ValidationError(
                "A data inicial não pode ser posterior à data final."
            )

        return cleaned_data