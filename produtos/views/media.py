import mimetypes
from pathlib import Path

from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404

from produtos.models import ImagemProduto, Produto


def _entregar_campo(campo):
    if not campo:
        raise Http404("Imagem não cadastrada.")
    try:
        campo.open("rb")
    except (FileNotFoundError, OSError, ValueError):
        raise Http404("Imagem não encontrada no storage.")

    content_type = mimetypes.guess_type(Path(campo.name).name)[0] or "image/jpeg"
    response = FileResponse(campo, content_type=content_type)
    response["Cache-Control"] = "private, max-age=300"
    return response


@login_required
def visualizar_foto_produto(request, produto_id):
    produto = get_object_or_404(Produto, pk=produto_id)
    return _entregar_campo(produto.foto)


@login_required
def visualizar_imagem_produto(request, imagem_id):
    imagem = get_object_or_404(ImagemProduto, pk=imagem_id)
    return _entregar_campo(imagem.imagem)
