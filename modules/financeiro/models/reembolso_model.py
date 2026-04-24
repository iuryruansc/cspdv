from __future__ import annotations

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, List, Sequence

from database.connection import get_connection


CENT = Decimal("0.01")


class ReembolsoModel:
    @staticmethod
    def registrar_reembolso(
        *,
        venda_id: int,
        tipo: str,
        motivo: str,
        observacao: str,
        usuario_id: int,
        itens: Sequence[Dict[str, Any]],
        pagamentos: Sequence[Dict[str, Any]],
    ) -> int:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            total_reembolso = sum(
                (Decimal(str(item.get("valor_total") or 0)).quantize(CENT, rounding=ROUND_HALF_UP) for item in itens),
                Decimal("0.00"),
            )

            cursor.execute(
                """
                INSERT INTO venda_reembolsos
                    (venda_id, tipo, status, valor_total, motivo, observacao, usuario_id, data_hora, ativo, createdAt, updatedAt)
                VALUES
                    (%s, %s, 'CONCLUIDO', %s, %s, %s, %s, NOW(), 'S', NOW(), NOW())
                """,
                (
                    int(venda_id),
                    str(tipo),
                    float(total_reembolso),
                    str(motivo),
                    str(observacao or ""),
                    int(usuario_id),
                ),
            )
            reembolso_id = int(cursor.lastrowid or 0)
            if reembolso_id <= 0:
                raise RuntimeError("Não foi possível obter o ID do reembolso.")

            data_hora = datetime.now()
            total_produtos: Dict[int, int] = {}

            for item in itens:
                item_venda_id = int(item["item_venda_id"])
                produto_id = int(item["produto_id"])
                lote_id = int(item["lote_id"])
                quantidade = int(item["quantidade"])
                valor_unitario = Decimal(str(item["valor_unitario"])).quantize(CENT, rounding=ROUND_HALF_UP)
                valor_total = (valor_unitario * Decimal(quantidade)).quantize(CENT, rounding=ROUND_HALF_UP)

                cursor.execute(
                    """
                    INSERT INTO venda_reembolso_itens
                        (reembolso_id, item_venda_id, produto_id, lote_id, quantidade, valor_unitario, valor_total, createdAt, updatedAt)
                    VALUES
                        (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                    """,
                    (
                        reembolso_id,
                        item_venda_id,
                        produto_id,
                        lote_id,
                        quantidade,
                        float(valor_unitario),
                        float(valor_total),
                    ),
                )

                cursor.execute(
                    """
                    UPDATE lotes
                    SET quantidade = COALESCE(quantidade, 0) + %s,
                        updatedAt = NOW()
                    WHERE id = %s
                    """,
                    (quantidade, lote_id),
                )

                total_produtos[produto_id] = total_produtos.get(produto_id, 0) + quantidade

                cursor.execute(
                    """
                    INSERT INTO movimentacao_estoque
                        (lote_id, venda_id, data_hora, tipo, quantidade, usuario_id, observacao, tipo_movimento_id, ativo, createdAt, updatedAt)
                    VALUES
                        (%s, %s, %s, %s, %s, %s, %s, NULL, 'S', NOW(), NOW())
                    """,
                    (
                        lote_id,
                        venda_id,
                        data_hora,
                        "entrada_reembolso",
                        quantidade,
                        usuario_id,
                        f"Entrada por reembolso #{reembolso_id}",
                    ),
                )

            for produto_id, quantidade in total_produtos.items():
                cursor.execute(
                    """
                    UPDATE produtos
                    SET quantidade_estoque = COALESCE(quantidade_estoque, 0) + %s,
                        updatedAt = NOW()
                    WHERE id = %s
                    """,
                    (quantidade, produto_id),
                )

            for pagamento in pagamentos:
                valor = Decimal(str(pagamento.get("valor") or 0)).quantize(CENT, rounding=ROUND_HALF_UP)
                if valor <= Decimal("0.00"):
                    continue
                cursor.execute(
                    """
                    INSERT INTO venda_reembolso_pagamentos
                        (reembolso_id, forma_pagamento, valor, observacao, createdAt, updatedAt)
                    VALUES
                        (%s, %s, %s, %s, NOW(), NOW())
                    """,
                    (
                        reembolso_id,
                        str(pagamento.get("forma_pagamento") or "Forma"),
                        float(valor),
                        str(pagamento.get("observacao") or ""),
                    ),
                )

            conn.commit()
            return reembolso_id
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

