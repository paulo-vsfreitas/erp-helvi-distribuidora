import json

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import redirect, render, get_object_or_404

from comercial.forms import OrcamentoForm
from comercial.services import (
    criar_orcamento,
    editar_orcamento as editar_orcamento_service,
)

from comercial.models import Orcamento
from usuarios.decorators import permissao_requerida
from usuarios.permissoes import Modulo


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


def _serializar_itens(orcamento):
    itens = []

    for item in orcamento.itens.select_related(
        "produto",
        "produto__marca",
    ):
        itens.append(
            {
                "produto_id": item.produto_id,
                "codigo": item.produto.codigo,
                "descricao": item.produto.modelo,
                "marca": (
                    item.produto.marca.nome
                    if item.produto.marca
                    else ""
                ),
                "quantidade": item.quantidade,
                "valor_unitario": item.valor_unitario,
                "desconto": item.desconto,
            }
        )

    return json.dumps(itens, cls=DjangoJSONEncoder)


@permissao_requerida(Modulo.VENDAS)
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

@permissao_requerida(Modulo.VENDAS)
def editar_orcamento(request, numero):
    orcamento = get_object_or_404(
        Orcamento,
        numero=numero,
    )

    if request.method == "POST":
        form = OrcamentoForm(
            request.POST,
            instance=orcamento,
        )

        if form.is_valid():
            try:
                itens = _extrair_itens(request)
                orcamento = editar_orcamento_service(
                    orcamento=orcamento,
                    dados=form.cleaned_data,
                    itens=itens,
                )
            except ValidationError as erro:
                _adicionar_erros_ao_form(form, erro)
            else:
                messages.success(
                    request,
                    f"Orçamento {orcamento.codigo} atualizado com sucesso.",
                )
                return redirect(
                    "comercial:ficha",
                    numero=orcamento.numero,
                )
    else:
        form = OrcamentoForm(instance=orcamento)

    contexto = {
        "form": form,
        "orcamento": orcamento,
        "modo_edicao": True,
        "itens_json": (
            request.POST.get("itens_json", "[]")
            if request.method == "POST"
            else _serializar_itens(orcamento)
        ),
    }

    return render(
        request,
        "comercial/novo_orcamento.html",
        contexto,
    )
