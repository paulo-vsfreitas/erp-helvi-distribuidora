from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from produtos.models import Produto


@login_required
def ficha_produto(request, produto_id):
    produto = get_object_or_404(
        Produto.objects.select_related(
            "marca",
            "colecao",
            "genero",
            "tipo_armacao",
        ),
        pk=produto_id,
    )

    return render(
        request,
        "produtos/ficha_produto.html",
        {
            "produto": produto,
            "imagens": produto.imagens.all(),
        },
    )