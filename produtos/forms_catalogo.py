from django import forms
from PIL import Image, UnidentifiedImageError

from catalogo.models import TipoArmacao
from fornecedores.models import Fornecedor


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    widget = MultipleFileInput

    def clean(self, data, initial=None):
        single_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_clean(item, initial) for item in data]
        return [single_clean(data, initial)]


class ImportacaoCatalogoForm(forms.Form):
    fornecedor = forms.ModelChoiceField(
        queryset=Fornecedor.objects.none(),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    tipo_armacao = forms.ModelChoiceField(
        queryset=TipoArmacao.objects.none(),
        label="Tipo de armação",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    preco_custo = forms.DecimalField(
        min_value=0,
        decimal_places=2,
        max_digits=10,
        label="Preço de custo",
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
    )
    preco_venda = forms.DecimalField(
        min_value=0,
        decimal_places=2,
        max_digits=10,
        label="Preço de venda",
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
    )
    estoque_inicial = forms.IntegerField(
        min_value=0,
        initial=1,
        label="Estoque inicial padrão",
        widget=forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
    )
    estoque_minimo = forms.IntegerField(
        min_value=0,
        initial=0,
        label="Estoque mínimo",
        widget=forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
    )
    arquivos = MultipleFileField(
        label="Catálogos e imagens",
        help_text="Envie PDF, JPG, JPEG ou PNG. Você pode selecionar vários arquivos de uma vez.",
        widget=MultipleFileInput(
            attrs={
                "class": "form-control",
                "accept": ".pdf,.jpg,.jpeg,.png,application/pdf,image/jpeg,image/png",
                "multiple": True,
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["fornecedor"].queryset = Fornecedor.objects.filter(ativo=True).order_by("razao_social")
        self.fields["tipo_armacao"].queryset = TipoArmacao.objects.filter(ativo=True).order_by("nome")

    def clean(self):
        cleaned = super().clean()
        custo = cleaned.get("preco_custo")
        venda = cleaned.get("preco_venda")
        if custo is not None and venda is not None and venda < custo:
            self.add_error("preco_venda", "O preço de venda não deve ser menor que o preço de custo.")
        return cleaned

    def clean_arquivos(self):
        arquivos = self.cleaned_data["arquivos"]
        permitidas = (".pdf", ".jpg", ".jpeg", ".png")
        erros = []
        for arquivo in arquivos:
            nome = arquivo.name.lower()
            if not nome.endswith(permitidas):
                erros.append(f"{arquivo.name}: formato não aceito.")
                continue
            if arquivo.size > 25 * 1024 * 1024:
                erros.append(f"{arquivo.name}: o arquivo excede 25 MB.")
                continue

            try:
                if nome.endswith(".pdf"):
                    assinatura = arquivo.read(5)
                    if assinatura != b"%PDF-":
                        erros.append(f"{arquivo.name}: o conteúdo não parece ser um PDF válido.")
                else:
                    Image.open(arquivo).verify()
            except (UnidentifiedImageError, OSError, ValueError):
                erros.append(f"{arquivo.name}: imagem inválida ou corrompida.")
            finally:
                arquivo.seek(0)
        if erros:
            raise forms.ValidationError(erros)
        return arquivos
