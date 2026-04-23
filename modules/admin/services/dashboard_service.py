from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, List

from modules.admin.models.dashboard_model import DashboardAdminModel


class DashboardAdminService:
    @staticmethod
    def carregar_dashboard() -> Dict[str, Any]:
        resumo = DashboardAdminModel.obter_resumo()
        return {
            "vendas_hoje": int(resumo.get("vendas_hoje") or 0),
            "faturamento_dia": DashboardAdminService._formatar_moeda(
                Decimal(str(resumo.get("faturamento_dia") or 0))
            ),
            "produtos_ativos": int(resumo.get("produtos_ativos") or 0),
            "clientes_ativos": int(resumo.get("clientes_ativos") or 0),
            "ultimas_vendas": DashboardAdminService._formatar_ultimas_vendas(
                resumo.get("ultimas_vendas") or []
            ),
        }

    @staticmethod
    def _formatar_ultimas_vendas(rows: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        formatadas: List[Dict[str, str]] = []
        for row in rows:
            formatadas.append(
                {
                    "numero_venda": str(row.get("numero_venda") or "-"),
                    "data_hora": str(row.get("data_hora") or "-"),
                    "operador": str(row.get("operador") or "-"),
                    "forma_pagamento": str(row.get("forma_pagamento") or "-"),
                    "total": DashboardAdminService._formatar_moeda(Decimal(str(row.get("total") or 0))),
                }
            )
        return formatadas

    @staticmethod
    def _formatar_moeda(valor: Decimal) -> str:
        texto = f"{valor:,.2f}"
        return f"R$ {texto.replace(',', 'X').replace('.', ',').replace('X', '.')}"
