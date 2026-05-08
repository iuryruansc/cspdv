from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, List

from modules.admin.models.dashboard_model import DashboardAdminModel
from utils.backup_runtime import BackupService

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
            "usuarios_ativos": int(resumo.get("usuarios_ativos") or 0),
            "perfis_ativos": int(resumo.get("perfis_ativos") or 0),
            "pdvs_ativos": int(resumo.get("pdvs_ativos") or 0),
            "formas_pagamento_ativas": int(resumo.get("formas_pagamento_ativas") or 0),
            "caixas_abertos": int(resumo.get("caixas_abertos") or 0),
            "contas_vencidas": int(resumo.get("contas_vencidas") or 0),
            "promocoes_vencidas_ativas": int(resumo.get("promocoes_vencidas_ativas") or 0),
            "alertas_dashboard": DashboardAdminService._montar_alertas(resumo),
            "ultimas_vendas": DashboardAdminService._formatar_ultimas_vendas(
                resumo.get("ultimas_vendas") or []
            ),
        }

    @staticmethod
    def _montar_alertas(resumo: Dict[str, Any]) -> List[Dict[str, str]]:
        alertas: List[Dict[str, str]] = []

        contas_vencidas = int(resumo.get("contas_vencidas") or 0)
        if contas_vencidas > 0:
            alertas.append(
                {
                    "nivel": "critico",
                    "texto": f"{contas_vencidas} conta(s) vencida(s) aguardando cobrança.",
                    "acao": "abrir_financeiro",
                }
            )

        promocoes_vencidas = int(resumo.get("promocoes_vencidas_ativas") or 0)
        if promocoes_vencidas > 0:
            alertas.append(
                {
                    "nivel": "aviso",
                    "texto": f"{promocoes_vencidas} promoção(ões) vencida(s) ainda ativa(s).",
                    "acao": "abrir_promocoes",
                }
            )

        caixas_abertos = int(resumo.get("caixas_abertos") or 0)
        if caixas_abertos > 0:
            alertas.append(
                {
                    "nivel": "info",
                    "texto": f"{caixas_abertos} caixa(s) aberto(s) no momento.",
                    "acao": "fechar_caixa",
                }
            )

        if BackupService.backup_esta_vencido():
            alertas.append(
                {
                    "nivel": "aviso",
                    "texto": "Backup fora do intervalo configurado.",
                    "acao": "abrir_configuracoes",
                }
            )

        if not alertas:
            alertas.append(
                {
                    "nivel": "ok",
                    "texto": "Nenhum alerta estrutural no momento.",
                    "acao": "nenhuma",
                }
            )

        return alertas[:4]

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
