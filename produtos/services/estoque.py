from django.core.exceptions import ValidationError
from django.db import transaction

from estoque.services import ajustar_estoque, registrar_entrada_estoque
from estoque.services.saldos import sincronizar_estoque_produto
from produtos.models import VariacaoCor


def _ajustar_saldo_se_necessario(*, produto, quantidade, usuario, variacao_cor=None):
    atual = variacao_cor.estoque if variacao_cor is not None else produto.estoque_atual

    if atual == quantidade:
        return

    if atual == 0 and quantidade > 0:
        registrar_entrada_estoque(
            produto=produto,
            variacao_cor=variacao_cor,
            quantidade=quantidade,
            usuario=usuario,
            origem="Cadastro de Produto",
            local="Estoque Principal",
            observacao="Estoque inicial informado no cadastro/edição do produto.",
        )
        return

    ajustar_estoque(
        produto=produto,
        variacao_cor=variacao_cor,
        quantidade_correta=quantidade,
        usuario=usuario,
        motivo="Alteração pelo cadastro/edição do produto",
        local="Estoque Principal",
    )


@transaction.atomic
def salvar_produto_com_cores(form, formset, *, usuario=None):
    """Salva produto/cores e encaminha qualquer mudança de saldo ao domínio de estoque."""
    produto_existente = form.instance.pk is not None
    estoque_simples_anterior = form.instance.estoque_atual if produto_existente else 0
    estoque_simples_desejado = form.cleaned_data.get("estoque_atual") or 0

    # O saldo nunca é persistido pelo ModelForm. Ele será aplicado pelos services.
    produto = form.save(commit=False)
    produto.estoque_atual = estoque_simples_anterior
    produto.save()
    form.save_m2m()

    formset.instance = produto

    # Ao migrar um produto de estoque simples para controle por cor, zera o
    # saldo simples com histórico antes de criar a primeira variação.
    vai_ter_variacoes = any(
        hasattr(cor_form, "cleaned_data")
        and not cor_form.cleaned_data.get("DELETE")
        and (cor_form.cleaned_data.get("codigo") or "").strip()
        for cor_form in formset.forms
    )
    if (
        not produto.variacoes_cor.exists()
        and vai_ter_variacoes
        and produto.estoque_atual > 0
    ):
        ajustar_estoque(
            produto=produto,
            quantidade_correta=0,
            usuario=usuario,
            motivo="Conversão do produto para controle de estoque por variação",
            local="Estoque Principal",
        )
        produto.refresh_from_db()

    saldos_desejados = {}
    variacoes_novas = []
    variacoes_apagar = []

    for cor_form in formset.forms:
        if not hasattr(cor_form, "cleaned_data"):
            continue

        if cor_form.cleaned_data.get("DELETE"):
            if cor_form.instance.pk:
                variacoes_apagar.append(cor_form.instance)
            continue

        codigo = (cor_form.cleaned_data.get("codigo") or "").strip().upper()
        if not codigo:
            continue

        desejado = cor_form.cleaned_data.get("estoque") or 0
        variacao = cor_form.save(commit=False)
        variacao.produto = produto

        if variacao.pk:
            # Não permita que o form grave o saldo diretamente.
            atual = VariacaoCor.objects.get(pk=variacao.pk).estoque
            variacao.estoque = atual
            variacao.save()
            saldos_desejados[variacao.pk] = desejado
        else:
            variacao.estoque = 0
            variacao.save()
            variacoes_novas.append((variacao, desejado))

    for variacao in variacoes_apagar:
        if variacao.movimentacoes_estoque.exists():
            raise ValidationError(
                "Não é possível remover uma variação com histórico de estoque."
            )
        variacao.delete()

    tem_variacoes = produto.variacoes_cor.exists()

    if tem_variacoes:
        # Produto com variações não mantém saldo simples paralelo.
        for pk, desejado in saldos_desejados.items():
            variacao = VariacaoCor.objects.get(pk=pk)
            _ajustar_saldo_se_necessario(
                produto=produto,
                variacao_cor=variacao,
                quantidade=desejado,
                usuario=usuario,
            )

        for variacao, desejado in variacoes_novas:
            _ajustar_saldo_se_necessario(
                produto=produto,
                variacao_cor=variacao,
                quantidade=desejado,
                usuario=usuario,
            )

        sincronizar_estoque_produto(produto)
    else:
        _ajustar_saldo_se_necessario(
            produto=produto,
            quantidade=estoque_simples_desejado,
            usuario=usuario,
        )

    produto.refresh_from_db()
    return produto
