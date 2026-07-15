from django.db.models import Q
from django import forms

from .models import ImagemProduto, Produto



class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = [
            "codigo",
            "codigo_fornecedor",
            "modelo",
            "marca",
            "colecao",
            "genero",
            "tipo_armacao",
            "cores_disponiveis",
            "preco_custo",
            "preco_venda",
            "estoque_atual",
            "estoque_minimo",
            "observacoes",
            "foto",
            "ativo",
        ]

        widgets = {
            "codigo": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex: HV0001",
            }),

            "codigo_fornecedor": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex: ROMA-C2-54",
                "autocomplete": "off",
            }),


            "modelo": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex: Roma, Milano, Classic 01",
            }),
            "marca": forms.Select(attrs={"class": "form-select"}),
            "colecao": forms.Select(attrs={"class": "form-select"}),
            "genero": forms.Select(attrs={"class": "form-select"}),
            "tipo_armacao": forms.Select(attrs={"class": "form-select"}),
            "cores_disponiveis": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex: Preto, Dourado, Transparente",
            }),
            "preco_custo": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "0",
            }),
            "preco_venda": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "0",
            }),
            "estoque_atual": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "0",
            }),
            "estoque_minimo": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "0",
            }),
            "observacoes": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Informações adicionais sobre o produto",
            }),
            "foto": forms.ClearableFileInput(attrs={
                "class": "form-control",
            }),
            "ativo": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }

        labels = {
            "codigo": "Código",
            "modelo": "Modelo",
            "marca": "Marca",
            "colecao": "Coleção",
            "genero": "Gênero",
            "tipo_armacao": "Tipo de Armação",
            "cores_disponiveis": "Cores Disponíveis",
            "preco_custo": "Preço de Custo",
            "preco_venda": "Preço de Venda",
            "estoque_atual": "Estoque Atual",
            "estoque_minimo": "Estoque Mínimo",
            "observacoes": "Observações",
            "foto": "Foto Principal",
            "ativo": "Produto Ativo",
            "codigo_fornecedor": "Código do fornecedor",
        }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            fornecedor_atual_id = getattr(
                self.instance,
                "fornecedor_id",
                None,
            )

            filtro = Q(ativo=True)

            if fornecedor_atual_id:
                filtro |= Q(pk=fornecedor_atual_id)

            self.fields["fornecedor"].queryset = (
                self.fields["fornecedor"]
                .queryset
                .filter(filtro)
                .distinct()
                .order_by(
                    "nome_fantasia",
                    "razao_social",
                )
            )

            self.fields["fornecedor"].empty_label = (
                "Selecione o fornecedor principal"
            )

    def clean_codigo(self):
        codigo = self.cleaned_data.get("codigo")

        if codigo:
            codigo = codigo.strip().upper()

        return codigo

    def clean_codigo_fornecedor(self):
        codigo_fornecedor = self.cleaned_data.get(
            "codigo_fornecedor"
        )

        if codigo_fornecedor:
            codigo_fornecedor = (
                codigo_fornecedor
                .strip()
                .upper()
            )

        return codigo_fornecedor

    def clean_modelo(self):
        modelo = self.cleaned_data.get("modelo")

        if modelo:
            modelo = modelo.strip()

        return modelo

    def clean(self):
        cleaned_data = super().clean()

        preco_custo = cleaned_data.get("preco_custo")
        preco_venda = cleaned_data.get("preco_venda")
        estoque_atual = cleaned_data.get("estoque_atual")
        estoque_minimo = cleaned_data.get("estoque_minimo")

        if preco_custo is not None and preco_custo < 0:
            self.add_error("preco_custo", "O preço de custo não pode ser negativo.")

        if preco_venda is not None and preco_venda < 0:
            self.add_error("preco_venda", "O preço de venda não pode ser negativo.")

        if estoque_atual is not None and estoque_atual < 0:
            self.add_error("estoque_atual", "O estoque atual não pode ser negativo.")

        if estoque_minimo is not None and estoque_minimo < 0:
            self.add_error("estoque_minimo", "O estoque mínimo não pode ser negativo.")

        if preco_custo and preco_venda and preco_venda < preco_custo:
            self.add_error(
                "preco_venda",
                "O preço de venda não deve ser menor que o preço de custo."
            )

        return cleaned_data


class ImagemProdutoForm(forms.ModelForm):
    class Meta:
        model = ImagemProduto
        fields = [
            "imagem",
            "descricao",
            "principal",
        ]

        widgets = {
            "imagem": forms.ClearableFileInput(attrs={
                "class": "form-control",
            }),
            "descricao": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex: Frente, lateral, detalhe da haste",
            }),
            "principal": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }

        labels = {
            "imagem": "Imagem",
            "descricao": "Descrição",
            "principal": "Imagem principal",
        }