import re
from decimal import Decimal

from django import forms
from django.core.exceptions import ValidationError

from .models import Cliente


UF_CHOICES = [
    ("", "Selecione o estado"),
    ("AC", "Acre"),
    ("AL", "Alagoas"),
    ("AP", "Amapá"),
    ("AM", "Amazonas"),
    ("BA", "Bahia"),
    ("CE", "Ceará"),
    ("DF", "Distrito Federal"),
    ("ES", "Espírito Santo"),
    ("GO", "Goiás"),
    ("MA", "Maranhão"),
    ("MT", "Mato Grosso"),
    ("MS", "Mato Grosso do Sul"),
    ("MG", "Minas Gerais"),
    ("PA", "Pará"),
    ("PB", "Paraíba"),
    ("PR", "Paraná"),
    ("PE", "Pernambuco"),
    ("PI", "Piauí"),
    ("RJ", "Rio de Janeiro"),
    ("RN", "Rio Grande do Norte"),
    ("RS", "Rio Grande do Sul"),
    ("RO", "Rondônia"),
    ("RR", "Roraima"),
    ("SC", "Santa Catarina"),
    ("SP", "São Paulo"),
    ("SE", "Sergipe"),
    ("TO", "Tocantins"),
]


def somente_numeros(valor):
    """
    Remove pontos, traços, parênteses, espaços e outros caracteres,
    mantendo apenas os números.
    """
    return re.sub(r"\D", "", valor or "")


def cnpj_valido(cnpj):
    """
    Valida os dois dígitos verificadores do CNPJ.
    """
    cnpj = somente_numeros(cnpj)

    if len(cnpj) != 14:
        return False

    if cnpj == cnpj[0] * 14:
        return False

    pesos_primeiro_digito = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(
        int(numero) * peso
        for numero, peso in zip(cnpj[:12], pesos_primeiro_digito)
    )

    resto = soma % 11
    primeiro_digito = 0 if resto < 2 else 11 - resto

    pesos_segundo_digito = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(
        int(numero) * peso
        for numero, peso in zip(cnpj[:13], pesos_segundo_digito)
    )

    resto = soma % 11
    segundo_digito = 0 if resto < 2 else 11 - resto

    return cnpj[-2:] == f"{primeiro_digito}{segundo_digito}"


def formatar_cnpj(cnpj):
    """
    Retorna o CNPJ no formato 00.000.000/0000-00.
    """
    numeros = somente_numeros(cnpj)

    return (
        f"{numeros[:2]}."
        f"{numeros[2:5]}."
        f"{numeros[5:8]}/"
        f"{numeros[8:12]}-"
        f"{numeros[12:14]}"
    )

def cpf_valido(cpf):
    cpf = somente_numeros(cpf)

    if len(cpf) != 11:
        return False

    if cpf == cpf[0] * 11:
        return False

    soma = sum(
        int(cpf[indice]) * (10 - indice)
        for indice in range(9)
    )

    resto = soma % 11
    primeiro_digito = 0 if resto < 2 else 11 - resto

    soma = sum(
        int(cpf[indice]) * (11 - indice)
        for indice in range(10)
    )

    resto = soma % 11
    segundo_digito = 0 if resto < 2 else 11 - resto

    return cpf[-2:] == f"{primeiro_digito}{segundo_digito}"

def formatar_cpf(cpf):
    numeros = somente_numeros(cpf)

    return (
        f"{numeros[:3]}."
        f"{numeros[3:6]}."
        f"{numeros[6:9]}-"
        f"{numeros[9:11]}"
    )


def formatar_telefone(telefone):
    """
    Formata telefone fixo ou celular.
    """
    numeros = somente_numeros(telefone)

    if len(numeros) == 11:
        return (
            f"({numeros[:2]}) "
            f"{numeros[2:7]}-"
            f"{numeros[7:]}"
        )

    if len(numeros) == 10:
        return (
            f"({numeros[:2]}) "
            f"{numeros[2:6]}-"
            f"{numeros[6:]}"
        )

    return telefone


