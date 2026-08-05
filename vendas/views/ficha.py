from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from vendas.models import Venda
from django.contrib.auth import get_user_model
from vendas.services.cadastro_service import pode_editar_vendedor


@login_required
def ficha_venda(request, numero):
    venda = get_object_or_404(
        Venda.objects
        .select_related(
            "cliente",
            "criada_por",
            "finalizada_por",
            "cancelada_por",
            "cancelamento_autorizado_por",
        )
        .prefetch_related(
            "itens__produto",
            "itens__produto__marca",
            "itens__produto__colecao",
            "itens__variacao_cor",
        ),
        numero=numero,
    )

    Usuario = get_user_model()
    vendedores = (
        Usuario.objects.filter(
            is_active=True,
            perfil__in=[
                Usuario.Perfil.ADMINISTRADOR,
                Usuario.Perfil.GERENTE,
                Usuario.Perfil.VENDEDOR,
            ],
        ).order_by("first_name", "username")
        if pode_editar_vendedor(request.user) else []
    )
    return render(
        request,
        "vendas/ficha.html",
        {
            "venda": venda,
            "pode_editar_vendedor": pode_editar_vendedor(request.user),
            "vendedores": vendedores,
        },
    )
