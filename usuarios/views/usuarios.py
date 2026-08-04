from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from usuarios.decorators import permissao_requerida
from usuarios.forms import UsuarioForm, UsuarioUpdateForm
from usuarios.permissoes import Modulo


@permissao_requerida(Modulo.USUARIOS)
def lista_usuarios(request):
    busca = request.GET.get("busca", "").strip()

    Usuario = get_user_model()

    usuarios = Usuario.objects.all().order_by(
        "first_name",
        "last_name",
        "username",
    )

    if busca:
        usuarios = (
            usuarios.filter(username__icontains=busca)
            | usuarios.filter(first_name__icontains=busca)
            | usuarios.filter(last_name__icontains=busca)
            | usuarios.filter(email__icontains=busca)
        )

    return render(
        request,
        "usuarios/lista_usuarios.html",
        {
            "usuarios": usuarios,
            "busca": busca,
        },
    )


@permissao_requerida(Modulo.USUARIOS)
def novo_usuario(request):
    if request.method == "POST":
        form = UsuarioForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Usuário cadastrado com sucesso.")
            return redirect("usuarios:lista_usuarios")
    else:
        form = UsuarioForm()

    return render(
        request,
        "usuarios/form_usuario.html",
        {
            "form": form,
            "titulo": "Novo Usuário",
            "modo_edicao": False,
            "usuario": None,
        },
    )


@permissao_requerida(Modulo.USUARIOS)
def editar_usuario(request, pk):
    Usuario = get_user_model()
    usuario = get_object_or_404(Usuario, pk=pk)

    if request.method == "POST":
        form = UsuarioUpdateForm(
            request.POST,
            request.FILES,
            instance=usuario,
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Usuário atualizado com sucesso.")
            return redirect("usuarios:lista_usuarios")
    else:
        form = UsuarioUpdateForm(instance=usuario)

    return render(
        request,
        "usuarios/form_usuario.html",
        {
            "form": form,
            "titulo": "Editar Usuário",
            "modo_edicao": True,
            "usuario": usuario,
        },
    )


@permissao_requerida(Modulo.USUARIOS)
@require_POST
@transaction.atomic
def inativar_usuario(request, pk):
    Usuario = get_user_model()
    usuario = get_object_or_404(
        Usuario.objects.select_for_update(),
        pk=pk,
    )

    if usuario.pk == request.user.pk:
        messages.error(
            request,
            "Você não pode inativar o próprio usuário.",
        )
        return redirect("usuarios:lista_usuarios")

    if (
        usuario.perfil == Usuario.Perfil.ADMINISTRADOR
        and usuario.is_active
        and not Usuario.objects.filter(
            perfil=Usuario.Perfil.ADMINISTRADOR,
            is_active=True,
        ).exclude(pk=usuario.pk).exists()
    ):
        messages.error(
            request,
            "Mantenha pelo menos um administrador ativo no ERP.",
        )
        return redirect("usuarios:lista_usuarios")

    usuario.is_active = False
    usuario.save(update_fields=["is_active"])

    messages.success(request, "Usuário inativado com sucesso.")
    return redirect("usuarios:lista_usuarios")


@permissao_requerida(Modulo.USUARIOS)
@require_POST
def reativar_usuario(request, pk):
    Usuario = get_user_model()
    usuario = get_object_or_404(Usuario, pk=pk)

    usuario.is_active = True
    usuario.save(update_fields=["is_active"])

    messages.success(request, "Usuário reativado com sucesso.")
    return redirect("usuarios:lista_usuarios")
