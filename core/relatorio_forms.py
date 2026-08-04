from django import forms


class RelatorioAnaliticoFiltroForm(forms.Form):
    data_inicial = forms.DateField(required=False, label="Data inicial", widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}))
    data_final = forms.DateField(required=False, label="Data final", widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}))
    busca = forms.CharField(required=False, label="Pesquisar", widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Nome, código ou descrição"}))
    status = forms.ChoiceField(required=False, label="Status", choices=(("", "Todos"),), widget=forms.Select(attrs={"class": "form-select"}))
    por_pagina = forms.ChoiceField(
        required=False,
        label="Linhas por página",
        choices=(("25", "25"), ("50", "50"), ("100", "100")),
        initial="25",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    def __init__(self, *args, status_choices=(), **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["status"].choices = (("", "Todos"), *status_choices)
        if not status_choices:
            self.fields.pop("status")

    def clean(self):
        dados = super().clean()
        if dados.get("data_inicial") and dados.get("data_final") and dados["data_inicial"] > dados["data_final"]:
            raise forms.ValidationError("A data inicial não pode ser posterior à data final.")
        return dados
