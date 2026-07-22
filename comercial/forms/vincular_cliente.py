from django import forms

from comercial.models import Orcamento


class VincularClienteForm(forms.ModelForm):
    class Meta:
        model = Orcamento
        fields = [
            "cliente",
        ]
        widgets = {
            "cliente": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
        }

    def clean_cliente(self):
        cliente = self.cleaned_data.get("cliente")

        if not cliente:
            raise forms.ValidationError(
                "Selecione um cliente cadastrado."
            )

        return cliente