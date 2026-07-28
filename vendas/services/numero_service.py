from django.db import transaction
from django.db.models import Max

from vendas.models import SequenciaDocumento, Venda


@transaction.atomic
def gerar_proximo_numero_documento(tipo, model, campo_numero="numero"):
    maior_numero_existente = (
        model.objects.aggregate(
            maior=Max(campo_numero),
        )["maior"]
        or 0
    )

    sequencia, _ = (
        SequenciaDocumento.objects
        .select_for_update()
        .get_or_create(
            tipo=tipo,
            defaults={
                "ultimo_numero": maior_numero_existente,
            },
        )
    )

    if sequencia.ultimo_numero < maior_numero_existente:
        sequencia.ultimo_numero = maior_numero_existente

    sequencia.ultimo_numero += 1

    sequencia.save(
        update_fields=[
            "ultimo_numero",
            "atualizado_em",
        ]
    )

    return sequencia.ultimo_numero


def gerar_proximo_numero_venda():
    return gerar_proximo_numero_documento(
        tipo=SequenciaDocumento.TIPO_VENDA,
        model=Venda,
    )