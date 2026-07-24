from __future__ import annotations

from datetime import date
from typing import Any, Dict

from modules.relatorios.models.relatorio_model import RelatorioModel


class RelatorioService:
    @staticmethod
    def visao_geral(
        *,
        data_inicial: date,
        data_final: date,
        agrupamento: str = "dia",
    ) -> Dict[str, Any]:
        return RelatorioModel.visao_geral(
            data_inicial=data_inicial,
            data_final=data_final,
            agrupamento=agrupamento,
        )

    @staticmethod
    def produtos_mais_vendidos(
        *,
        data_inicial: date,
        data_final: date,
        agrupamento: str = "dia",
    ) -> Dict[str, Any]:
        return RelatorioModel.produtos_mais_vendidos(
            data_inicial=data_inicial,
            data_final=data_final,
            agrupamento=agrupamento,
        )

    @staticmethod
    def clientes_ticket_medio(
        *,
        data_inicial: date,
        data_final: date,
        agrupamento: str = "dia",
    ) -> Dict[str, Any]:
        return RelatorioModel.clientes_ticket_medio(
            data_inicial=data_inicial,
            data_final=data_final,
            agrupamento=agrupamento,
        )

    @staticmethod
    def caixa_por_periodo(
        *,
        data_inicial: date,
        data_final: date,
        agrupamento: str = "dia",
    ) -> Dict[str, Any]:
        return RelatorioModel.caixa_por_periodo(
            data_inicial=data_inicial,
            data_final=data_final,
            agrupamento=agrupamento,
        )

    @staticmethod
    def matriz_vendas_anual(ano: int) -> Dict[str, Any]:
        return RelatorioModel.matriz_vendas_anual(ano=ano)
