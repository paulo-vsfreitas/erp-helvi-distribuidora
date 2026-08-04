from .cadastro import nova_venda
from .cancelamento import cancelar_venda_view
from .ficha import ficha_venda
from .finalizacao import finalizar_venda_view
from .lista import lista_vendas
from .relatorios import relatorio_vendas

__all__ = [
    "ficha_venda",
    "cancelar_venda_view",
    "finalizar_venda_view",
    "lista_vendas",
    "nova_venda",
]
