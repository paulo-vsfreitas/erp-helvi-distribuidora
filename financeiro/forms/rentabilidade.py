from django import forms
from django.utils import timezone


class RentabilidadeFiltroForm(forms.Form):
    data_inicial = forms.DateField(
        label="Data inicial",
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )
    data_final = forms.DateField(
        label="Data final",
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )
    busca = forms.CharField(
        label="Busca",
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Número da venda, cliente, vendedor ou produto",
        }),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        hoje = timezone.localdate()
        self.fields["data_inicial"].initial = hoje.replace(day=1)
        self.fields["data_final"].initial = hoje

    def clean(self):
        dados = super().clean()
        if dados.get("data_inicial") and dados.get("data_final") and dados["data_inicial"] > dados["data_final"]:
            self.add_error("data_final", "A data final não pode ser anterior à data inicial.")
        return dados
