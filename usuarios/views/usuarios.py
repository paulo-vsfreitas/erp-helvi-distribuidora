from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect, render

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
        },
    )


@permissao_requerida(Modulo.USUARIOS)
def inativar_usuario(request, pk):
    Usuario = get_user_model()
    usuario = get_object_or_404(Usuario, pk=pk)

    usuario.is_active = False
    usuario.save()

    messages.success(request, "Usuário inativado com sucesso.")
    return redirect("usuarios:lista_usuarios")


@permissao_requerida(Modulo.USUARIOS)
def reativar_usuario(request, pk):
    Usuario = get_user_model()
    usuario = get_object_or_404(Usuario, pk=pk)

    usuario.is_active = True
    usuario.save()

    messages.success(request, "Usuário reativado com sucesso.")
    return redirect("usuarios:lista_usuarios")