import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render, get_object_or_404

from comercial.forms import OrcamentoForm
from comercial.services import criar_orcamento

from comercial.models import Orcamento


def _extrair_itens(request):
    """
    Converte o campo oculto `itens_json` em uma lista Python.

    A validação completa dos itens continua sendo responsabilidade
    do OrcamentoService.
    """
    itens_json = request.POST.get("itens_json", "").strip()

    if not itens_json:
        raise ValidationError(
            {
                "itens": (
                    "Adicione pelo menos um produto ao orçamento."
                )
            }
        )

    try:
        itens = json.loads(itens_json)
    except json.JSONDecodeError:
        raise ValidationError(
            {
                "itens": (
                    "Não foi possível interpretar os produtos "
                    "do orçamento."
                )
            }
        )

    if not isinstance(itens, list):
        raise ValidationError(
            {
                "itens": "A lista de produtos possui formato inválido."
            }
        )

    return itens


def _adicionar_erros_ao_form(form, erro):
    """
    Transfere erros gerados pelo Service para o formulário sempre
    que existir um campo correspondente.

    Erros de itens ou erros gerais são exibidos como mensagens.
    """
    if hasattr(erro, "message_dict"):
        for campo, mensagens_erro in erro.message_dict.items():
            if not isinstance(mensagens_erro, (list, tuple)):
                mensagens_erro = [mensagens_erro]

            for mensagem_erro in mensagens_erro:
                if campo in form.fields:
                    form.add_error(campo, mensagem_erro)
                else:
                    form.add_error(None, mensagem_erro)

        return

    mensagens_erro = getattr(
        erro,
        "messages",
        ["Não foi possível salvar o orçamento."],
    )

    for mensagem_erro in mensagens_erro:
        form.add_error(None, mensagem_erro)


@login_required
def cadastrar_orcamento(request):
    if request.method == "POST":
        form = OrcamentoForm(request.POST)

        if form.is_valid():
            try:
                itens = _extrair_itens(request)

                orcamento = criar_orcamento(
                    dados=form.cleaned_data,
                    itens=itens,
                    vendedor=request.user,
                )

            except ValidationError as erro:
                _adicionar_erros_ao_form(form, erro)

            else:
                messages.success(
                    request,
                    (
                        f"Orçamento {orcamento.codigo} "
                        "criado com sucesso."
                    ),
                )

                return redirect(
                    "comercial:ficha",
                    numero=orcamento.numero,
                )

    else:
        form = OrcamentoForm()

    contexto = {
        "form": form,
        "itens_json": request.POST.get(
            "itens_json",
            "[]",
        ),
    }

    return render(
        request,
        "comercial/novo_orcamento.html",
        contexto,
    )

@login_required
def editar_orcamento(request, numero):
    orcamento = get_object_or_404(
        Orcamento,
        numero=numero,
    )

    if request.method == "POST":
        # vamos implementar no próximo passo
        pass

    form = OrcamentoForm(instance=orcamento)

    contexto = {
        "form": form,
        "orcamento": orcamento,
        "modo_edicao": True,
        "itens_json": "[]",
    }

    return render(
        request,
        "comercial/novo_orcamento.html",
        contexto,
    )