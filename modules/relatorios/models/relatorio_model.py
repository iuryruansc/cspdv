from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional, cast

from database.connection import get_connection
from modules.shared.constants import FLAG_SIM, STATUS_VENDA_OPERACIONAL

STATUS_VENDA_SQL = "', '".join(STATUS_VENDA_OPERACIONAL)


def _periodo(data_inicial: date, data_final: date):
    inicio = data_inicial
    fim = data_final + timedelta(days=1)
    return inicio, fim


def _buscar_reembolsos_periodo(cursor: Any, inicio, fim) -> Decimal:
    cursor.execute(
        f"""
        SELECT COALESCE(SUM(vr.valor_total), 0) AS total
        FROM venda_reembolsos vr
        WHERE vr.ativo = 'S'
          AND vr.status = 'CONCLUIDO'
          AND vr.data_hora >= %s AND vr.data_hora < %s
        """,
        (inicio, fim),
    )
    row = cast(Dict[str, Any], cursor.fetchone() or {})
    return Decimal(str(row.get("total") or 0))


def _buscar_reembolsos_por_periodo(cursor: Any, inicio, fim, group_expr: str) -> Dict[str, Decimal]:
    cursor.execute(
        f"""
        SELECT
            {group_expr} AS periodo,
            COALESCE(SUM(vr.valor_total), 0) AS reembolsos
        FROM venda_reembolsos vr
        INNER JOIN vendas v ON v.id = vr.venda_id
        WHERE vr.ativo = 'S'
          AND vr.status = 'CONCLUIDO'
          AND vr.data_hora >= %s AND vr.data_hora < %s
        GROUP BY periodo
        """,
        (inicio, fim),
    )
    return {r["periodo"]: Decimal(str(r.get("reembolsos") or 0)) for r in cursor.fetchall()}


def _buscar_reembolsos_por_cliente(cursor: Any, inicio, fim) -> Dict[str, Decimal]:
    cursor.execute(
        f"""
        SELECT
            COALESCE(c.nome, 'Consumidor Final') AS cliente,
            COALESCE(SUM(vr.valor_total), 0) AS reembolsos
        FROM venda_reembolsos vr
        INNER JOIN vendas v ON v.id = vr.venda_id
        LEFT JOIN clientes c ON c.id = v.cliente_id
        WHERE vr.ativo = 'S'
          AND vr.status = 'CONCLUIDO'
          AND vr.data_hora >= %s AND vr.data_hora < %s
        GROUP BY c.nome
        """,
        (inicio, fim),
    )
    return {r["cliente"]: Decimal(str(r.get("reembolsos") or 0)) for r in cursor.fetchall()}


class RelatorioModel:
    @staticmethod
    def visao_geral(
        *,
        data_inicial: date,
        data_final: date,
        agrupamento: str = "dia",
    ) -> Dict[str, Any]:
        inicio, fim = _periodo(data_inicial, data_final)
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                f"""
                SELECT
                    COUNT(DISTINCT v.id) AS total_vendas,
                    COALESCE(SUM(v.valor_total), 0) AS faturamento,
                    COUNT(DISTINCT v.cliente_id) AS total_clientes
                FROM vendas v
                WHERE v.data_hora >= %s AND v.data_hora < %s
                  AND v.status IN ('{STATUS_VENDA_SQL}')
                """,
                (inicio, fim),
            )
            resumo = cast(Dict[str, Any], cursor.fetchone() or {})

            reemb_total = _buscar_reembolsos_periodo(cursor, inicio, fim)
            resumo["faturamento"] = float(Decimal(str(resumo.get("faturamento") or 0)) - reemb_total)
            resumo["ticket_medio"] = (
                float(resumo.get("faturamento") or 0) / int(resumo.get("total_vendas") or 1)
            )

            group_expr = {
                "semana": "YEARWEEK(v.data_hora, 1)",
                "mes": "DATE_FORMAT(v.data_hora, '%%Y-%%m')",
            }.get(agrupamento, "DATE(v.data_hora)")

            cursor.execute(
                f"""
                SELECT
                    {group_expr} AS periodo,
                    COUNT(DISTINCT v.id) AS vendas,
                    COALESCE(SUM(v.valor_total), 0) AS faturamento,
                    COUNT(DISTINCT v.cliente_id) AS clientes
                FROM vendas v
                WHERE v.data_hora >= %s AND v.data_hora < %s
                  AND v.status IN ('{STATUS_VENDA_SQL}')
                GROUP BY periodo
                ORDER BY MIN(v.data_hora) ASC
                """,
                (inicio, fim),
            )
            resumo_periodo = list(cursor.fetchall())

            reemb_periodo = _buscar_reembolsos_por_periodo(cursor, inicio, fim, group_expr)

            for row in resumo_periodo:
                periodo = row.get("periodo")
                reemb = reemb_periodo.get(periodo, Decimal("0"))
                faturamento = Decimal(str(row.get("faturamento") or 0)) - reemb
                row["faturamento"] = float(faturamento)
                vendas = int(row.get("vendas") or 0)
                row["ticket_medio"] = float(faturamento) / vendas if vendas > 0 else 0

            cursor.execute(
                f"""
                SELECT
                    COALESCE(pr.nome, '-') AS produto,
                    SUM(iv.quantidade) - COALESCE(reemb.qtd_reembolso, 0) AS quantidade,
                    SUM(iv.quantidade * iv.preco_unitario) - COALESCE(reemb.receita_reembolso, 0) AS receita
                FROM itens_venda iv
                INNER JOIN vendas v ON v.id = iv.venda_id
                LEFT JOIN produtos pr ON pr.id = iv.produto_id
                LEFT JOIN (
                    SELECT
                        vri.produto_id,
                        SUM(vri.quantidade) AS qtd_reembolso,
                        SUM(vri.quantidade * vri.valor_unitario) AS receita_reembolso
                    FROM venda_reembolso_itens vri
                    INNER JOIN venda_reembolsos vr ON vr.id = vri.reembolso_id
                    WHERE vr.ativo = 'S' AND vr.status = 'CONCLUIDO'
                      AND vr.data_hora >= %s AND vr.data_hora < %s
                    GROUP BY vri.produto_id
                ) reemb ON reemb.produto_id = iv.produto_id
                WHERE v.data_hora >= %s AND v.data_hora < %s
                  AND v.status IN ('{STATUS_VENDA_SQL}')
                GROUP BY iv.produto_id, pr.nome
                HAVING quantidade > 0
                ORDER BY quantidade DESC
                LIMIT 10
                """,
                (inicio, fim, inicio, fim),
            )
            produtos = list(cursor.fetchall())

            cursor.execute(
                f"""
                SELECT
                    COALESCE(c.nome, 'Consumidor Final') AS cliente,
                    COUNT(DISTINCT v.id) AS compras,
                    SUM(v.valor_total) AS total_gasto
                FROM vendas v
                LEFT JOIN clientes c ON c.id = v.cliente_id
                WHERE v.data_hora >= %s AND v.data_hora < %s
                  AND v.status IN ('{STATUS_VENDA_SQL}')
                GROUP BY c.nome
                ORDER BY total_gasto DESC
                LIMIT 10
                """,
                (inicio, fim),
            )
            clientes = list(cursor.fetchall())

            reemb_cliente = _buscar_reembolsos_por_cliente(cursor, inicio, fim)
            for cli in clientes:
                nome = cli.get("cliente")
                cli["total_gasto"] = float(Decimal(str(cli.get("total_gasto") or 0)) - reemb_cliente.get(nome, Decimal("0")))

            return {
                "resumo": resumo,
                "resumo_periodo": resumo_periodo,
                "produtos": produtos,
                "clientes": clientes,
            }
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def produtos_mais_vendidos(
        *,
        data_inicial: date,
        data_final: date,
        agrupamento: str = "dia",
    ) -> Dict[str, Any]:
        inicio, fim = _periodo(data_inicial, data_final)
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                f"""
                SELECT
                    COUNT(DISTINCT v.id) AS total_vendas,
                    COALESCE(SUM(v.valor_total), 0) AS faturamento,
                    COUNT(DISTINCT iv.produto_id) AS total_produtos
                FROM vendas v
                INNER JOIN itens_venda iv ON iv.venda_id = v.id
                WHERE v.data_hora >= %s AND v.data_hora < %s
                  AND v.status IN ('{STATUS_VENDA_SQL}')
                """,
                (inicio, fim),
            )
            resumo = cast(Dict[str, Any], cursor.fetchone() or {})

            reemb_total = _buscar_reembolsos_periodo(cursor, inicio, fim)
            resumo["faturamento"] = float(Decimal(str(resumo.get("faturamento") or 0)) - reemb_total)

            group_expr = {
                "semana": "YEARWEEK(v.data_hora, 1)",
                "mes": "DATE_FORMAT(v.data_hora, '%%Y-%%m')",
            }.get(agrupamento, "DATE(v.data_hora)")

            cursor.execute(
                f"""
                SELECT
                    {group_expr} AS periodo,
                    COUNT(DISTINCT v.id) AS vendas,
                    COALESCE(SUM(v.valor_total), 0) AS faturamento
                FROM vendas v
                WHERE v.data_hora >= %s AND v.data_hora < %s
                  AND v.status IN ('{STATUS_VENDA_SQL}')
                GROUP BY periodo
                ORDER BY MIN(v.data_hora) ASC
                """,
                (inicio, fim),
            )
            resumo_periodo = list(cursor.fetchall())

            reemb_periodo = _buscar_reembolsos_por_periodo(cursor, inicio, fim, group_expr)

            for row in resumo_periodo:
                periodo = row.get("periodo")
                reemb = reemb_periodo.get(periodo, Decimal("0"))
                faturamento = Decimal(str(row.get("faturamento") or 0)) - reemb
                row["faturamento"] = float(faturamento)
                vendas = int(row.get("vendas") or 0)
                row["ticket_medio"] = float(faturamento) / vendas if vendas > 0 else 0

            cursor.execute(
                f"""
                SELECT
                    COALESCE(pr.nome, '-') AS produto,
                    SUM(iv.quantidade) - COALESCE(reemb.qtd_reembolso, 0) AS quantidade,
                    SUM(iv.quantidade * iv.preco_unitario) - COALESCE(reemb.receita_reembolso, 0) AS receita
                FROM itens_venda iv
                INNER JOIN vendas v ON v.id = iv.venda_id
                LEFT JOIN produtos pr ON pr.id = iv.produto_id
                LEFT JOIN (
                    SELECT
                        vri.produto_id,
                        SUM(vri.quantidade) AS qtd_reembolso,
                        SUM(vri.quantidade * vri.valor_unitario) AS receita_reembolso
                    FROM venda_reembolso_itens vri
                    INNER JOIN venda_reembolsos vr ON vr.id = vri.reembolso_id
                    WHERE vr.ativo = 'S' AND vr.status = 'CONCLUIDO'
                      AND vr.data_hora >= %s AND vr.data_hora < %s
                    GROUP BY vri.produto_id
                ) reemb ON reemb.produto_id = iv.produto_id
                WHERE v.data_hora >= %s AND v.data_hora < %s
                  AND v.status IN ('{STATUS_VENDA_SQL}')
                GROUP BY iv.produto_id, pr.nome
                HAVING quantidade > 0
                ORDER BY quantidade DESC
                LIMIT 10
                """,
                (inicio, fim, inicio, fim),
            )
            produtos = list(cursor.fetchall())

            return {
                "resumo": resumo,
                "resumo_periodo": resumo_periodo,
                "produtos": produtos,
            }
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def clientes_ticket_medio(
        *,
        data_inicial: date,
        data_final: date,
        agrupamento: str = "dia",
    ) -> Dict[str, Any]:
        inicio, fim = _periodo(data_inicial, data_final)
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                f"""
                SELECT
                    COUNT(DISTINCT v.id) AS total_vendas,
                    COALESCE(SUM(v.valor_total), 0) AS faturamento,
                    COUNT(DISTINCT v.cliente_id) AS total_clientes
                FROM vendas v
                WHERE v.data_hora >= %s AND v.data_hora < %s
                  AND v.status IN ('{STATUS_VENDA_SQL}')
                  AND v.cliente_id IS NOT NULL
                """,
                (inicio, fim),
            )
            resumo = cast(Dict[str, Any], cursor.fetchone() or {})

            reemb_total = _buscar_reembolsos_periodo(cursor, inicio, fim)
            resumo["faturamento"] = float(Decimal(str(resumo.get("faturamento") or 0)) - reemb_total)
            total_vendas = int(resumo.get("total_vendas") or 0)
            resumo["ticket_medio"] = float(resumo.get("faturamento") or 0) / total_vendas if total_vendas > 0 else 0

            group_expr = {
                "semana": "YEARWEEK(v.data_hora, 1)",
                "mes": "DATE_FORMAT(v.data_hora, '%%Y-%%m')",
            }.get(agrupamento, "DATE(v.data_hora)")

            cursor.execute(
                f"""
                SELECT
                    {group_expr} AS periodo,
                    COUNT(DISTINCT v.id) AS vendas,
                    COUNT(DISTINCT v.cliente_id) AS clientes,
                    COALESCE(SUM(v.valor_total), 0) AS faturamento
                FROM vendas v
                WHERE v.data_hora >= %s AND v.data_hora < %s
                  AND v.status IN ('{STATUS_VENDA_SQL}')
                GROUP BY periodo
                ORDER BY MIN(v.data_hora) ASC
                """,
                (inicio, fim),
            )
            resumo_periodo = list(cursor.fetchall())

            reemb_periodo = _buscar_reembolsos_por_periodo(cursor, inicio, fim, group_expr)

            for row in resumo_periodo:
                periodo = row.get("periodo")
                reemb = reemb_periodo.get(periodo, Decimal("0"))
                faturamento = Decimal(str(row.get("faturamento") or 0)) - reemb
                row["faturamento"] = float(faturamento)
                vendas = int(row.get("vendas") or 0)
                row["ticket_medio"] = float(faturamento) / vendas if vendas > 0 else 0

            cursor.execute(
                f"""
                SELECT
                    c.nome AS cliente,
                    COUNT(DISTINCT v.id) AS compras,
                    SUM(v.valor_total) AS total_gasto,
                    SUM(v.valor_total) / COUNT(DISTINCT v.id) AS ticket_medio
                FROM vendas v
                INNER JOIN clientes c ON c.id = v.cliente_id
                WHERE v.data_hora >= %s AND v.data_hora < %s
                  AND v.status IN ('{STATUS_VENDA_SQL}')
                GROUP BY c.id, c.nome
                ORDER BY total_gasto DESC
                LIMIT 15
                """,
                (inicio, fim),
            )
            clientes = list(cursor.fetchall())

            reemb_cliente = _buscar_reembolsos_por_cliente(cursor, inicio, fim)
            for cli in clientes:
                nome = cli.get("cliente")
                total = Decimal(str(cli.get("total_gasto") or 0)) - reemb_cliente.get(nome, Decimal("0"))
                cli["total_gasto"] = float(total)
                compras = int(cli.get("compras") or 0)
                cli["ticket_medio"] = float(total) / compras if compras > 0 else 0

            return {
                "resumo": resumo,
                "resumo_periodo": resumo_periodo,
                "clientes": clientes,
            }
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def caixa_por_periodo(
        *,
        data_inicial: date,
        data_final: date,
        agrupamento: str = "dia",
    ) -> Dict[str, Any]:
        inicio, fim = _periodo(data_inicial, data_final)
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                f"""
                SELECT
                    COUNT(DISTINCT v.id) AS total_vendas,
                    COALESCE(SUM(v.valor_total), 0) AS faturamento,
                    COUNT(DISTINCT v.cliente_id) AS total_clientes
                FROM vendas v
                WHERE v.data_hora >= %s AND v.data_hora < %s
                  AND v.status IN ('{STATUS_VENDA_SQL}')
                """,
                (inicio, fim),
            )
            resumo = cast(Dict[str, Any], cursor.fetchone() or {})

            reemb_total = _buscar_reembolsos_periodo(cursor, inicio, fim)
            faturamento_liquido = float(Decimal(str(resumo.get("faturamento") or 0)) - reemb_total)
            resumo["faturamento"] = faturamento_liquido
            resumo["entradas"] = faturamento_liquido
            total_vendas = int(resumo.get("total_vendas") or 0)
            resumo["ticket_medio"] = faturamento_liquido / total_vendas if total_vendas > 0 else 0

            group_expr = {
                "semana": "YEARWEEK(v.data_hora, 1)",
                "mes": "DATE_FORMAT(v.data_hora, '%%Y-%%m')",
            }.get(agrupamento, "DATE(v.data_hora)")

            cursor.execute(
                f"""
                SELECT
                    {group_expr} AS periodo,
                    COUNT(DISTINCT v.id) AS vendas,
                    COALESCE(SUM(v.valor_total), 0) AS faturamento
                FROM vendas v
                WHERE v.data_hora >= %s AND v.data_hora < %s
                  AND v.status IN ('{STATUS_VENDA_SQL}')
                GROUP BY periodo
                ORDER BY MIN(v.data_hora) ASC
                """,
                (inicio, fim),
            )
            resumo_periodo = list(cursor.fetchall())

            reemb_periodo = _buscar_reembolsos_por_periodo(cursor, inicio, fim, group_expr)

            for row in resumo_periodo:
                periodo = row.get("periodo")
                reemb = reemb_periodo.get(periodo, Decimal("0"))
                faturamento = Decimal(str(row.get("faturamento") or 0)) - reemb
                row["faturamento"] = float(faturamento)
                vendas = int(row.get("vendas") or 0)
                row["ticket_medio"] = float(faturamento) / vendas if vendas > 0 else 0

            cursor.execute(
                f"""
                SELECT
                    COALESCE(pr.nome, '-') AS produto,
                    SUM(iv.quantidade) - COALESCE(reemb.qtd_reembolso, 0) AS quantidade,
                    SUM(iv.quantidade * iv.preco_unitario) - COALESCE(reemb.receita_reembolso, 0) AS receita
                FROM itens_venda iv
                INNER JOIN vendas v ON v.id = iv.venda_id
                LEFT JOIN produtos pr ON pr.id = iv.produto_id
                LEFT JOIN (
                    SELECT
                        vri.produto_id,
                        SUM(vri.quantidade) AS qtd_reembolso,
                        SUM(vri.quantidade * vri.valor_unitario) AS receita_reembolso
                    FROM venda_reembolso_itens vri
                    INNER JOIN venda_reembolsos vr ON vr.id = vri.reembolso_id
                    WHERE vr.ativo = 'S' AND vr.status = 'CONCLUIDO'
                      AND vr.data_hora >= %s AND vr.data_hora < %s
                    GROUP BY vri.produto_id
                ) reemb ON reemb.produto_id = iv.produto_id
                WHERE v.data_hora >= %s AND v.data_hora < %s
                  AND v.status IN ('{STATUS_VENDA_SQL}')
                GROUP BY iv.produto_id, pr.nome
                HAVING quantidade > 0
                ORDER BY quantidade DESC
                LIMIT 10
                """,
                (inicio, fim, inicio, fim),
            )
            produtos = list(cursor.fetchall())

            cursor.execute(
                f"""
                SELECT
                    COALESCE(c.nome, 'Consumidor Final') AS cliente,
                    COUNT(DISTINCT v.id) AS compras,
                    SUM(v.valor_total) AS total_gasto
                FROM vendas v
                LEFT JOIN clientes c ON c.id = v.cliente_id
                WHERE v.data_hora >= %s AND v.data_hora < %s
                  AND v.status IN ('{STATUS_VENDA_SQL}')
                GROUP BY c.nome
                ORDER BY total_gasto DESC
                LIMIT 10
                """,
                (inicio, fim),
            )
            clientes = list(cursor.fetchall())

            reemb_cliente = _buscar_reembolsos_por_cliente(cursor, inicio, fim)
            for cli in clientes:
                nome = cli.get("cliente")
                cli["total_gasto"] = float(Decimal(str(cli.get("total_gasto") or 0)) - reemb_cliente.get(nome, Decimal("0")))

            return {
                "resumo": resumo,
                "resumo_periodo": resumo_periodo,
                "produtos": produtos,
                "clientes": clientes,
            }
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def matriz_vendas_anual(ano: int) -> Dict[str, Any]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    COALESCE(SUM(quantidade_estoque * preco_venda), 0) AS estoque_bruto,
                    COALESCE(SUM(quantidade_estoque * COALESCE(preco_compra, 0)), 0) AS estoque_liquido
                FROM produtos
                WHERE ativo = 'S'
                """
            )
            est = cursor.fetchone() or {}
            estoque_bruto = float(est.get("estoque_bruto") or 0.0)
            estoque_liquido = float(est.get("estoque_liquido") or 0.0)

            cursor.execute("SELECT DISTINCT YEAR(data_hora) AS ano FROM vendas ORDER BY ano DESC")
            anos_rows = cursor.fetchall()
            anos_disponiveis = [r["ano"] for r in anos_rows if r.get("ano")]
            ano_atual = date.today().year
            if ano_atual not in anos_disponiveis:
                anos_disponiveis.append(ano_atual)
            anos_disponiveis = sorted(list(set(anos_disponiveis)), reverse=True)

            cursor.execute(
                f"""
                SELECT
                    MONTH(data_hora) AS mes,
                    DAY(data_hora) AS dia,
                    COALESCE(SUM(valor_total), 0) AS total_dia
                FROM vendas
                WHERE YEAR(data_hora) = %s
                  AND status IN ('{STATUS_VENDA_SQL}')
                GROUP BY MONTH(data_hora), DAY(data_hora)
                ORDER BY mes, dia
                """,
                (ano,),
            )
            vendas_rows = cursor.fetchall()

            cursor.execute(
                """
                SELECT
                    MONTH(vr.data_hora) AS mes,
                    DAY(vr.data_hora) AS dia,
                    COALESCE(SUM(vr.valor_total), 0) AS total_reembolso
                FROM venda_reembolsos vr
                INNER JOIN vendas v ON v.id = vr.venda_id
                WHERE YEAR(vr.data_hora) = %s
                  AND vr.ativo = 'S'
                  AND vr.status = 'CONCLUIDO'
                GROUP BY MONTH(vr.data_hora), DAY(vr.data_hora)
                ORDER BY mes, dia
                """,
                (ano,),
            )
            reemb_rows = cursor.fetchall()
            reemb_map: Dict[tuple, float] = {}
            for r in reemb_rows:
                m = int(r["mes"])
                d = int(r["dia"])
                reemb_map[(m, d)] = float(r.get("total_reembolso") or 0.0)

            matriz: Dict[tuple[int, int], float] = {}
            totais_mensais: Dict[int, float] = {m: 0.0 for m in range(1, 13)}
            total_ano_bruto = 0.0

            for r in vendas_rows:
                m = int(r["mes"])
                d = int(r["dia"])
                val = float(r["total_dia"] or 0.0) - reemb_map.get((m, d), 0.0)
                matriz[(m, d)] = val
                totais_mensais[m] += val
                total_ano_bruto += val

            return {
                "estoque_bruto": estoque_bruto,
                "estoque_liquido": estoque_liquido,
                "matriz_vendas": matriz,
                "totais_mensais": totais_mensais,
                "total_ano_bruto": total_ano_bruto,
                "total_ano_liquido": total_ano_bruto,
                "anos_disponiveis": anos_disponiveis,
                "ano_selecionado": ano,
            }
        finally:
            cursor.close()
            conn.close()
