from django import forms


class ImportacaoProdutosForm(forms.Form):
    arquivo = forms.FileField(
        label="Arquivo de produtos",
        help_text="Formatos aceitos: Excel (.xlsx) ou CSV (.csv).",
        widget=forms.ClearableFileInput(
            attrs={
                "class": "form-control",
                "accept": ".xlsx,.csv",
            }
        ),
    )

    def clean_arquivo(self):
        arquivo = self.cleaned_data["arquivo"]

        nome = arquivo.name.lower()

        if not nome.endswith((".xlsx", ".csv")):
            raise forms.ValidationError(
                "Envie um arquivo Excel (.xlsx) ou CSV (.csv)."
            )

        return arquivo