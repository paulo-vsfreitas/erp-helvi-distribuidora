from django import forms

from .models import Marca


class MarcaForm(forms.ModelForm):

    class Meta:
        model = Marca

        fields = [
            'nome',
            'descricao',
            'ativo',
        ]

        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control'
            }),

            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }