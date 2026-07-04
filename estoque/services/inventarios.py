from django.db import transaction
from django.utils import timezone

from estoque.models import Inventario, InventarioItem, MovimentacaoEstoque
from produtos.models import Produto


@transaction.atomic
def criar_inventario(usuario, observacao=None):
    inventario = Inventario.objects.create(
        usuario=usuario,
        observacao=observacao,
    )

    inventario.codigo = f"INV-{inventario.pk:05d}"
    inventario.save(update_fields=["codigo"])

    produtos = Produto.objects.filter(ativo=True).order_by("modelo")

    itens = [
        InventarioItem(
            inventario=inventario,
            produto=produto,
            estoque_sistema=produto.estoque_atual or 0,
        )
        for produto in produtos
    ]

    InventarioItem.objects.bulk_create(itens)

    return inventario


@transaction.atomic
def salvar_conferencia_inventario(inventario, dados):
    for item in inventario.itens.all():
        campo = f"quantidade_fisica_{item.id}"
        valor = dados.get(campo)

        if valor == "" or valor is None:
            continue

        quantidade_fisica = int(valor)

        item.quantidade_fisica = quantidade_fisica
        item.diferenca = quantidade_fisica - item.estoque_sistema
        item.save(update_fields=["quantidade_fisica", "diferenca"])


@transaction.atomic
def finalizar_inventario(inventario, usuario):
    if inventario.status == "finalizado":
        return inventario

    for item in inventario.itens.select_related("produto").all():
        if item.quantidade_fisica is None:
            continue

        produto = item.produto
        saldo_anterior = produto.estoque_atual or 0
        saldo_atual = item.quantidade_fisica

        if item.diferenca != 0:
            tipo = "ajuste_positivo" if item.diferenca > 0 else "ajuste_negativo"

            MovimentacaoEstoque.objects.create(
                produto=produto,
                tipo=tipo,
                quantidade=abs(item.diferenca),
                saldo_anterior=saldo_anterior,
                saldo_atual=saldo_atual,
                usuario=usuario,
                origem=f"Inventário {inventario.codigo}",
                observacao="Ajuste automático gerado pelo inventário.",
            )

            produto.estoque_atual = saldo_atual
            produto.save(update_fields=["estoque_atual"])

        item.ajustado = True
        item.save(update_fields=["ajustado"])

    inventario.status = "finalizado"
    inventario.data_finalizacao = timezone.now()
    inventario.save(update_fields=["status", "data_finalizacao"])

    return inventario

def obter_resumo_inventario(inventario):
    itens = inventario.itens.all()

    total = itens.count()
    conferidos = itens.filter(quantidade_fisica__isnull=False).count()
    pendentes = total - conferidos
    divergencias = itens.exclude(diferenca=0).filter(
        quantidade_fisica__isnull=False
    ).count()

    return {
        "total": total,
        "conferidos": conferidos,
        "pendentes": pendentes,
        "divergencias": divergencias,
    }