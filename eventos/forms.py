from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from financeiro.models import BaixaPagar, CategoriaFinanceira, ContaFinanceira, RecebimentoConta
from usuarios.models import Usuario

from .models import EquipeEvento, Evento, PessoaEquipe, TipoProdutoEvento, VendaEvento


def _normalizar_instagram(valor):
    valor = (valor or "").strip()
    return "@" + valor.lstrip("@") if valor else ""


def _normalizar_telefone(valor):
    numeros = "".join(caractere for caractere in (valor or "") if caractere.isdigit())[:11]
    if len(numeros) == 11:
        return f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
    if len(numeros) == 10:
        return f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"
    return (valor or "").strip()


class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        exclude = ["criado_por"]
        widgets = {
            "inicio": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
            "fim": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
            "participantes": forms.CheckboxSelectMultiple(),
            "pessoas_equipe": forms.CheckboxSelectMultiple(),
            "participantes_externos": forms.Textarea(attrs={"rows": 3}),
            "observacoes": forms.Textarea(attrs={"rows": 3}),
            "lembrete_mensagem": forms.Textarea(attrs={"rows": 2}),
            "contato_responsavel": forms.TextInput(attrs={"type": "tel", "placeholder": "(00) 00000-0000"}),
            "instagram": forms.TextInput(attrs={"placeholder": "@usuario"}),
            "contato_organizador": forms.TextInput(attrs={"placeholder": "(00) 00000-0000"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["responsavel"].queryset = Usuario.objects.filter(is_active=True).order_by("first_name", "username")
        self.fields["participantes"].queryset = Usuario.objects.filter(is_active=True).order_by("first_name", "username")
        self.fields["equipe"].queryset = EquipeEvento.objects.filter(ativo=True).order_by("nome")
        self.fields["pessoas_equipe"].queryset = PessoaEquipe.objects.filter(ativo=True).order_by("nome")
        self.fields["lembrete_dias_antes"].required = False
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs.setdefault("class", "form-select" if isinstance(field.widget, forms.Select) else "form-control")

    def clean(self):
        dados = super().clean()
        dados["lembrete_dias_antes"] = dados.get("lembrete_dias_antes") or 1
        if dados.get("inicio") and dados.get("fim") and dados["fim"] < dados["inicio"]:
            self.add_error("fim", "O término não pode ser anterior ao início.")
        for contato, tipo in (
            ("contato_responsavel", "tipo_contato_responsavel"),
            ("contato_organizador", "tipo_contato_organizador"),
        ):
            if dados.get(tipo) in {Evento.CONTATO_WHATSAPP, Evento.CONTATO_TELEFONE}:
                dados[contato] = _normalizar_telefone(dados.get(contato))
        if not self.errors:
            from .services import validar_agenda_evento
            try:
                validar_agenda_evento(dados=dados, evento_id=self.instance.pk or None)
            except ValidationError as erro:
                raise ValidationError(erro.messages)
        return dados

    def clean_instagram(self):
        return _normalizar_instagram(self.cleaned_data.get("instagram"))

    def save(self, commit=True):
        evento = super().save(commit=commit)
        if commit and evento.equipe_id:
            evento.pessoas_equipe.add(*evento.equipe.pessoas.filter(ativo=True))
        return evento


class DespesaRapidaForm(forms.Form):
    evento = forms.ModelChoiceField(label="Evento relacionado", queryset=Evento.objects.none(), required=False)
    descricao = forms.CharField(label="Gasto", max_length=200)
    categoria = forms.ModelChoiceField(queryset=CategoriaFinanceira.objects.none())
    valor = forms.DecimalField(max_digits=14, decimal_places=2, min_value=0.01)
    ja_pago = forms.BooleanField(label="Já foi pago", required=False, initial=True)
    data = forms.DateField(initial=timezone.localdate, widget=forms.DateInput(attrs={"type": "date"}))
    vencimento = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    conta_financeira = forms.ModelChoiceField(queryset=ContaFinanceira.objects.none(), required=False)
    forma_pagamento = forms.ChoiceField(choices=BaixaPagar.FORMA_CHOICES, required=False)
    observacoes = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 2}))

    def __init__(self, *args, operacao="use-helvi", **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["evento"].queryset = Evento.objects.exclude(status=Evento.STATUS_CANCELADO).order_by("-inicio")
        self.fields["categoria"].queryset = CategoriaFinanceira.objects.filter(tipo="despesa", ativo=True).order_by("nome")
        self.fields["conta_financeira"].queryset = ContaFinanceira.objects.filter(
            ativo=True, operacao=operacao,
        ).order_by("-conta_padrao", "nome")
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-check-input" if isinstance(field.widget, forms.CheckboxInput) else ("form-select" if isinstance(field.widget, forms.Select) else "form-control"))

    def clean(self):
        dados = super().clean()
        if dados.get("ja_pago") and not dados.get("conta_financeira"):
            self.add_error("conta_financeira", "Selecione de onde saiu o dinheiro.")
        if not dados.get("ja_pago") and not dados.get("vencimento"):
            self.add_error("vencimento", "Informe quando a despesa deverá ser paga.")
        return dados


class ReceitaRapidaForm(forms.Form):
    evento = forms.ModelChoiceField(label="Evento relacionado", queryset=Evento.objects.none(), required=False)
    descricao = forms.CharField(label="Receita", max_length=200)
    categoria = forms.ModelChoiceField(queryset=CategoriaFinanceira.objects.none())
    valor = forms.DecimalField(max_digits=14, decimal_places=2, min_value=0.01)
    ja_recebido = forms.BooleanField(label="Já foi recebido", required=False, initial=True)
    data = forms.DateField(initial=timezone.localdate, widget=forms.DateInput(attrs={"type": "date"}))
    vencimento = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    conta_financeira = forms.ModelChoiceField(queryset=ContaFinanceira.objects.none(), required=False)
    forma_recebimento = forms.ChoiceField(choices=RecebimentoConta.FORMA_CHOICES, required=False)
    observacoes = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 2}))

    def __init__(self, *args, operacao="use-helvi", **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["evento"].queryset = Evento.objects.exclude(status=Evento.STATUS_CANCELADO).order_by("-inicio")
        self.fields["categoria"].queryset = CategoriaFinanceira.objects.filter(tipo="receita", ativo=True).order_by("nome")
        self.fields["conta_financeira"].queryset = ContaFinanceira.objects.filter(ativo=True, operacao=operacao).order_by("-conta_padrao", "nome")
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-check-input" if isinstance(field.widget, forms.CheckboxInput) else ("form-select" if isinstance(field.widget, forms.Select) else "form-control"))

    def clean(self):
        dados = super().clean()
        if dados.get("ja_recebido") and not dados.get("conta_financeira"):
            self.add_error("conta_financeira", "Selecione onde o dinheiro entrou.")
        if not dados.get("ja_recebido") and not dados.get("vencimento"):
            self.add_error("vencimento", "Informe quando a receita deverá ser recebida.")
        return dados


class CompartilharRelatorioForm(forms.Form):
    email = forms.EmailField(label="E-mail", required=False)
    whatsapp = forms.CharField(label="WhatsApp", max_length=30, required=False)

    def clean(self):
        dados = super().clean()
        if not dados.get("email") and not dados.get("whatsapp"):
            raise forms.ValidationError("Informe um e-mail ou WhatsApp para compartilhar.")
        return dados


class VendaEventoForm(forms.ModelForm):
    forma_recebimento = forms.ChoiceField(
        label="Forma de recebimento",
        choices=RecebimentoConta.FORMA_CHOICES,
        required=False,
    )

    class Meta:
        model = VendaEvento
        fields = [
            "data", "descricao", "tipo_produto", "quantidade", "valor_venda",
            "custo_produtos", "valor_recebido", "forma_recebimento", "observacoes",
        ]
        widgets = {"data": forms.DateInput(attrs={"type": "date"}), "observacoes": forms.Textarea(attrs={"rows": 2})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["data"].initial = timezone.localdate()
        self.fields["valor_venda"].label = "Valor vendido"
        self.fields["custo_produtos"].label = "Custo dos produtos"
        self.fields["valor_recebido"].label = "Valor já recebido"
        self.fields["descricao"].widget.attrs["placeholder"] = "Ex.: vendas do dia ou nome do cliente"
        self.fields["tipo_produto"].queryset = TipoProdutoEvento.objects.filter(ativo=True).order_by("nome")
        self.fields["tipo_produto"].required = True
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    def clean(self):
        dados = super().clean()
        if dados.get("valor_recebido", 0) > dados.get("valor_venda", 0):
            self.add_error("valor_recebido", "O valor recebido não pode superar a venda.")
        return dados


class TipoProdutoEventoForm(forms.ModelForm):
    class Meta:
        model = TipoProdutoEvento
        fields = ["nome"]
        widgets = {"nome": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex.: Casual feminino"})}


class PessoaEquipeForm(forms.ModelForm):
    class Meta:
        model = PessoaEquipe
        fields = ["nome", "tipo_contato", "contato", "cor_agenda"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control"}),
            "tipo_contato": forms.Select(attrs={"class": "form-select"}),
            "contato": forms.TextInput(attrs={"class": "form-control", "placeholder": "(11) 01234-5678"}),
            "cor_agenda": forms.TextInput(attrs={"class": "form-control", "type": "color"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["cor_agenda"].required = False
        self.fields["cor_agenda"].initial = self.instance.cor_agenda or "#743f76"

    def clean_cor_agenda(self):
        return self.cleaned_data.get("cor_agenda") or "#743f76"

    def clean_contato(self):
        valor = self.cleaned_data.get("contato")
        if self.cleaned_data.get("tipo_contato") in {PessoaEquipe.CONTATO_WHATSAPP, PessoaEquipe.CONTATO_TELEFONE}:
            return _normalizar_telefone(valor)
        return (valor or "").strip()

class EquipeEventoForm(forms.ModelForm):
    class Meta:
        model = EquipeEvento
        fields = ["nome", "pessoas"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control"}),
            "pessoas": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["pessoas"].queryset = PessoaEquipe.objects.filter(ativo=True).order_by("nome")


class CategoriaDespesaForm(forms.ModelForm):
    class Meta:
        model = CategoriaFinanceira
        fields = ["nome", "tipo", "descricao"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex.: Marketing"}),
            "tipo": forms.Select(attrs={"class": "form-select"}),
            "descricao": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }

    def save(self, commit=True):
        categoria = super().save(commit=False)
        categoria.ativo = True
        if commit:
            categoria.save()
        return categoria


class CancelarEventoForm(forms.Form):
    motivo = forms.CharField(
        label="Motivo do cancelamento", min_length=5,
        widget=forms.Textarea(attrs={
            "class": "form-control", "rows": 3,
            "placeholder": "Explique por que o evento foi cancelado.",
        }),
    )
