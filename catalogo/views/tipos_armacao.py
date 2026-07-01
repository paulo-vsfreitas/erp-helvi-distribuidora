from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from catalogo.forms.tipo_armacao import TipoArmacaoForm
from catalogo.models import TipoArmacao


@login_required
def lista_tipo_armacao(request):
    busca = request.GET.get("busca", "").strip()

    tipos_armacao = TipoArmacao.objects.all().order_by("nome")

    if busca:
        tipos_armacao = tipos_armacao.filter(
            Q(nome__icontains=busca)
            | Q(descricao__icontains=busca)
        )

    return render(request, "catalogo/lista_tipo_armacao.html", {
        "tipos_armacao": tipos_armacao,
        "busca": busca,
    })


@login_required
def novo_tipo_armacao(request):
    if request.method == "POST":
        form = TipoArmacaoForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Tipo de armação cadastrado com sucesso.")
            return redirect("catalogo:lista_tipo_armacao")
    else:
        form = TipoArmacaoForm()

    return render(request, "catalogo/form_tipo_armacao.html", {
        "form": form,
        "titulo": "Novo Tipo de Armação",
    })


@login_required
def editar_tipo_armacao(request, pk):
    tipo_armacao = get_object_or_404(TipoArmacao, pk=pk)

    if request.method == "POST":
        form = TipoArmacaoForm(request.POST, instance=tipo_armacao)

        if form.is_valid():
            form.save()
            messages.success(request, "Tipo de armação atualizado com sucesso.")
            return redirect("catalogo:lista_tipo_armacao")
    else:
        form = TipoArmacaoForm(instance=tipo_armacao)

    return render(request, "catalogo/form_tipo_armacao.html", {
        "form": form,
        "titulo": "Editar Tipo de Armação",
        "tipo_armacao": tipo_armacao,
    })


@login_required
def inativar_tipo_armacao(request, pk):
    tipo_armacao = get_object_or_404(TipoArmacao, pk=pk)

    tipo_armacao.ativo = False
    tipo_armacao.save()

    messages.success(request, "Tipo de armação inativado com sucesso.")
    return redirect("catalogo:lista_tipo_armacao")


@login_required
def reativar_tipo_armacao(request, pk):
    tipo_armacao = get_object_or_404(TipoArmacao, pk=pk)

    tipo_armacao.ativo = True
    tipo_armacao.save()

    messages.success(request, "Tipo de armação reativado com sucesso.")
    return redirect("catalogo:lista_tipo_armacao")