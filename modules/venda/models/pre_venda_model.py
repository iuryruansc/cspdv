from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List, Optional, cast

from database.connection import get_connection
from modules.shared.constants import FLAG_SIM


class PreVendaModel:

    @staticmethod
    def salvar_pre_venda(
        *,
        usuario_id: int,
        caixa_id: int,
        cliente_id: Optional[int],
        itens: List[Dict[str, Any]],
        desconto_global: float = 0.0,
        desconto_itens: float = 0.0,
        desconto_total: float = 0.0,
        valor_total: float,
        data_hora: Optional[datetime] = None,
        observacao: Optional[str] = None,
    ) -> int:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            data_registro = data_hora or datetime.now()
            itens_json = json.dumps(itens, ensure_ascii=False, default=str)

            cursor.execute(
                """
                INSERT INTO pre_vendas
                    (cliente_id, usuario_id, caixa_id, data_hora, valor_total,
                     itens_json, desconto_global, desconto_itens, desconto_total,
                     observacao, createdAt, updatedAt)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                """,
                (
                    cliente_id,
                    usuario_id,
                    caixa_id,
                    data_registro,
                    valor_total,
                    itens_json,
                    desconto_global,
                    desconto_itens,
                    desconto_total,
                    observacao,
                ),
            )
            pre_venda_id = int(cursor.lastrowid or 0)

            cursor.execute(
                "UPDATE pre_vendas SET numero_venda = %s WHERE id = %s",
                (pre_venda_id, pre_venda_id),
            )

            conn.commit()
            return pre_venda_id
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def listar_pre_vendas_pendentes(
        *,
        usuario_id: Optional[int] = None,
        caixa_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            filtros = ["pv.status = 'PENDENTE'"]
            params: List[Any] = []

            if usuario_id is not None:
                filtros.append("pv.usuario_id = %s")
                params.append(usuario_id)
            if caixa_id is not None:
                filtros.append("pv.caixa_id = %s")
                params.append(caixa_id)

            where = " AND ".join(filtros) if filtros else "1=1"

            cursor.execute(
                f"""
                SELECT
                    pv.id,
                    pv.numero_venda,
                    pv.data_hora,
                    pv.valor_total,
                    pv.status,
                    pv.observacao,
                    pv.usuario_id,
                    u.nome AS usuario_nome,
                    pv.cliente_id,
                    c.nome AS cliente_nome
                FROM pre_vendas pv
                LEFT JOIN usuarios u ON u.id = pv.usuario_id
                LEFT JOIN clientes c ON c.id = pv.cliente_id
                WHERE {where}
                ORDER BY pv.data_hora DESC
                """,
                tuple(params),
            )
            return cast(List[Dict[str, Any]], cursor.fetchall())
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def carregar_pre_venda(pre_venda_id: int) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    pv.*,
                    u.nome AS usuario_nome,
                    c.nome AS cliente_nome
                FROM pre_vendas pv
                LEFT JOIN usuarios u ON u.id = pv.usuario_id
                LEFT JOIN clientes c ON c.id = pv.cliente_id
                WHERE pv.id = %s
                """,
                (pre_venda_id,),
            )
            resultado = cast(Optional[Dict[str, Any]], cursor.fetchone())
            if resultado is not None:
                itens_json = resultado.get("itens_json")
                if isinstance(itens_json, str):
                    resultado["itens"] = json.loads(itens_json)
            return resultado
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def marcar_importada(pre_venda_id: int, nova_venda_id: int) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                UPDATE pre_vendas
                SET status = 'IMPORTADA',
                    observacao = CONCAT(COALESCE(observacao, ''), ' | Importada como venda #', %s),
                    updatedAt = NOW()
                WHERE id = %s
                """,
                (nova_venda_id, pre_venda_id),
            )
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def cancelar_pre_venda(pre_venda_id: int) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                UPDATE pre_vendas
                SET status = 'CANCELADA',
                    updatedAt = NOW()
                WHERE id = %s
                """,
                (pre_venda_id,),
            )
            conn.commit()
        finally:
            cursor.close()
            conn.close()