class ClienteForm(forms.ModelForm):
    estado = forms.ChoiceField(
        choices=UF_CHOICES,
        required=False,
        label="Estado",
        widget=forms.Select(
            attrs={
                "class": "form-control",
            }
        ),
    )

    class Meta:
        model = Cliente
        fields = [
            "razao_social",
            "nome_fantasia",
            "cnpj",
            "responsavel",
            "telefone",
            "whatsapp",
            "email",
            "cidade",
            "estado",
            "endereco",
            "limite_credito",
            "condicao_pagamento",
            "observacoes",
            "ativo",
        ]

        labels = {
            "cnpj": "CPF / CNPJ",
        }

        widgets = {
            "razao_social": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "autocomplete": "organization",
                }
            ),
            "nome_fantasia": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "autocomplete": "organization",
                }
            ),
            "cnpj": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "CPF ou CNPJ",
                    "inputmode": "numeric",
                    "maxlength": "18",
                    "autocomplete": "off",
                    "data-mask": "cpf-cnpj",
                }
            ),
            "responsavel": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "autocomplete": "name",
                }
            ),
            "telefone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "(00) 0000-0000",
                    "inputmode": "tel",
                    "maxlength": "15",
                    "autocomplete": "tel",
                    "data-mask": "telefone",
                }
            ),
            "whatsapp": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "(00) 00000-0000",
                    "inputmode": "tel",
                    "maxlength": "15",
                    "autocomplete": "tel",
                    "data-mask": "telefone",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "contato@empresa.com.br",
                    "autocomplete": "email",
                }
            ),
            "cidade": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "autocomplete": "address-level2",
                }
            ),
            "endereco": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "autocomplete": "street-address",
                }
            ),
            "limite_credito": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "step": "0.01",
                }
            ),
            "condicao_pagamento": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "observacoes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                }
            ),
        }

    def clean_razao_social(self):
        razao_social = self.cleaned_data.get("razao_social", "").strip()

        if not razao_social:
            raise ValidationError("Informe a razão social.")

        if len(razao_social) < 2:
            raise ValidationError(
                "A razão social deve possuir pelo menos 2 caracteres."
            )

        return razao_social

    def clean_nome_fantasia(self):
        nome_fantasia = self.cleaned_data.get("nome_fantasia", "").strip()

        if not nome_fantasia:
            raise ValidationError("Informe o nome fantasia.")

        if len(nome_fantasia) < 2:
            raise ValidationError(
                "O nome fantasia deve possuir pelo menos 2 caracteres."
            )

        return nome_fantasia

    def clean_cnpj(self):
        documento = self.cleaned_data.get("cnpj")

        # CPF/CNPJ permanece opcional
        if not documento:
            return None

        numeros = somente_numeros(documento)

        if len(numeros) == 11:
            if not cpf_valido(numeros):
                raise ValidationError(
                    "Informe um CPF válido."
                )

            documento_formatado = formatar_cpf(numeros)

        elif len(numeros) == 14:
            if not cnpj_valido(numeros):
                raise ValidationError(
                    "Informe um CNPJ válido."
                )

            documento_formatado = formatar_cnpj(numeros)

        else:
            raise ValidationError(
                "Informe um CPF com 11 números ou um CNPJ com 14 números."
            )

        documentos_equivalentes = [
            numeros,
            documento_formatado,
        ]

        cliente_existente = Cliente.objects.filter(
            cnpj__in=documentos_equivalentes
        ).exclude(pk=self.instance.pk)

        if cliente_existente.exists():
            raise ValidationError(
                "Já existe um cliente cadastrado com este CPF ou CNPJ."
            )

        return documento_formatado

    def clean_responsavel(self):
        responsavel = self.cleaned_data.get("responsavel")

        if not responsavel:
            return None

        responsavel = responsavel.strip()

        if len(responsavel) < 2:
            raise ValidationError(
                "O nome do responsável deve possuir pelo menos 2 caracteres."
            )

        return responsavel

    def clean_telefone(self):
        telefone = self.cleaned_data.get("telefone")

        if not telefone:
            return None

        numeros = somente_numeros(telefone)

        if len(numeros) not in (10, 11):
            raise ValidationError(
                "Informe um telefone com DDD e 10 ou 11 números."
            )

        return formatar_telefone(numeros)

    def clean_whatsapp(self):
        whatsapp = self.cleaned_data.get("whatsapp")

        if not whatsapp:
            return None

        numeros = somente_numeros(whatsapp)

        if len(numeros) not in (10, 11):
            raise ValidationError(
                "Informe um WhatsApp com DDD e 10 ou 11 números."
            )

        return formatar_telefone(numeros)

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if not email:
            return None

        return email.strip().lower()

    def clean_cidade(self):
        cidade = self.cleaned_data.get("cidade")

        if not cidade:
            return None

        cidade = cidade.strip()

        if len(cidade) < 2:
            raise ValidationError(
                "Informe uma cidade válida."
            )

        return cidade

    def clean_endereco(self):
        endereco = self.cleaned_data.get("endereco")

        if not endereco:
            return None

        endereco = endereco.strip()

        if len(endereco) < 3:
            raise ValidationError(
                "Informe um endereço válido."
            )

        return endereco

    def clean_condicao_pagamento(self):
        condicao_pagamento = self.cleaned_data.get("condicao_pagamento")

        if not condicao_pagamento:
            return None

        return condicao_pagamento.strip()

    def clean_limite_credito(self):
        limite_credito = self.cleaned_data.get("limite_credito")

        if limite_credito is None:
            return Decimal("0.00")

        if limite_credito < 0:
            raise ValidationError(
                "O limite de crédito não pode ser negativo."
            )

        return limite_credito