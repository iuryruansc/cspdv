from __future__ import annotations

from datetime import date
from typing import Any, Mapping


class EstoqueLoteModel:
    """Operações compartilhadas de sincronização e baixa por lote."""

    @staticmethod
    def _campo(registro: Any, indice: int, nome: str, padrao: Any = None) -> Any:
        if isinstance(registro, Mapping):
            return registro.get(nome, padrao)
        try:
            return registro[indice]
        except (IndexError, KeyError, TypeError):
            return padrao

    @staticmethod
    def _obter_lotes(cursor: Any, produto_id: int, *, bloquear: bool = False) -> list[Any]:
        query = """
            SELECT id, quantidade
            FROM lotes
            WHERE produto_id = %s AND ativo = 'S'
            ORDER BY
                CASE WHEN numero_lote LIKE 'AUTO-%%' THEN 0 ELSE 1 END,
                data_validade DESC,
                id DESC
        """
        if bloquear:
            query += " FOR UPDATE"
        cursor.execute(query, (int(produto_id),))
        return list(cursor.fetchall())

    @staticmethod
    def _criar_lote_automatico(cursor: Any, produto_id: int, quantidade: int) -> int:
        cursor.execute(
            """
            SELECT preco_compra, preco_venda
            FROM produtos
            WHERE id = %s
            """,
            (int(produto_id),),
        )
        precos = cursor.fetchone() or (0, 0)
        cursor.execute(
            """
            INSERT INTO lotes
                (produto_id, preco_compra, preco_venda, numero_lote, quantidade,
                 data_validade, localizacao, createdAt, updatedAt, ativo)
            VALUES
                (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW(), 'S')
            """,
            (
                int(produto_id),
                float(EstoqueLoteModel._campo(precos, 0, "preco_compra", 0) or 0),
                float(EstoqueLoteModel._campo(precos, 1, "preco_venda", 0) or 0),
                f"AUTO-{int(produto_id):06d}",
                int(quantidade),
                date(2099, 12, 31),
                "AUTO",
            ),
        )
        return int(cursor.lastrowid)

    @classmethod
    def sincronizar_quantidade(
        cls,
        cursor: Any,
        produto_id: int,
        nova_quantidade: int,
        quantidade_anterior: int = 0,
    ) -> list[tuple[int, int]]:
        lotes = cls._obter_lotes(cursor, produto_id)
        if not lotes:
            lote_id = cls._criar_lote_automatico(cursor, produto_id, nova_quantidade)
            return [(lote_id, int(nova_quantidade) - int(quantidade_anterior))]

        total_lotes = sum(int(cls._campo(lote, 1, "quantidade", 0) or 0) for lote in lotes)
        diferenca = int(nova_quantidade) - total_lotes
        if diferenca == 0:
            return []

        movimentacoes: list[tuple[int, int]] = []
        if diferenca > 0:
            lote_id = int(cls._campo(lotes[0], 0, "id", 0))
            cursor.execute(
                "UPDATE lotes SET quantidade = quantidade + %s, updatedAt = NOW() WHERE id = %s",
                (diferenca, lote_id),
            )
            return [(lote_id, diferenca)]

        restante = abs(diferenca)
        for lote in lotes:
            lote_id = int(cls._campo(lote, 0, "id", 0))
            disponivel = int(cls._campo(lote, 1, "quantidade", 0) or 0)
            reduzir = min(disponivel, restante)
            if reduzir <= 0:
                continue
            cursor.execute(
                "UPDATE lotes SET quantidade = quantidade - %s, updatedAt = NOW() WHERE id = %s",
                (reduzir, lote_id),
            )
            movimentacoes.append((lote_id, -reduzir))
            restante -= reduzir
            if restante == 0:
                break
        return movimentacoes

    @classmethod
    def baixar_quantidade(
        cls,
        cursor: Any,
        produto_id: int,
        quantidade: int,
    ) -> list[tuple[int, int]]:
        lotes = cls._obter_lotes(cursor, produto_id, bloquear=True)
        if not lotes:
            cursor.execute(
                "SELECT quantidade_estoque FROM produtos WHERE id = %s FOR UPDATE",
                (int(produto_id),),
            )
            estoque = int(cls._campo(cursor.fetchone() or (0,), 0, "quantidade_estoque", 0) or 0)
            lote_id = cls._criar_lote_automatico(cursor, produto_id, estoque)
            lotes = [(lote_id, estoque)]

        restante = int(quantidade)
        movimentacoes: list[tuple[int, int]] = []
        for lote in lotes:
            disponivel = int(cls._campo(lote, 1, "quantidade", 0) or 0)
            retirada = min(disponivel, restante)
            if retirada <= 0:
                continue
            lote_id = int(cls._campo(lote, 0, "id", 0))
            cursor.execute(
                "UPDATE lotes SET quantidade = quantidade - %s, updatedAt = NOW() WHERE id = %s",
                (retirada, lote_id),
            )
            movimentacoes.append((lote_id, retirada))
            restante -= retirada
            if restante == 0:
                return movimentacoes

        raise ValueError("Não foi possível localizar estoque disponível nos lotes.")
