from django import template

from core.formatters import formatar_moeda_br


register = template.Library()


@register.filter(name="moeda")
def moeda(valor):
    return formatar_moeda_br(valor)
