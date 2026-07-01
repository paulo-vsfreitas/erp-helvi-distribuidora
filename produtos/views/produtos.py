from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from produtos.forms import ImagemProdutoForm, ProdutoForm
from produtos.models import ImagemProduto, Produto


@login_required
def lista_produtos(request):
    busca = request.GET.get("busca", "").strip()
    status = request.GET.get("status", "ativos")

    produtos = Produto.objects.all().order_by("modelo")

    if status == "ativos":
        produtos = produtos.filter(ativo=True)
    elif status == "inativos":
        produtos = produtos.filter(ativo=False)

    if busca:
        produtos = produtos.filter(
            Q(codigo__icontains=busca)
            | Q(modelo__icontains=busca)
            | Q(marca__nome__icontains=busca)
        )

    return render(request, "produtos/lista_produtos.html", {
        "produtos": produtos,
        "busca": busca,
        "status": status,
    })


@login_required
def novo_produto(request):
    if request.method == "POST":
        form = ProdutoForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            messages.success(request, "Produto cadastrado com sucesso.")
            return redirect("produtos:lista_produtos")
    else:
        form = ProdutoForm()

    return render(request, "produtos/form_produto.html", {
        "form": form,
        "titulo": "Novo Produto",
        "produto": None,
        "imagens": None,
        "imagem_form": None,
    })


@login_required
def editar_produto(request, produto_id):
    produto = get_object_or_404(Produto, pk=produto_id)

    if request.method == "POST":
        form = ProdutoForm(request.POST, request.FILES, instance=produto)

        if form.is_valid():
            form.save()
            messages.success(request, "Produto atualizado com sucesso.")
            return redirect("produtos:lista_produtos")
    else:
        form = ProdutoForm(instance=produto)

    return render(request, "produtos/form_produto.html", {
        "form": form,
        "titulo": "Editar Produto",
        "produto": produto,
        "imagens": produto.imagens.all(),
        "imagem_form": ImagemProdutoForm(),
    })


@login_required
def inativar_produto(request, produto_id):
    produto = get_object_or_404(Produto, pk=produto_id)
    produto.ativo = False
    produto.save()

    messages.success(request, "Produto inativado com sucesso.")
    return redirect("produtos:lista_produtos")


@login_required
def reativar_produto(request, produto_id):
    produto = get_object_or_404(Produto, pk=produto_id)
    produto.ativo = True
    produto.save()

    messages.success(request, "Produto reativado com sucesso.")
    return redirect("produtos:lista_produtos")


@login_required
def galeria_produto(request, produto_id):
    produto = get_object_or_404(Produto, pk=produto_id)
    imagens = produto.imagens.all()

    if request.method == "POST":
        form = ImagemProdutoForm(request.POST, request.FILES)

        if form.is_valid():
            imagem_produto = form.save(commit=False)
            imagem_produto.produto = produto
            imagem_produto.save()

            if imagem_produto.principal:
                ImagemProduto.objects.filter(produto=produto).exclude(pk=imagem_produto.pk).update(principal=False)
                produto.foto = imagem_produto.imagem
                produto.save()

            messages.success(request, "Imagem adicionada com sucesso.")
            return redirect("produtos:editar_produto", produto_id=produto.id)
    else:
        form = ImagemProdutoForm()

    return render(request, "produtos/galeria_produto.html", {
        "produto": produto,
        "imagens": imagens,
        "form": form,
    })


@login_required
def excluir_imagem_produto(request, imagem_id):
    imagem = get_object_or_404(ImagemProduto, pk=imagem_id)
    produto = imagem.produto

    imagem.delete()

    messages.success(request, "Imagem removida com sucesso.")
    return redirect("produtos:editar_produto", produto_id=produto.id)