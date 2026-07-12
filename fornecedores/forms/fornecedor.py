from django import forms

from fornecedores.models import Fornecedor
from fornecedores.utils.documentos import (
    formatar_cpf_cnpj,
    formatar_telefone,
    somente_numeros,
    validar_cpf_cnpj,
)



class FornecedorForm(forms.ModelForm):
    class Meta:
        model = Fornecedor

        fields = [
            "tipo_pessoa",
            "razao_social",
            "nome_fantasia",
            "cpf_cnpj",
            "inscricao_estadual",
            "inscricao_municipal",
            "contato_principal",
            "telefone",
            "whatsapp",
            "email",
            "site",
            "cep",
            "logradouro",
            "numero",
            "complemento",
            "bairro",
            "cidade",
            "estado",
            "prazo_medio_entrega",
            "condicao_pagamento_padrao",
            "observacoes",
            "ativo",
        ]

        widgets = {
            "tipo_pessoa": forms.Select(
                attrs={"class": "form-select"}
            ),
            "razao_social": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Razão social ou nome completo",
                    "autocomplete": "off",
                }
            ),
            "nome_fantasia": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nome fantasia",
                    "autocomplete": "off",
                }
            ),
            "cpf_cnpj": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "CPF ou CNPJ",
                    "inputmode": "numeric",
                    "maxlength": "18",
                    "autocomplete": "off",
                    "data-mask": "cpf-cnpj",
                }
            ),
            "inscricao_estadual": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Inscrição estadual",
                    "autocomplete": "off",
                }
            ),
            "inscricao_municipal": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Inscrição municipal",
                    "autocomplete": "off",
                }
            ),
            "contato_principal": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nome do contato principal",
                    "autocomplete": "off",
                }
            ),
            "telefone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "(11) 3333-3333",
                    "inputmode": "tel",
                    "maxlength": "15",
                    "autocomplete": "tel",
                    "data-mask": "telefone",
                }
            ),
            "whatsapp": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "(11) 99999-9999",
                    "inputmode": "tel",
                    "maxlength": "15",
                    "autocomplete": "tel",
                    "data-mask": "telefone",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "fornecedor@empresa.com.br",
                    "autocomplete": "off",
                }
            ),
            "site": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://",
                    "autocomplete": "off",
                }
            ),
            "cep": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "00000-000",
                    "inputmode": "numeric",
                    "maxlength": "9",
                    "autocomplete": "postal-code",
                    "data-mask": "cep",
                    "data-cep-autocomplete": "true",
                    "data-logradouro-target": "id_logradouro",
                    "data-bairro-target": "id_bairro",
                    "data-cidade-target": "id_cidade",
                    "data-estado-target": "id_estado",
                    "data-complemento-target": "id_complemento",
                }
            ),
            "logradouro": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Rua, avenida ou estrada",
                    "autocomplete": "off",
                }
            ),
            "numero": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Número",
                    "autocomplete": "off",
                }
            ),
            "complemento": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Complemento",
                    "autocomplete": "off",
                }
            ),
            "bairro": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Bairro",
                    "autocomplete": "off",
                }
            ),
            "cidade": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Cidade",
                    "autocomplete": "off",
                }
            ),
            "estado": forms.Select(
                attrs={"class": "form-select"}
            ),
            "prazo_medio_entrega": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Prazo em dias",
                    "min": "0",
                }
            ),
            "condicao_pagamento_padrao": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex.: 30/60/90 dias",
                    "autocomplete": "off",
                }
            ),
            "observacoes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Informações adicionais sobre o fornecedor",
                }
            ),
            "ativo": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }

    def clean_cpf_cnpj(self):
        documento = self.cleaned_data.get("cpf_cnpj", "")
        tipo_pessoa = self.cleaned_data.get("tipo_pessoa")

        documento_numerico = somente_numeros(documento)

        if not documento_numerico:
            raise forms.ValidationError(
                "Informe o CPF ou CNPJ do fornecedor."
            )

        if tipo_pessoa == Fornecedor.TIPO_PESSOA_FISICA:
            descricao_documento = "CPF"
        else:
            descricao_documento = "CNPJ"

        if not validar_cpf_cnpj(
            documento_numerico,
            tipo_pessoa,
        ):
            raise forms.ValidationError(
                f"Informe um {descricao_documento} válido."
            )

        fornecedores_existentes = Fornecedor.objects.filter(
            cpf_cnpj=formatar_cpf_cnpj(documento_numerico)
        )

        if self.instance.pk:
            fornecedores_existentes = fornecedores_existentes.exclude(
                pk=self.instance.pk
            )

        if fornecedores_existentes.exists():
            raise forms.ValidationError(
                "Já existe um fornecedor cadastrado com este documento."
            )

        return formatar_cpf_cnpj(documento_numerico)

    def clean_telefone(self):
        telefone = somente_numeros(
            self.cleaned_data.get("telefone", "")
        )

        if not telefone:
            return ""

        if len(telefone) not in (10, 11):
            raise forms.ValidationError(
                "Informe um telefone com DDD e 10 ou 11 números."
            )

        return formatar_telefone(telefone)

    def clean_whatsapp(self):
        whatsapp = somente_numeros(
            self.cleaned_data.get("whatsapp", "")
        )

        if not whatsapp:
            return ""

        if len(whatsapp) not in (10, 11):
            raise forms.ValidationError(
                "Informe um WhatsApp com DDD e 10 ou 11 números."
            )

        return formatar_telefone(whatsapp)

    def clean_cep(self):
        cep = somente_numeros(
            self.cleaned_data.get("cep", "")
        )

        if cep and len(cep) != 8:
            raise forms.ValidationError(
                "Informe um CEP válido com 8 números."
            )

        if cep:
            return f"{cep[:5]}-{cep[5:]}"

        return ""

    def clean_email(self):
        email = self.cleaned_data.get("email", "")

        return email.strip().lower()

    def clean_site(self):
        site = self.cleaned_data.get("site", "")

        return site.strip()

    def clean_razao_social(self):
        razao_social = self.cleaned_data.get(
            "razao_social",
            ""
        ).strip()

        if len(razao_social) < 3:
            raise forms.ValidationError(
                "Informe uma razão social ou nome com pelo menos 3 caracteres."
            )

        return razao_social

    def clean_nome_fantasia(self):
        return self.cleaned_data.get(
            "nome_fantasia",
            ""
        ).strip()