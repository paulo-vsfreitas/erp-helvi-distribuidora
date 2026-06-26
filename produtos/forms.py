from django import forms
from .models import Produto


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = [
            'codigo',
            'modelo',
            'marca',
            'colecao',
            'genero',
            'tipo_armacao',
            'cores_disponiveis',
            'preco_custo',
            'preco_venda',
            'estoque_atual',
            'estoque_minimo',
            'observacoes',
            'foto',
            'ativo',
        ]

        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'marca': forms.Select(attrs={'class': 'form-control'}),
            'colecao': forms.Select(attrs={'class': 'form-control'}),
            'genero': forms.Select(attrs={'class': 'form-control'}),
            'tipo_armacao': forms.Select(attrs={'class': 'form-control'}),
            'cores_disponiveis': forms.TextInput(attrs={'class': 'form-control'}),
            'preco_custo': forms.NumberInput(attrs={'class': 'form-control'}),
            'preco_venda': forms.NumberInput(attrs={'class': 'form-control'}),
            'estoque_atual': forms.NumberInput(attrs={'class': 'form-control'}),
            'estoque_minimo': forms.NumberInput(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }