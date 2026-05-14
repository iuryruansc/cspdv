from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, List, Optional, Sequence, cast

from database.connection import get_connection

class DashboardAdminModel:
    @staticmethod
    def obter_resumo() -> Dict[str, Any]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            produtos_ativos = DashboardAdminModel._contar(
                cursor,
                "SELECT COUNT(*) AS total FROM produtos WHERE ativo = 'S'",
            )
            clientes_ativos = DashboardAdminModel._contar(
                cursor,
                "SELECT COUNT(*) AS total FROM clientes WHERE ativo = 'S'",
            )
            usuarios_ativos = DashboardAdminModel._contar_ativos_ou_total(cursor, "usuarios")
            perfis_ativos = DashboardAdminModel._contar_ativos_ou_total(cursor, "perfis")
            pdvs_ativos = DashboardAdminModel._contar_ativos_ou_total(cursor, "pdvs")
            formas_pagamento_ativas = DashboardAdminModel._contar_ativos_ou_total(cursor, "formas_pagamento")
            caixas_abertos = DashboardAdminModel._contar_caixas_abertos(cursor)
            contas_vencidas = DashboardAdminModel._contar_contas_vencidas(cursor)
            promocoes_vencidas_ativas = DashboardAdminModel._contar_promocoes_vencidas_ativas(cursor)
            recebimentos_dia = DashboardAdminModel._somar_recebimentos_dia(cursor)
            reembolsos_dia = DashboardAdminModel._somar_reembolsos_dia(cursor)

            vendas_hoje = 0
            faturamento_dia = Decimal("0")
            ultimas_vendas: List[Dict[str, Any]] = []

            if DashboardAdminModel._tabela_existe(cursor, "vendas"):
                colunas_vendas = DashboardAdminModel._listar_colunas(cursor, "vendas")
                coluna_data = DashboardAdminModel._primeira_coluna_existente(
                    colunas_vendas,
                    ("data_venda", "createdAt", "created_at", "data_emissao"),
                )
                coluna_total = DashboardAdminModel._primeira_coluna_existente(
                    colunas_vendas,
                    ("total", "valor_total", "total_liquido", "valor_liquido"),
                )
                coluna_status = DashboardAdminModel._primeira_coluna_existente(
                    colunas_vendas,
                    ("status", "situacao"),
                )

                if coluna_data and coluna_total:
                    where_partes = [f"DATE(v.{coluna_data}) = CURDATE()"]
                    if coluna_status:
                        where_partes.append(
                            f"LOWER(COALESCE(v.{coluna_status}, '')) NOT IN ('cancelada', 'cancelado', 'c')"
                        )
                    where_sql = " AND ".join(where_partes)
                    cursor.execute(
                        f"""
                        SELECT
                            COUNT(*) AS vendas_hoje,
                            COALESCE(SUM(v.{coluna_total}), 0) AS faturamento_dia
                        FROM vendas v
                        WHERE {where_sql}
                        """
                    )
                    resumo = cast(Optional[Dict[str, Any]], cursor.fetchone()) or {}
                    vendas_hoje = int(resumo.get("vendas_hoje") or 0)
                    faturamento_dia = Decimal(str(resumo.get("faturamento_dia") or 0))

                    ultimas_vendas = DashboardAdminModel._buscar_ultimas_vendas(
                        cursor,
                        colunas_vendas,
                        coluna_data=coluna_data,
                        coluna_total=coluna_total,
                    )

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
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def _buscar_ultimas_vendas(
        cursor: Any,
        colunas_vendas: Sequence[str],
        *,
        coluna_data: str,
        coluna_total: str,
    ) -> List[Dict[str, Any]]:
        coluna_id = DashboardAdminModel._primeira_coluna_existente(colunas_vendas, ("id", "id_venda"))
        coluna_forma_pgto = DashboardAdminModel._primeira_coluna_existente(
            colunas_vendas,
            ("forma_pagamento", "forma_pgto", "pagamento"),
        )
        coluna_operador = DashboardAdminModel._primeira_coluna_existente(
            colunas_vendas,
            ("operador", "usuario_nome"),
        )
        coluna_usuario_id = DashboardAdminModel._primeira_coluna_existente(
            colunas_vendas,
            ("usuario_id", "operador_id"),
        )

        if coluna_id is None:
            return []

        select_partes = [
            f"v.{coluna_id} AS numero_venda",
            f"DATE_FORMAT(v.{coluna_data}, '%d/%m/%Y %H:%i') AS data_hora",
            f"COALESCE(v.{coluna_total}, 0) AS total",
        ]
        joins: List[str] = []

        if coluna_operador:
            select_partes.append(f"COALESCE(v.{coluna_operador}, '-') AS operador")
        elif coluna_usuario_id and DashboardAdminModel._tabela_existe(cursor, "usuarios"):
            select_partes.append("COALESCE(u.nome, '-') AS operador")
            joins.append(f"LEFT JOIN usuarios u ON u.id = v.{coluna_usuario_id}")
        else:
            select_partes.append("'-' AS operador")

        if coluna_forma_pgto:
            select_partes.append(f"COALESCE(v.{coluna_forma_pgto}, '-') AS forma_pagamento")
        else:
            select_partes.append("'-' AS forma_pagamento")

        joins_sql = "\n".join(joins)
        cursor.execute(
            f"""
            SELECT
                {", ".join(select_partes)}
            FROM vendas v
            {joins_sql}
            ORDER BY v.{coluna_data} DESC
            LIMIT 10
            """
        )
        return cast(List[Dict[str, Any]], cursor.fetchall())

    @staticmethod
    def _contar(cursor: Any, sql: str) -> int:
        cursor.execute(sql)
        resultado = cast(Optional[Dict[str, Any]], cursor.fetchone()) or {}
        return int(resultado.get("total") or 0)

    @staticmethod
    def _contar_ativos_ou_total(cursor: Any, tabela: str) -> int:
        if not DashboardAdminModel._tabela_existe(cursor, tabela):
            return 0

        colunas = DashboardAdminModel._listar_colunas(cursor, tabela)
        if "ativo" in colunas:
            cursor.execute(f"SELECT COUNT(*) AS total FROM {tabela} WHERE ativo = 'S'")
        else:
            cursor.execute(f"SELECT COUNT(*) AS total FROM {tabela}")
        resultado = cast(Optional[Dict[str, Any]], cursor.fetchone()) or {}
        return int(resultado.get("total") or 0)

    @staticmethod
    def _contar_caixas_abertos(cursor: Any) -> int:
        if not DashboardAdminModel._tabela_existe(cursor, "caixas"):
            return 0

        colunas = DashboardAdminModel._listar_colunas(cursor, "caixas")
        where_partes = []
        if "status" in colunas:
            where_partes.append("LOWER(status) = 'aberto'")
        if "ativo" in colunas:
            where_partes.append("ativo = 'S'")

        if where_partes:
            cursor.execute(f"SELECT COUNT(*) AS total FROM caixas WHERE {' AND '.join(where_partes)}")
        else:
            cursor.execute("SELECT COUNT(*) AS total FROM caixas")

        resultado = cast(Optional[Dict[str, Any]], cursor.fetchone()) or {}
        return int(resultado.get("total") or 0)

    @staticmethod
    def _contar_contas_vencidas(cursor: Any) -> int:
        if not DashboardAdminModel._tabela_existe(cursor, "contas_receber"):
            return 0
        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM contas_receber
            WHERE ativo = 'S'
              AND status IN ('PENDENTE', 'PARCIALMENTE_RECEBIDA')
              AND data_vencimento < CURDATE()
            """
        )
        resultado = cast(Optional[Dict[str, Any]], cursor.fetchone()) or {}
        return int(resultado.get("total") or 0)

    @staticmethod
    def _contar_promocoes_vencidas_ativas(cursor: Any) -> int:
        if not DashboardAdminModel._tabela_existe(cursor, "promocoes"):
            return 0
        colunas = DashboardAdminModel._listar_colunas(cursor, "promocoes")
        if "status" not in colunas or "data_fim" not in colunas:
            return 0
        where_partes = [
            "status = 'ATIVA'",
            "data_fim < NOW()",
        ]
        if "ativo" in colunas:
            where_partes.append("ativo = 'S'")
        cursor.execute(
            f"""
            SELECT COUNT(*) AS total
            FROM promocoes
            WHERE {' AND '.join(where_partes)}
            """
        )
        resultado = cast(Optional[Dict[str, Any]], cursor.fetchone()) or {}
        return int(resultado.get("total") or 0)

    @staticmethod
    def _somar_recebimentos_dia(cursor: Any) -> Decimal:
        if not DashboardAdminModel._tabela_existe(cursor, "contas_receber_recebimentos"):
            return Decimal("0")

        colunas = DashboardAdminModel._listar_colunas(cursor, "contas_receber_recebimentos")
        if "data_recebimento" not in colunas or "valor_recebido" not in colunas:
            return Decimal("0")

        where_partes = ["DATE(data_recebimento) = CURDATE()"]
        if "ativo" in colunas:
            where_partes.append("ativo = 'S'")

        cursor.execute(
            f"""
            SELECT COALESCE(SUM(valor_recebido), 0) AS total
            FROM contas_receber_recebimentos
            WHERE {' AND '.join(where_partes)}
            """
        )
        resultado = cast(Optional[Dict[str, Any]], cursor.fetchone()) or {}
        return Decimal(str(resultado.get("total") or 0))

    @staticmethod
    def _somar_reembolsos_dia(cursor: Any) -> Decimal:
        if not DashboardAdminModel._tabela_existe(cursor, "venda_reembolsos"):
            return Decimal("0")

        colunas = DashboardAdminModel._listar_colunas(cursor, "venda_reembolsos")
        coluna_data = DashboardAdminModel._primeira_coluna_existente(
            colunas,
            ("data_hora", "createdAt", "created_at"),
        )
        if coluna_data is None or "valor_total" not in colunas:
            return Decimal("0")

        where_partes = [f"DATE({coluna_data}) = CURDATE()"]
        if "ativo" in colunas:
            where_partes.append("ativo = 'S'")
        if "status" in colunas:
            where_partes.append("status = 'CONCLUIDO'")

        cursor.execute(
            f"""
            SELECT COALESCE(SUM(valor_total), 0) AS total
            FROM venda_reembolsos
            WHERE {' AND '.join(where_partes)}
            """
        )
        resultado = cast(Optional[Dict[str, Any]], cursor.fetchone()) or {}
        return Decimal(str(resultado.get("total") or 0))

    @staticmethod
    def _tabela_existe(cursor: Any, tabela: str) -> bool:
        cursor.execute("SHOW TABLES LIKE %s", (tabela,))
        return cursor.fetchone() is not None

    @staticmethod
    def _listar_colunas(cursor: Any, tabela: str) -> List[str]:
        cursor.execute(f"SHOW COLUMNS FROM {tabela}")
        return [str(item["Field"]) for item in cast(List[Dict[str, Any]], cursor.fetchall())]

    @staticmethod
    def _primeira_coluna_existente(colunas: Sequence[str], candidatas: Sequence[str]) -> Optional[str]:
        for candidata in candidatas:
            if candidata in colunas:
                return candidata
        return None
