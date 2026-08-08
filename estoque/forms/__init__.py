from .ajustes import *
from .entradas import *
from .saidas import *


def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    produto_id = (
        self.data.get("produto")
        or self.initial.get("produto")
    )

    if produto_id:
        try:
            produto_id = int(produto_id)
        except (TypeError, ValueError):
            return

        self.fields["variacao_cor"].queryset = (
            VariacaoCor.objects
            .filter(produto_id=produto_id)
            .order_by("codigo", "nome")
        )