from django import forms
from django.core.exceptions import ValidationError

from configuracoes.models import Empresa
from configuracoes.services.mensagens_service import validar_modelo_mensagem
from fornecedores.utils.documentos import (
    formatar_cpf_cnpj,
    formatar_telefone,
    somente_numeros,
    validar_cpf_cnpj,
)


class EmpresaForm(forms.ModelForm):
    TAMANHO_MAXIMO_LOGO = 2 * 1024 * 1024

    class Meta:
        model = Empresa

        fields = [
            "nome_fantasia",
            "razao_social",
            "cnpj",
            "inscricao_estadual",
            "inscricao_municipal",
            "telefone",
            "whatsapp",
            "email",
            "site",
            "instagram",
            "facebook",
            "exibir_whatsapp_pdf",
            "exibir_instagram_pdf",
            "exibir_facebook_pdf",
            "exibir_site_pdf",
            "cep",
            "logradouro",
            "numero",
            "complemento",
            "bairro",
            "cidade",
            "estado",
            "logo",
            "rodape_documentos",
            "assunto_padrao_email",
            "mensagem_padrao_email",
            "mensagem_padrao_whatsapp",
        ]

        widgets = {
            "nome_fantasia": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex.: Helvi Distribuidora",
                    "autocomplete": "organization",
                }
            ),
            "razao_social": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Razão social da empresa",
                    "autocomplete": "organization",
                }
            ),
            "cnpj": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "00.000.000/0000-00",
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
                    "placeholder": "contato@empresa.com.br",
                    "autocomplete": "email",
                }
            ),
            "site": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://",
                    "autocomplete": "url",
                }
            ),
            "instagram": forms.TextInput(attrs={"class": "form-control", "placeholder": "@helvidistribuidora"}),
            "facebook": forms.TextInput(attrs={"class": "form-control", "placeholder": "facebook.com/helvidistribuidora"}),
            "exibir_whatsapp_pdf": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "exibir_instagram_pdf": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "exibir_facebook_pdf": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "exibir_site_pdf": forms.CheckboxInput(attrs={"class": "form-check-input"}),
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
                    "autocomplete": "address-line1",
                }
            ),
            "numero": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Número",
                    "autocomplete": "address-line2",
                }
            ),
            "complemento": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Sala, conjunto, bloco...",
                    "autocomplete": "off",
                }
            ),
            "bairro": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Bairro",
                    "autocomplete": "address-level3",
                }
            ),
            "cidade": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Cidade",
                    "autocomplete": "address-level2",
                }
            ),
            "estado": forms.Select(
                attrs={
                    "class": "form-select",
                    "autocomplete": "address-level1",
                }
            ),
            "logo": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": ".png,.jpg,.jpeg,image/png,image/jpeg",
                    "data-image-preview": "true",
                    "data-preview-target": "#preview-logo",
                    "data-placeholder-target": "#preview-logo-placeholder",
                }
            ),
            "rodape_documentos": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": (
                        "Ex.: Agradecemos pela preferência. "
                        "Helvi Distribuidora."
                    ),
                }
            ),
            "assunto_padrao_email": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "data-mensagem-editor": "",
                    "placeholder": "Ex.: {EMPRESA} • Orçamento {ORCAMENTO}",
                }
            ),
            "mensagem_padrao_email": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "data-mensagem-editor": "",
                    "rows": 8,
                    "placeholder": "Olá, {CLIENTE}! Segue o orçamento {ORCAMENTO}.",
                }
            ),
            "mensagem_padrao_whatsapp": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "data-mensagem-editor": "",
                    "rows": 8,
                    "placeholder": "Olá, {CLIENTE}! Seu orçamento é {ORCAMENTO}.",
                }
            ),
        }

    def _clean_modelo(self, nome_campo):
        modelo = (self.cleaned_data.get(nome_campo) or "").strip()
        validar_modelo_mensagem(modelo)
        return modelo

    def clean_assunto_padrao_email(self):
        return self._clean_modelo("assunto_padrao_email")

    def clean_mensagem_padrao_email(self):
        return self._clean_modelo("mensagem_padrao_email")

    def clean_mensagem_padrao_whatsapp(self):
        return self._clean_modelo("mensagem_padrao_whatsapp")

    def clean_nome_fantasia(self):
        nome_fantasia = (
            self.cleaned_data.get("nome_fantasia") or ""
        ).strip()

        if len(nome_fantasia) < 3:
            raise forms.ValidationError(
                "Informe um nome fantasia com pelo menos 3 caracteres."
            )

        return nome_fantasia

    def clean_razao_social(self):
        razao_social = (
            self.cleaned_data.get("razao_social") or ""
        ).strip()

        if len(razao_social) < 3:
            raise forms.ValidationError(
                "Informe uma razão social com pelo menos 3 caracteres."
            )

        return razao_social

    def clean_cnpj(self):
        cnpj = somente_numeros(
            self.cleaned_data.get("cnpj", "")
        )

        if not cnpj:
            return ""

        if not validar_cpf_cnpj(
            cnpj,
            tipo_pessoa="PJ",
        ):
            raise forms.ValidationError(
                "Informe um CNPJ válido."
            )

        return formatar_cpf_cnpj(cnpj)

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

    def clean_email(self):
        email = (
            self.cleaned_data.get("email") or ""
        ).strip().lower()

        return email

    def clean_site(self):
        site = (
            self.cleaned_data.get("site") or ""
        ).strip()

        return site

    def clean_cep(self):
        cep = somente_numeros(
            self.cleaned_data.get("cep", "")
        )

        if not cep:
            return ""

        if len(cep) != 8:
            raise forms.ValidationError(
                "Informe um CEP válido com 8 números."
            )

        return f"{cep[:5]}-{cep[5:]}"

    def clean_logo(self):
        logo = self.cleaned_data.get("logo")

        if not logo:
            return logo

        if logo.size > self.TAMANHO_MAXIMO_LOGO:
            raise ValidationError(
                "A logo deve possuir no máximo 2 MB."
            )

        tipos_permitidos = {
            "image/png",
            "image/jpeg",
        }

        content_type = getattr(
            logo,
            "content_type",
            None,
        )

        if content_type and content_type not in tipos_permitidos:
            raise ValidationError(
                "Envie uma imagem no formato PNG, JPG ou JPEG."
            )

        return logo
