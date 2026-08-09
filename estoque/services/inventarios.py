from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from estoque.models import (
    Inventario,
    InventarioItem,
    MovimentacaoEstoque,
)
from produtos.models import Produto


@transaction.atomic
def criar_inventario(usuario, observacao=None):
    inventario = Inventario.objects.create(
        usuario=usuario,
        observacao=observacao,
    )

    inventario.codigo = f"INV-{inventario.pk:05d}"
    inventario.save(update_fields=["codigo"])

    produtos = (
        Produto.objects
        .filter(ativo=True)
        .prefetch_related("variacoes_cor")
        .order_by("modelo", "codigo")
    )

    itens = []

    for produto in produtos:
        variacoes = list(produto.variacoes_cor.all())

        if variacoes:
            for variacao in variacoes:
                itens.append(
                    InventarioItem(
                        inventario=inventario,
                        produto=produto,
                        variacao_cor=variacao,
                        estoque_sistema=variacao.estoque or 0,
                    )
                )
        else:
            itens.append(
                InventarioItem(
                    inventario=inventario,
                    produto=produto,
                    variacao_cor=None,
                    estoque_sistema=produto.estoque_atual or 0,
                )
            )

    InventarioItem.objects.bulk_create(itens)

    return inventario


@transaction.atomic
def salvar_conferencia_inventario(inventario, dados):
    for item in inventario.itens.all():
        campo = f"quantidade_fisica_{item.id}"
        valor = dados.get(campo)

        if valor == "" or valor is None:
            continue

        try:
            quantidade_fisica = int(valor)
        except (TypeError, ValueError):
            raise ValidationError(
                "A quantidade física informada é inválida."
            )

        if quantidade_fisica < 0:
            raise ValidationError(
                "A quantidade física não pode ser negativa."
            )

        item.quantidade_fisica = quantidade_fisica
        item.diferenca = (
            quantidade_fisica - item.estoque_sistema
        )

        item.save(
            update_fields=[
                "quantidade_fisica",
                "diferenca",
            ]
        )


def _recalcular_estoque_total_produto(produto):
    total_variacoes = (
        produto.variacoes_cor.aggregate(
            total=Sum("estoque")
        )["total"]
        or 0
    )

    produto.estoque_atual = total_variacoes
    produto.save(update_fields=["estoque_atual"])


@transaction.atomic
def finalizar_inventario(inventario, usuario):
    if inventario.status == "finalizado":
        return inventario

    itens = (
        inventario.itens
        .select_related(
            "produto",
            "variacao_cor",
        )
        .all()
    )

    produtos_com_variacao_alterada = set()

    for item in itens:
        if item.quantidade_fisica is None:
            continue

        produto = item.produto

        if item.variacao_cor:
            variacao = item.variacao_cor

            saldo_anterior = variacao.estoque or 0
            saldo_atual = item.quantidade_fisica

            if saldo_anterior != saldo_atual:
                diferenca = saldo_atual - saldo_anterior

                tipo = (
                    "ajuste_positivo"
                    if diferenca > 0
                    else "ajuste_negativo"
                )

                MovimentacaoEstoque.objects.create(
                    produto=produto,
                    variacao_cor=variacao,
                    tipo=tipo,
                    quantidade=abs(diferenca),
                    saldo_anterior=saldo_anterior,
                    saldo_atual=saldo_atual,
                    usuario=usuario,
                    origem=f"Inventário {inventario.codigo}",
                    observacao=(
                        "Ajuste automático gerado pelo "
                        "inventário."
                    ),
                )

                variacao.estoque = saldo_atual
                variacao.save(update_fields=["estoque"])

                produtos_com_variacao_alterada.add(
                    produto.pk
                )

        else:
            saldo_anterior = produto.estoque_atual or 0
            saldo_atual = item.quantidade_fisica

            if saldo_anterior != saldo_atual:
                diferenca = saldo_atual - saldo_anterior

                tipo = (
                    "ajuste_positivo"
                    if diferenca > 0
                    else "ajuste_negativo"
                )

                MovimentacaoEstoque.objects.create(
                    produto=produto,
                    variacao_cor=None,
                    tipo=tipo,
                    quantidade=abs(diferenca),
                    saldo_anterior=saldo_anterior,
                    saldo_atual=saldo_atual,
                    usuario=usuario,
                    origem=f"Inventário {inventario.codigo}",
                    observacao=(
                        "Ajuste automático gerado pelo "
                        "inventário."
                    ),
                )

                produto.estoque_atual = saldo_atual
                produto.save(
                    update_fields=["estoque_atual"]
                )

        item.ajustado = True
        item.save(update_fields=["ajustado"])

    if produtos_com_variacao_alterada:
        produtos = (
            Produto.objects
            .filter(
                pk__in=produtos_com_variacao_alterada
            )
            .prefetch_related("variacoes_cor")
        )

        for produto in produtos:
            _recalcular_estoque_total_produto(
                produto
            )

    inventario.status = "finalizado"
    inventario.data_finalizacao = timezone.now()

    inventario.save(
        update_fields=[
            "status",
            "data_finalizacao",
        ]
    )

    return inventario


def obter_resumo_inventario(inventario):
    itens = inventario.itens.all()

    total = itens.count()

    conferidos = itens.filter(
        quantidade_fisica__isnull=False
    ).count()

    pendentes = total - conferidos

    divergencias = (
        itens
        .exclude(diferenca=0)
        .filter(
            quantidade_fisica__isnull=False
        )
        .count()
    )

    return {
        "total": total,
        "conferidos": conferidos,
        "pendentes": pendentes,
        "divergencias": divergencias,
    }