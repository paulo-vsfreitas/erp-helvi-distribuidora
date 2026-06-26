from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Cliente
from .forms import ClienteForm


@login_required
def lista_clientes(request):
    busca = request.GET.get('busca', '')

    clientes = Cliente.objects.all().order_by('nome_fantasia')

    if busca:
        clientes = clientes.filter(nome_fantasia__icontains=busca)

    return render(request, 'clientes/lista_clientes.html', {
        'clientes': clientes,
        'busca': busca,
    })


@login_required
def novo_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('lista_clientes')
    else:
        form = ClienteForm()

    return render(request, 'clientes/form_cliente.html', {
        'form': form,
        'titulo': 'Nova Ótica',
    })


@login_required
def editar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)

    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)

        if form.is_valid():
            form.save()
            return redirect('lista_clientes')
    else:
        form = ClienteForm(instance=cliente)

    return render(request, 'clientes/form_cliente.html', {
        'form': form,
        'titulo': 'Editar Ótica',
    })