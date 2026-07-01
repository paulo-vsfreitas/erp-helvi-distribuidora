from django import template

from usuarios.permissoes import usuario_tem_permissao


register = template.Library()


@register.simple_tag
def pode_acessar(usuario, modulo):
    return usuario_tem_permissao(usuario, modulo)