from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import redirect, render


@login_required
def primeiro_acesso(request):
    if not request.user.primeiro_acesso:
        return redirect("selecionar_operacao")

    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)

        if form.is_valid():
            usuario = form.save()
            usuario.primeiro_acesso = False
            usuario.save(update_fields=["primeiro_acesso"])
            update_session_auth_hash(request, usuario)
            messages.success(
                request,
                "Senha definida com sucesso. Seu acesso está liberado.",
            )
            return redirect("selecionar_operacao")
    else:
        form = PasswordChangeForm(request.user)

    for campo in form.fields.values():
        campo.widget.attrs["class"] = "form-control"

    return render(
        request,
        "usuarios/primeiro_acesso.html",
        {"form": form},
    )
