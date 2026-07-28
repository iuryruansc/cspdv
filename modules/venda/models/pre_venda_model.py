from __future__ import annotations

import json
from datetime import datetime
from typing import Any, cast

from database.connection import db_cursor, db_transaction
from modules.shared.constants import FLAG_SIM

class PreVendaModel:

    @staticmethod
    def salvar_pre_venda(
        *,
        usuario_id: int,
        caixa_id: int,
        cliente_id: int | None,
        itens: list[dict[str, Any]],
        desconto_global: float = 0.0,
        desconto_itens: float = 0.0,
        desconto_total: float = 0.0,
        valor_total: float,
        data_hora: datetime | None = None,
        observacao: str | None = None,
    ) -> int:
        with db_transaction(dictionary=False) as cur:
            data_registro = data_hora or datetime.now()
            itens_json = json.dumps(itens, ensure_ascii=False, default=str)

            cur.execute(
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
            pre_venda_id = int(cur.lastrowid or 0)

            cur.execute(
                "UPDATE pre_vendas SET numero_venda = %s WHERE id = %s",
                (pre_venda_id, pre_venda_id),
            )

            return pre_venda_id
    @staticmethod
    def listar_pre_vendas_pendentes(
        *,
        usuario_id: int | None = None,
        caixa_id: int | None = None,
    ) -> list[dict[str, Any]]:
        with db_cursor() as cur:
            filtros = ["pv.status = 'PENDENTE'"]
            params: list[Any] = []

            if usuario_id is not None:
                filtros.append("pv.usuario_id = %s")
                params.append(usuario_id)
            if caixa_id is not None:
                filtros.append("pv.caixa_id = %s")
                params.append(caixa_id)

            where = " AND ".join(filtros) if filtros else "1=1"

            cur.execute(
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
            return cast(list[dict[str, Any]], cur.fetchall())
    @staticmethod
    def carregar_pre_venda(pre_venda_id: int) -> dict[str, Any] | None:
        with db_cursor() as cur:
            cur.execute(
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
            resultado = cast(dict[str, Any] | None, cur.fetchone())
            if resultado is not None:
                itens_json = resultado.get("itens_json")
                if isinstance(itens_json, str):
                    resultado["itens"] = json.loads(itens_json)
            return resultado
    @staticmethod
    def marcar_importada(pre_venda_id: int, nova_venda_id: int) -> None:
        with db_transaction(dictionary=False) as cur:
            cur.execute(
                """
                UPDATE pre_vendas
                SET status = 'IMPORTADA',
                    observacao = CONCAT(COALESCE(observacao, ''), ' | Importada como venda #', %s),
                    updatedAt = NOW()
                WHERE id = %s
                """,
                (nova_venda_id, pre_venda_id),
            )
    @staticmethod
    def cancelar_pre_venda(pre_venda_id: int) -> None:
        with db_transaction(dictionary=False) as cur:
            cur.execute(
                """
                UPDATE pre_vendas
                SET status = 'CANCELADA',
                    updatedAt = NOW()
                WHERE id = %s
                """,
                (pre_venda_id,),
            )
