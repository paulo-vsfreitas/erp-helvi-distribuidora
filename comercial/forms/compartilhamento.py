from django import forms

from comercial.models import CompartilhamentoOrcamento


class CompartilhamentoOrcamentoForm(forms.Form):
    canal = forms.ChoiceField(
        choices=CompartilhamentoOrcamento.Canal.choices,
        widget=forms.RadioSelect,
    )

    telefone = forms.CharField(
        required=False,
        max_length=20,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "(11) 99999-9999",
                "autocomplete": "off",
            }
        ),
    )

    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "cliente@email.com",
                "autocomplete": "off",
            }
        ),
    )

    assunto = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
    )

    mensagem = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 8,
            }
        ),
    )

    marcar_enviado = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-check-input",
            }
        ),
    )

    def clean(self):
        dados = super().clean()
        canal = dados.get("canal")

        if canal == CompartilhamentoOrcamento.Canal.WHATSAPP:
            if not (dados.get("telefone") or "").strip():
                self.add_error(
                    "telefone",
                    "Informe o telefone para compartilhar por WhatsApp.",
                )

        if canal == CompartilhamentoOrcamento.Canal.EMAIL:
            if not dados.get("email"):
                self.add_error(
                    "email",
                    "Informe o destinatário do e-mail.",
                )

            if not (dados.get("assunto") or "").strip():
                self.add_error(
                    "assunto",
                    "Informe o assunto do e-mail.",
                )

        return dados