from __future__ import annotations

from typing import Any, Dict, List, Optional, cast

from database.connection import get_connection


class EstoqueModel:
    ESTOQUE_CRITICO_PADRAO = 5

    @staticmethod
    def listar_categorias() -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT id, nome
                FROM categorias
                WHERE ativo = 'S'
                ORDER BY nome
                """
            )
            return cast(List[Dict[str, Any]], cursor.fetchall())
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def listar_fornecedores() -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT id_fornecedor, nome_fantasia
                FROM fornecedores
                WHERE ativo = 'S'
                ORDER BY nome_fantasia
                """
            )
            return cast(List[Dict[str, Any]], cursor.fetchall())
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def obter_metricas() -> Dict[str, int]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT COUNT(*) AS total
                FROM produtos
                WHERE ativo = 'S'
                """
            )
            produtos = cursor.fetchone() or {}

            cursor.execute(
                """
                SELECT COUNT(*) AS total
                FROM lotes
                WHERE ativo = 'S'
                  AND quantidade > 0
                """
            )
            lotes = cursor.fetchone() or {}

            cursor.execute(
                """
                SELECT COUNT(*) AS total
                FROM produtos
                WHERE ativo = 'S'
                  AND quantidade_estoque <= %s
                """,
                (EstoqueModel.ESTOQUE_CRITICO_PADRAO,),
            )
            critico = cursor.fetchone() or {}

            cursor.execute(
                """
                SELECT COUNT(*) AS total
                FROM movimentacao_estoque
                WHERE ativo = 'S'
                  AND DATE(data_hora) = CURDATE()
                """
            )
            movimentacoes = cursor.fetchone() or {}

            return {
                "produtos_ativos": int(produtos.get("total") or 0),
                "lotes_ativos": int(lotes.get("total") or 0),
                "estoque_critico": int(critico.get("total") or 0),
                "movimentacoes_dia": int(movimentacoes.get("total") or 0),
            }
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def listar_produtos_lotes(
        *,
        busca: str = "",
        categoria_id: Optional[int] = None,
        fornecedor_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            where: List[str] = ["p.ativo = 'S'"]
            params: List[Any] = []

            busca_limpa = str(busca or "").strip()
            if busca_limpa:
                termo = f"%{busca_limpa}%"
                where.append(
                    """
                    (
                        p.nome LIKE %s
                        OR p.codigo_barras LIKE %s
                        OR COALESCE(l.numero_lote, '') LIKE %s
                        OR COALESCE(m.nome_marca, '') LIKE %s
                    )
                    """
                )
                params.extend([termo, termo, termo, termo])

            if categoria_id:
                where.append("p.categoria_id = %s")
                params.append(int(categoria_id))

            if fornecedor_id:
                where.append("p.fornecedor_id = %s")
                params.append(int(fornecedor_id))

            cursor.execute(
                f"""
                SELECT
                    p.id,
                    p.codigo_barras,
                    p.nome,
                    COALESCE(c.nome, '-') AS categoria,
                    COALESCE(m.nome_marca, '-') AS marca,
                    COALESCE(l.numero_lote, '-') AS lote,
                    l.data_validade,
                    COALESCE(l.quantidade, p.quantidade_estoque, 0) AS quantidade,
                    COALESCE(l.preco_venda, p.preco_venda, 0) AS preco_venda
                FROM produtos p
                LEFT JOIN categorias c ON c.id = p.categoria_id
                LEFT JOIN marcas m ON m.id = p.marca_id
                LEFT JOIN lotes l
                    ON l.produto_id = p.id
                   AND l.ativo = 'S'
                WHERE {' AND '.join(where)}
                ORDER BY p.nome, l.data_validade, l.numero_lote
                """,
                tuple(params),
            )
            return cast(List[Dict[str, Any]], cursor.fetchall())
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def listar_movimentacoes_recentes(limite: int = 20) -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    me.data_hora,
                    COALESCE(p.nome, '-') AS produto,
                    me.tipo,
                    me.quantidade,
                    COALESCE(u.nome, '-') AS usuario
                FROM movimentacao_estoque me
                LEFT JOIN lotes l ON l.id = me.lote_id
                LEFT JOIN produtos p ON p.id = l.produto_id
                LEFT JOIN usuarios u ON u.id = me.usuario_id
                WHERE me.ativo = 'S'
                ORDER BY me.data_hora DESC, me.id DESC
                LIMIT %s
                """,
                (int(limite),),
            )
            return cast(List[Dict[str, Any]], cursor.fetchall())
        finally:
            cursor.close()
            conn.close()
