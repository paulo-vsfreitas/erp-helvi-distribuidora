"""
Service de composição do Dashboard Financeiro.

Os cálculos e indicadores financeiros reutilizáveis permanecem em
financeiro.services.indicadores_service.
"""

from financeiro.services.indicadores_service import (
    obter_dados_dashboard_financeiro,
)


__all__ = [
    "obter_dados_dashboard_financeiro",
]
