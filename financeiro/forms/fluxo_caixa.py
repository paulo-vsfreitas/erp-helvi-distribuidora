from django import forms
from django.utils import timezone

from financeiro.models import (
    CategoriaFinanceira,
    ContaFinanceira,
    MovimentacaoFinanceira,
)


class FluxoCaixaFiltroForm(forms.Form):
    STATUS_VALIDAS = "validas"
    STATUS_ESTORNADAS = "estornadas"
    STATUS_TODAS = "todas"

    STATUS_CHOICES = [
        (STATUS_VALIDAS, "Somente válidas"),
        (STATUS_ESTORNADAS, "Somente estornadas"),
        (STATUS_TODAS, "Todas"),
    ]

    data_inicial = forms.DateField(
        label="Data inicial",
        required=False,
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control",
            },
        ),
    )

    data_final = forms.DateField(
        label="Data final",
        required=False,
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control",
            },
        ),
    )

    conta_financeira = forms.ModelChoiceField(
        label="Conta financeira",
        queryset=ContaFinanceira.objects.none(),
        required=False,
        empty_label="Todas as contas",
        widget=forms.Select(
            attrs={
                "class": "form-select",
            },
        ),
    )

    categoria = forms.ModelChoiceField(
        label="Categoria",
        queryset=CategoriaFinanceira.objects.none(),
        required=False,
        empty_label="Todas as categorias",
        widget=forms.Select(
            attrs={
                "class": "form-select",
            },
        ),
    )

    tipo = forms.ChoiceField(
        label="Tipo",
        required=False,
        choices=[],
        widget=forms.Select(
            attrs={
                "class": "form-select",
            },
        ),
    )

    status = forms.ChoiceField(
        label="Situação",
        required=False,
        choices=STATUS_CHOICES,
        initial=STATUS_VALIDAS,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            },
        ),
    )

    busca = forms.CharField(
        label="Busca",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": (
                    "Descrição, origem, conta ou categoria"
                ),
            },
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        hoje = timezone.localdate()
        primeiro_dia_mes = hoje.replace(day=1)

        self.fields["conta_financeira"].queryset = (
            ContaFinanceira.objects
            .filter(ativo=True)
            .order_by("-conta_padrao", "nome")
        )

        self.fields["categoria"].queryset = (
            CategoriaFinanceira.objects
            .filter(ativo=True)
            .order_by("tipo", "nome")
        )

        self.fields["tipo"].choices = [
            ("", "Todos os tipos"),
            *MovimentacaoFinanceira.TIPO_CHOICES,
        ]

        if not self.is_bound:
            self.fields["data_inicial"].initial = (
                primeiro_dia_mes
            )

            self.fields["data_final"].initial = hoje

            self.fields["status"].initial = (
                self.STATUS_VALIDAS
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
            self.add_error(
                "data_final",
                (
                    "A data final não pode ser anterior "
                    "à data inicial."
                ),
            )

        return cleaned_data