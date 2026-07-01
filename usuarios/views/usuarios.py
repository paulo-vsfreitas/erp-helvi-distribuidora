from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from usuarios.decorators import perfil_requerido
from usuarios.forms import UsuarioForm, UsuarioUpdateForm


@login_required
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


@login_required
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


@login_required
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


@login_required
def inativar_usuario(request, pk):
    Usuario = get_user_model()
    usuario = get_object_or_404(Usuario, pk=pk)

    usuario.is_active = False
    usuario.save()

    messages.success(request, "Usuário inativado com sucesso.")
    return redirect("usuarios:lista_usuarios")

@login_required
def reativar_usuario(request, pk):
    Usuario = get_user_model()
    usuario = get_object_or_404(Usuario, pk=pk)

    usuario.is_active = True
    usuario.save()

    messages.success(request, "Usuário reativado com sucesso.")
    return redirect("usuarios:lista_usuarios")