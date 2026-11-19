from __future__ import annotations

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Sequence, cast

from database.connection import db_cursor, db_transaction
from modules.shared.constants import (
    FLAG_SIM,
    STATUS_CONTA_CANCELADA,
    STATUS_REEMBOLSO_CONCLUIDO,
    STATUS_VENDA_PARCIALMENTE_REEMBOLSADA,
    STATUS_VENDA_REEMBOLSADA,
    TIPO_MOVIMENTACAO_ENTRADA_REEMBOLSO,
    TIPO_MOVIMENTACAO_ENTRADA_REEMBOLSO_KIT,
)

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
        itens: Sequence[dict[str, Any]],
        pagamentos: Sequence[dict[str, Any]],
    ) -> int:
        with db_transaction() as cur:
            total_reembolso = sum(
                (Decimal(str(item.get("valor_total") or 0)).quantize(CENT, rounding=ROUND_HALF_UP) for item in itens),
                Decimal("0.00"),
            )

            cur.execute(
                """
                INSERT INTO venda_reembolsos
                    (venda_id, tipo, status, valor_total, motivo, observacao, usuario_id, data_hora, ativo, createdAt, updatedAt)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s, NOW(), %s, NOW(), NOW())
                """,
                (
                    int(venda_id),
                    str(tipo),
                    STATUS_REEMBOLSO_CONCLUIDO,
                    float(total_reembolso),
                    str(motivo),
                    str(observacao or ""),
                    int(usuario_id),
                    FLAG_SIM,
                ),
            )
            reembolso_id = int(cur.lastrowid or 0)
            if reembolso_id <= 0:
                raise RuntimeError("Não foi possível obter o ID do reembolso.")

            data_hora = datetime.now()
            total_produtos: dict[int, int] = {}

            for item in itens:
                item_venda_id = int(item["item_venda_id"])
                produto_id = int(item.get("produto_id") or 0) or None
                kit_id = int(item.get("kit_id") or 0)
                lote_id = int(item.get("lote_id") or 0) or None
                quantidade = int(item["quantidade"])
                valor_unitario = Decimal(str(item["valor_unitario"])).quantize(CENT, rounding=ROUND_HALF_UP)
                valor_total = (valor_unitario * Decimal(quantidade)).quantize(CENT, rounding=ROUND_HALF_UP)

                cur.execute(
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

                if produto_id:
                    cur.execute(
                        """
                        UPDATE lotes
                        SET quantidade = COALESCE(quantidade, 0) + %s,
                            updatedAt = NOW()
                        WHERE id = %s
                        """,
                        (quantidade, lote_id),
                    )
                    total_produtos[produto_id] = total_produtos.get(produto_id, 0) + quantidade

                    cur.execute(
                        """
                        INSERT INTO movimentacao_estoque
                            (lote_id, venda_id, data_hora, tipo, quantidade, usuario_id, observacao, tipo_movimento_id, ativo, createdAt, updatedAt)
                        VALUES
                            (%s, %s, %s, %s, %s, %s, %s, NULL, %s, NOW(), NOW())
                        """,
                        (
                            lote_id,
                            venda_id,
                            data_hora,
                            TIPO_MOVIMENTACAO_ENTRADA_REEMBOLSO,
                            quantidade,
                            usuario_id,
                            f"Entrada por reembolso #{reembolso_id}",
                            FLAG_SIM,
                        ),
                    )

                if kit_id:
                    cur.execute(
                        """
                        UPDATE kits
                        SET quantidade_estoque = COALESCE(quantidade_estoque, 0) + %s,
                            updatedAt = NOW()
                        WHERE id = %s
                        """,
                        (quantidade, kit_id),
                    )
                    ReembolsoModel._restaurar_componentes_kit(
                        cursor=cur,
                        kit_id=kit_id,
                        quantidade_kit=quantidade,
                        venda_id=venda_id,
                        reembolso_id=reembolso_id,
                        data_hora=data_hora,
                        usuario_id=usuario_id,
                    )

            for produto_id, quantidade in total_produtos.items():
                cur.execute(
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
                cur.execute(
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

            ReembolsoModel._atualizar_status_venda(cur, int(venda_id))
            return reembolso_id

    @staticmethod
    def _restaurar_componentes_kit(
        *,
        cursor: Any,
        kit_id: int,
        quantidade_kit: int,
        venda_id: int,
        reembolso_id: int,
        data_hora: datetime,
        usuario_id: int,
    ) -> None:
        cursor.execute(
            """
            SELECT produto_id, SUM(quantidade) AS quantidade_por_kit
            FROM kit_itens
            WHERE kit_id = %s
            GROUP BY produto_id
            """,
            (int(kit_id),),
        )
        componentes = list(cursor.fetchall())

        for componente in componentes:
            produto_id = int(componente["produto_id"])
            quantidade = int(componente["quantidade_por_kit"] or 0) * int(quantidade_kit)
            if quantidade <= 0:
                continue

            cursor.execute(
                """
                SELECT id, preco_compra, preco_venda
                FROM produtos
                WHERE id = %s
                LIMIT 1
                """,
                (produto_id,),
            )
            produto = cursor.fetchone()
            if not produto:
                raise ValueError(f"Componente {produto_id} do kit não foi encontrado.")

            cursor.execute(
                """
                SELECT id
                FROM lotes
                WHERE produto_id = %s AND ativo = %s
                ORDER BY data_validade, id
                LIMIT 1
                """,
                (produto_id, FLAG_SIM),
            )
            lote = cursor.fetchone()
            if lote:
                lote_id = int(lote["id"])
            else:
                cursor.execute(
                    """
                    INSERT INTO lotes
                        (produto_id, preco_compra, preco_venda, numero_lote, quantidade,
                         data_validade, localizacao, createdAt, updatedAt, ativo)
                    VALUES
                        (%s, %s, %s, %s, 0, %s, %s, NOW(), NOW(), %s)
                    """,
                    (
                        produto_id,
                        float(produto.get("preco_compra") or 0),
                        float(produto.get("preco_venda") or 0),
                        f"AUTO-{produto_id:06d}",
                        "2099-12-31",
                        "AUTO",
                        FLAG_SIM,
                    ),
                )
                lote_id = int(cursor.lastrowid or 0)

            cursor.execute(
                """
                UPDATE lotes
                SET quantidade = COALESCE(quantidade, 0) + %s,
                    updatedAt = NOW()
                WHERE id = %s
                """,
                (quantidade, lote_id),
            )
            cursor.execute(
                """
                UPDATE produtos
                SET quantidade_estoque = COALESCE(quantidade_estoque, 0) + %s,
                    updatedAt = NOW()
                WHERE id = %s
                """,
                (quantidade, produto_id),
            )
            cursor.execute(
                """
                INSERT INTO movimentacao_estoque
                    (lote_id, venda_id, data_hora, tipo, quantidade, usuario_id, observacao,
                     tipo_movimento_id, ativo, createdAt, updatedAt)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s, NULL, %s, NOW(), NOW())
                """,
                (
                    lote_id,
                    venda_id,
                    data_hora,
                    TIPO_MOVIMENTACAO_ENTRADA_REEMBOLSO_KIT,
                    quantidade,
                    usuario_id,
                    f"Entrada do componente do kit #{kit_id} por reembolso #{reembolso_id}",
                    FLAG_SIM,
                ),
            )
    @staticmethod
    def _atualizar_status_venda(cursor: Any, venda_id: int) -> None:
        cursor.execute(
            """
            SELECT COALESCE(valor_total, 0) AS valor_total
            FROM vendas
            WHERE id = %s
            LIMIT 1
            """,
            (int(venda_id),),
        )
        venda = cast(dict[str, Any], cursor.fetchone() or {})
        valor_total_venda = Decimal(str(venda.get("valor_total") or 0)).quantize(CENT, rounding=ROUND_HALF_UP)

        cursor.execute(
            """
            SELECT COALESCE(SUM(valor_total), 0) AS total_reembolsado
            FROM venda_reembolsos
            WHERE venda_id = %s
              AND ativo = %s
              AND status = %s
            """,
            (int(venda_id), FLAG_SIM, STATUS_REEMBOLSO_CONCLUIDO),
        )
        totais = cast(dict[str, Any], cursor.fetchone() or {})
        total_reembolsado = Decimal(str(totais.get("total_reembolsado") or 0)).quantize(CENT, rounding=ROUND_HALF_UP)

        novo_status = (
            STATUS_VENDA_REEMBOLSADA
            if total_reembolsado >= valor_total_venda
            else STATUS_VENDA_PARCIALMENTE_REEMBOLSADA
        )
        cursor.execute(
            """
            UPDATE vendas
            SET status = %s
            WHERE id = %s
            """,
            (novo_status, int(venda_id)),
        )

        if novo_status == STATUS_VENDA_REEMBOLSADA:
            cursor.execute(
                """
                UPDATE contas_receber
                SET status = %s,
                    valor_aberto = 0,
                    valor_recebido = valor_total,
                    updatedAt = NOW()
                WHERE venda_id = %s
                  AND ativo = %s
                  AND status IN ('PENDENTE', 'PARCIALMENTE_RECEBIDA')
                """,
                (STATUS_CONTA_CANCELADA, int(venda_id), FLAG_SIM),
            )
        elif novo_status == STATUS_VENDA_PARCIALMENTE_REEMBOLSADA:
            cursor.execute(
                """
                UPDATE contas_receber
                SET valor_aberto = GREATEST(valor_total - %s, 0),
                    status = CASE
                        WHEN GREATEST(valor_total - %s, 0) <= 0 THEN %s
                        ELSE status
                    END,
                    updatedAt = NOW()
                WHERE venda_id = %s
                  AND ativo = %s
                  AND status IN ('PENDENTE', 'PARCIALMENTE_RECEBIDA')
                """,
                (
                    float(total_reembolsado),
                    float(total_reembolsado),
                    STATUS_CONTA_CANCELADA,
                    int(venda_id),
                    FLAG_SIM,
                ),
            )
