from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Produto
from .forms import ProdutoForm


@login_required
def lista_produtos(request):
    busca = request.GET.get('busca', '')

    produtos = Produto.objects.all().order_by('modelo')

    if busca:
        produtos = produtos.filter(modelo__icontains=busca)

    return render(request, 'produtos/lista_produtos.html', {
        'produtos': produtos,
        'busca': busca,
    })


@login_required
def novo_produto(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('lista_produtos')
    else:
        form = ProdutoForm()

    return render(request, 'produtos/form_produto.html', {
        'form': form,
        'titulo': 'Novo Produto',
    })


@login_required
def editar_produto(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)

    if request.method == 'POST':
        form = ProdutoForm(request.POST, instance=produto)

        if form.is_valid():
            form.save()
            return redirect('lista_produtos')
    else:
        form = ProdutoForm(instance=produto)

    return render(request, 'produtos/form_produto.html', {
        'form': form,
        'titulo': 'Editar Produto',
    })