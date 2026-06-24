from django.shortcuts import render, redirect
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