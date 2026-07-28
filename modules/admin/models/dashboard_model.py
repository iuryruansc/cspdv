from __future__ import annotations

from decimal import Decimal
from typing import Any, cast

from database.connection import db_cursor
from modules.shared.constants import (
    FLAG_SIM,
    STATUS_CAIXA_ABERTO,
    STATUS_CONTA_ABERTAS,
    STATUS_PROMOCAO_ATIVA,
    STATUS_REEMBOLSO_CONCLUIDO,
)

STATUS_CONTA_ABERTAS_SQL = "', '".join(STATUS_CONTA_ABERTAS)

class DashboardAdminModel:
    @staticmethod
    def obter_resumo() -> dict[str, Any]:
        with db_cursor() as cur:
            produtos_ativos = DashboardAdminModel._contar(
                cur,
                f"SELECT COUNT(*) AS total FROM produtos WHERE ativo = '{FLAG_SIM}'",
            )
            clientes_ativos = DashboardAdminModel._contar(
                cur,
                f"SELECT COUNT(*) AS total FROM clientes WHERE ativo = '{FLAG_SIM}'",
            )
            usuarios_ativos = DashboardAdminModel._contar_ativos_ou_total(cur, "usuarios")
            perfis_ativos = DashboardAdminModel._contar_ativos_ou_total(cur, "perfis")
            pdvs_ativos = DashboardAdminModel._contar_ativos_ou_total(cur, "pdvs")
            formas_pagamento_ativas = DashboardAdminModel._contar_ativos_ou_total(cur, "formas_pagamento")
            caixas_abertos = DashboardAdminModel._contar_caixas_abertos(cur)
            contas_vencidas = DashboardAdminModel._contar_contas_vencidas(cur)
            promocoes_vencidas_ativas = DashboardAdminModel._contar_promocoes_vencidas_ativas(cur)
            recebimentos_dia = DashboardAdminModel._somar_recebimentos_dia(cur)
            reembolsos_dia = DashboardAdminModel._somar_reembolsos_dia(cur)
            cur.execute(
                """
                SELECT
                    COUNT(*) AS vendas_hoje,
                    COALESCE(SUM(v.valor_total), 0) AS faturamento_dia
                FROM vendas v
                WHERE DATE(v.data_hora) = CURDATE()
                  AND LOWER(COALESCE(v.status, '')) NOT IN ('cancelada', 'cancelado', 'c')
                """
            )
            resumo = cast(dict[str, Any] | None, cur.fetchone()) or {}
            vendas_hoje = int(resumo.get("vendas_hoje") or 0)
            faturamento_dia = Decimal(str(resumo.get("faturamento_dia") or 0)) - Decimal(str(reembolsos_dia or 0))
            ultimas_vendas = DashboardAdminModel._buscar_ultimas_vendas(cur)

            return {
                "vendas_hoje": vendas_hoje,
                "faturamento_dia": faturamento_dia,
                "produtos_ativos": produtos_ativos,
                "clientes_ativos": clientes_ativos,
                "usuarios_ativos": usuarios_ativos,
                "perfis_ativos": perfis_ativos,
                "pdvs_ativos": pdvs_ativos,
                "formas_pagamento_ativas": formas_pagamento_ativas,
                "caixas_abertos": caixas_abertos,
                "contas_vencidas": contas_vencidas,
                "promocoes_vencidas_ativas": promocoes_vencidas_ativas,
                "recebimentos_dia": recebimentos_dia,
                "reembolsos_dia": reembolsos_dia,
                "ultimas_vendas": ultimas_vendas,
            }
    @staticmethod
    def _buscar_ultimas_vendas(
        cursor: Any,
    ) -> list[dict[str, Any]]:
        cursor.execute(
            """
            SELECT
                v.id AS numero_venda,
                DATE_FORMAT(v.data_hora, '%d/%m/%Y %H:%i') AS data_hora,
                COALESCE(u.nome, '-') AS operador,
                CASE
                    WHEN v.status = 'CONCLUIDA_COM_PENDENCIA' THEN 'Consig'
                    ELSE COALESCE(
                        (SELECT GROUP_CONCAT(DISTINCT pp.forma_pagamento ORDER BY pp.forma_pagamento SEPARATOR ' / ')
                         FROM pagamento_parcial pp WHERE pp.venda_id = v.id),
                        '-'
                    )
                END AS forma_pagamento,
                COALESCE(v.valor_total, 0) AS total
            FROM vendas v
            LEFT JOIN usuarios u ON u.id = v.usuario_id
            ORDER BY v.data_hora DESC
            LIMIT 10
            """,
        )
        return cast(list[dict[str, Any]], cursor.fetchall())

    @staticmethod
    def _contar(cursor: Any, sql: str) -> int:
        cursor.execute(sql)
        resultado = cast(dict[str, Any] | None, cursor.fetchone()) or {}
        return int(resultado.get("total") or 0)

    @staticmethod
    def _contar_ativos_ou_total(cursor: Any, tabela: str) -> int:
        if tabela in {"usuarios", "perfis", "pdvs", "formas_pagamento"}:
            cursor.execute(f"SELECT COUNT(*) AS total FROM {tabela} WHERE ativo = '{FLAG_SIM}'")
        else:
            cursor.execute(f"SELECT COUNT(*) AS total FROM {tabela}")
        resultado = cast(dict[str, Any] | None, cursor.fetchone()) or {}
        return int(resultado.get("total") or 0)

    @staticmethod
    def _contar_caixas_abertos(cursor: Any) -> int:
        cursor.execute(
            f"""
            SELECT COUNT(*) AS total
            FROM caixas
            WHERE LOWER(status) = %s
              AND ativo = %s
            """,
            (STATUS_CAIXA_ABERTO, FLAG_SIM),
        )
        resultado = cast(dict[str, Any] | None, cursor.fetchone()) or {}
        return int(resultado.get("total") or 0)

    @staticmethod
    def _contar_contas_vencidas(cursor: Any) -> int:
        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM contas_receber
            WHERE ativo = %s
              AND status IN ('{STATUS_CONTA_ABERTAS_SQL}')
              AND data_vencimento < CURDATE()
            """,
            (FLAG_SIM,),
        )
        resultado = cast(dict[str, Any] | None, cursor.fetchone()) or {}
        return int(resultado.get("total") or 0)

    @staticmethod
    def _contar_promocoes_vencidas_ativas(cursor: Any) -> int:
        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM promocoes
            WHERE status = %s
              AND data_fim < NOW()
              AND ativo = %s
            """,
            (STATUS_PROMOCAO_ATIVA, FLAG_SIM),
        )
        resultado = cast(dict[str, Any] | None, cursor.fetchone()) or {}
        return int(resultado.get("total") or 0)

    @staticmethod
    def _somar_recebimentos_dia(cursor: Any) -> Decimal:
        cursor.execute(
            """
            SELECT COALESCE(SUM(valor_recebido), 0) AS total
            FROM contas_receber_recebimentos
            WHERE DATE(data_recebimento) = CURDATE()
              AND ativo = %s
            """,
            (FLAG_SIM,),
        )
        resultado = cast(dict[str, Any] | None, cursor.fetchone()) or {}
        return Decimal(str(resultado.get("total") or 0))

    @staticmethod
    def _somar_reembolsos_dia(cursor: Any) -> Decimal:
        cursor.execute(
            """
            SELECT COALESCE(SUM(valor_total), 0) AS total
            FROM venda_reembolsos
            WHERE DATE(data_hora) = CURDATE()
              AND ativo = %s
              AND status = %s
            """,
            (FLAG_SIM, STATUS_REEMBOLSO_CONCLUIDO),
        )
        resultado = cast(dict[str, Any] | None, cursor.fetchone()) or {}
        return Decimal(str(resultado.get("total") or 0))
