import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import get_user_model

from financeiro.models import ContaFinanceira
from vendas.forms import VendaForm
from vendas.services.processamento_venda_service import (
    processar_nova_venda,
)
from vendas.models import Venda
from vendas.services.cadastro_service import editar_venda_em_aberto, pode_editar_vendedor


def _contexto_vendedores(usuario):
    if not pode_editar_vendedor(usuario):
        return {"pode_editar_vendedor": False, "vendedores": []}
    Usuario = get_user_model()
    return {
        "pode_editar_vendedor": True,
        "vendedores": Usuario.objects.filter(
            is_active=True,
            perfil__in=[
                Usuario.Perfil.ADMINISTRADOR,
                Usuario.Perfil.GERENTE,
                Usuario.Perfil.VENDEDOR,
            ],
        ).order_by("first_name", "username"),
    }


def _serializar_itens(venda):
    itens = []
    for item in venda.itens.select_related("produto", "variacao_cor").prefetch_related("produto__variacoes_cor"):
        produto = item.produto
        itens.append({
            "produto_id": produto.pk,
            "descricao": str(produto),
            "preco_unitario": item.preco_unitario,
            "desconto": item.desconto,
            "quantidade": item.quantidade,
            "estoque": produto.estoque_atual,
            "variacao_cor_id": item.variacao_cor_id,
            "variacoes": [
                {"id": cor.pk, "nome": cor.nome or cor.codigo, "codigo": cor.codigo, "estoque": cor.estoque}
                for cor in produto.variacoes_cor.all()
            ],
        })
    return json.dumps(itens, cls=DjangoJSONEncoder)


@login_required
def nova_venda(request):
    if request.method == "POST":
        form = VendaForm(request.POST)

        if form.is_valid():
            try:
                resultado = processar_nova_venda(
                    form=form,
                    post=request.POST,
                    usuario=request.user,
                )
            except ValidationError as erro:
                mensagens = getattr(
                    erro,
                    "messages",
                    [str(erro)],
                )

                for mensagem in mensagens:
                    messages.error(
                        request,
                        mensagem,
                    )
            else:
                venda = resultado["venda"]

                if resultado["finalizada"]:
                    mensagem = (
                        f"Venda nº {venda.numero} finalizada "
                        "com sucesso."
                    )

                    if resultado["troco"] > 0:
                        mensagem += (
                            f" Troco: R$ "
                            f"{resultado['troco']:.2f}."
                        )

                    messages.success(
                        request,
                        mensagem,
                    )

                    return redirect(
                        "vendas:ficha",
                        venda.numero,
                    )

                messages.success(
                    request,
                    (
                        f"Venda nº {venda.numero} salva "
                        "em aberto com sucesso."
                    ),
                )

                return redirect(
                    "vendas:lista",
                )
    else:
        form = VendaForm()

    contas_financeiras = (
        ContaFinanceira.objects
        .filter(ativo=True)
        .order_by(
            "-conta_padrao",
            "nome",
        )
    )

    contexto = {
        "form": form,
        "modo_edicao": False,
        "itens_json": "[]",
        "vendedor_selecionado_id": request.POST.get("vendedor") or request.user.pk,
    }
    contexto.update(_contexto_vendedores(request.user))
    return render(
        request,
        "vendas/nova.html",
        contexto,
    )


@login_required
def editar_venda(request, numero):
    venda = get_object_or_404(Venda, numero=numero)
    if venda.status != Venda.STATUS_EM_ABERTO:
        messages.error(request, "Somente vendas em aberto podem ser editadas.")
        return redirect("vendas:ficha", venda.numero)

    if request.method == "POST":
        form = VendaForm(request.POST, instance=venda)
        if form.is_valid():
            try:
                editar_venda_em_aberto(
                    venda=venda, form=form, post=request.POST, usuario=request.user
                )
            except ValidationError as erro:
                for mensagem in getattr(erro, "messages", [str(erro)]):
                    messages.error(request, mensagem)
            else:
                messages.success(request, f"Venda nº {venda.numero} atualizada com sucesso.")
                return redirect("vendas:ficha", venda.numero)
        itens_json = _serializar_itens(venda)
    else:
        form = VendaForm(instance=venda)
        itens_json = _serializar_itens(venda)

    contexto = {
        "form": form,
        "venda": venda,
        "modo_edicao": True,
        "itens_json": itens_json,
        "vendedor_selecionado_id": request.POST.get("vendedor") or venda.criada_por_id,
    }
    contexto.update(_contexto_vendedores(request.user))
    return render(request, "vendas/nova.html", contexto)
