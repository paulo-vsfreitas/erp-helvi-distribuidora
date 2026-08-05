from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from vendas.models import Venda
from vendas.services.cadastro_service import alterar_vendedor_da_venda


@login_required
@require_POST
def alterar_vendedor_view(request, numero):
    venda = get_object_or_404(Venda, numero=numero)
    try:
        alterar_vendedor_da_venda(
            venda=venda,
            vendedor_id=request.POST.get("vendedor"),
            usuario=request.user,
            senha=request.POST.get("senha_autorizacao"),
        )
    except ValidationError as erro:
        for mensagem in erro.messages:
            messages.error(request, mensagem)
    else:
        messages.success(request, f"Vendedor da venda nº {numero} atualizado.")

    destino = request.POST.get("next")
    if destino == "lista":
        return redirect("vendas:lista")
    return redirect("vendas:ficha", numero)
