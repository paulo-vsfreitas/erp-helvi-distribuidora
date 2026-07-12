from django.db import transaction


@transaction.atomic
def criar_fornecedor(form):
    """
    Cria um fornecedor a partir de um formulário validado.
    """
    return form.save()


@transaction.atomic
def atualizar_fornecedor(form):
    """
    Atualiza um fornecedor a partir de um formulário validado.
    """
    return form.save()