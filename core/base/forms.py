from django import forms


class BaseModelForm(forms.ModelForm):
    """
    Formulário base para todos os cadastros simples do ERP Helvi.
    """

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for campo in self.fields.values():

            campo.widget.attrs.setdefault(
                "class",
                "form-control",
            )

            campo.widget.attrs.setdefault(
                "autocomplete",
                "off",
            )