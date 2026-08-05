from django import template

from usuarios.permissoes import usuario_pode_executar, usuario_tem_permissao


register = template.Library()


@register.simple_tag
def pode_acessar(usuario, modulo):
    return usuario_tem_permissao(usuario, modulo)


@register.simple_tag
def pode_executar(usuario, acao):
    return usuario_pode_executar(usuario, acao)
