from __future__ import annotations

from typing import Any

from database.connection import db_cursor, db_transaction
from modules.shared.constants import FLAG_SIM


class KitModel:
    @staticmethod
    def listar_resumo() -> list[dict[str, Any]]:
        with db_cursor() as cur:
            cur.execute(
                """
                SELECT
                    k.id,
                    k.cod_produto,
                    k.nome,
                    k.preco_kit,
                    k.quantidade_estoque,
                    (SELECT COUNT(*) FROM kit_itens ki WHERE ki.kit_id = k.id) AS qtd_itens,
                    k.ativo
                FROM kits k
                WHERE k.ativo = %s
                ORDER BY k.nome
                """,
                (FLAG_SIM,),
            )
            return list(cur.fetchall())

    @staticmethod
    def listar_todas() -> list[dict[str, Any]]:
        with db_cursor() as cur:
            cur.execute(
                """
                SELECT
                    k.id,
                    k.cod_produto,
                    k.nome,
                    k.descricao,
                    k.preco_kit,
                    k.quantidade_estoque,
                    k.ativo,
                    k.createdAt
                FROM kits k
                ORDER BY k.nome
                """,
            )
            return list(cur.fetchall())

    @staticmethod
    def buscar_por_id(kit_id: int) -> dict[str, Any] | None:
        with db_cursor() as cur:
            cur.execute(
                """
                SELECT
                    k.id,
                    k.cod_produto,
                    k.nome,
                    k.descricao,
                    k.preco_kit,
                    k.quantidade_estoque,
                    k.ativo
                FROM kits k
                WHERE k.id = %s
                LIMIT 1
                """,
                (int(kit_id),),
            )
            return cur.fetchone()

    @staticmethod
    def listar_itens(kit_id: int) -> list[dict[str, Any]]:
        with db_cursor() as cur:
            cur.execute(
                """
                SELECT
                    ki.id,
                    ki.produto_id,
                    p.nome AS produto,
                    p.codigo_barras,
                    p.preco_venda,
                    ki.quantidade,
                    (p.preco_venda * ki.quantidade) AS subtotal
                FROM kit_itens ki
                INNER JOIN produtos p ON p.id = ki.produto_id
                WHERE ki.kit_id = %s
                ORDER BY p.nome
                """,
                (int(kit_id),),
            )
            return list(cur.fetchall())

    @staticmethod
    def criar_kit(
        *,
        cod_produto: str | None,
        nome: str,
        descricao: str,
        preco_kit: float,
        quantidade_estoque: int,
        itens: list[dict[str, Any]],
    ) -> int:
        with db_transaction() as cur:
            cur.execute(
                """
                INSERT INTO kits
                    (cod_produto, nome, descricao, preco_kit, quantidade_estoque, ativo, createdAt, updatedAt)
                VALUES
                    (%s, %s, %s, %s, %s, %s, NOW(), NOW())
                """,
                (cod_produto, str(nome), str(descricao), float(preco_kit), int(quantidade_estoque), FLAG_SIM),
            )
            kit_id = int(cur.lastrowid or 0)
            if kit_id <= 0:
                raise RuntimeError("Nao foi possivel criar o kit.")

            for item in itens:
                cur.execute(
                    """
                    INSERT INTO kit_itens
                        (kit_id, produto_id, quantidade, createdAt, updatedAt)
                    VALUES
                        (%s, %s, %s, NOW(), NOW())
                    """,
                    (kit_id, int(item["produto_id"]), int(item["quantidade"])),
                )

            return kit_id

    @staticmethod
    def atualizar_kit(
        *,
        kit_id: int,
        cod_produto: str | None,
        nome: str,
        descricao: str,
        preco_kit: float,
        quantidade_estoque: int,
        itens: list[dict[str, Any]],
    ) -> None:
        with db_transaction() as cur:
            cur.execute(
                """
                UPDATE kits
                SET cod_produto = %s,
                    nome = %s,
                    descricao = %s,
                    preco_kit = %s,
                    quantidade_estoque = %s,
                    updatedAt = NOW()
                WHERE id = %s
                """,
                (cod_produto, str(nome), str(descricao), float(preco_kit), int(quantidade_estoque), int(kit_id)),
            )

            cur.execute(
                "DELETE FROM kit_itens WHERE kit_id = %s",
                (int(kit_id),),
            )

            for item in itens:
                cur.execute(
                    """
                    INSERT INTO kit_itens
                        (kit_id, produto_id, quantidade, createdAt, updatedAt)
                    VALUES
                        (%s, %s, %s, NOW(), NOW())
                    """,
                    (int(kit_id), int(item["produto_id"]), int(item["quantidade"])),
                )

    @staticmethod
    def alternar_status(kit_id: int) -> bool:
        with db_transaction() as cur:
            cur.execute(
                "SELECT ativo FROM kits WHERE id = %s LIMIT 1",
                (int(kit_id),),
            )
            row = cur.fetchone()
            if not row:
                return False
            novo_status = "N" if str(row.get("ativo") or FLAG_SIM).upper() == FLAG_SIM else FLAG_SIM
            cur.execute(
                "UPDATE kits SET ativo = %s, updatedAt = NOW() WHERE id = %s",
                (novo_status, int(kit_id)),
            )
            return True

    @staticmethod
    def excluir_kit(kit_id: int) -> bool:
        with db_transaction() as cur:
            cur.execute(
                "DELETE FROM kits WHERE id = %s",
                (int(kit_id),),
            )
            return cur.rowcount > 0

    @staticmethod
    def atualizar_estoque(kit_id: int, nova_quantidade: int) -> bool:
        with db_transaction() as cur:
            cur.execute(
                "UPDATE kits SET quantidade_estoque = %s, updatedAt = NOW() WHERE id = %s",
                (int(nova_quantidade), int(kit_id)),
            )
            return cur.rowcount > 0

    @staticmethod
    def ajustar_estoque_e_componentes(
        kit_id: int,
        nova_quantidade_kit: int,
        diferenca: int,
    ) -> None:
        with db_transaction() as cur:
            cur.execute(
                "UPDATE kits SET quantidade_estoque = %s, updatedAt = NOW() WHERE id = %s",
                (int(nova_quantidade_kit), int(kit_id)),
            )

            if diferenca == 0:
                return

            cur.execute(
                "SELECT produto_id, quantidade FROM kit_itens WHERE kit_id = %s",
                (int(kit_id),),
            )
            itens = cur.fetchall()

            for item in itens:
                produto_id = int(item["produto_id"])
                qtd_por_kit = int(item["quantidade"])
                ajuste = qtd_por_kit * diferenca

                if ajuste > 0:
                    cur.execute(
                        "UPDATE produtos SET quantidade_estoque = GREATEST(quantidade_estoque - %s, 0), updatedAt = NOW() WHERE id = %s",
                        (ajuste, produto_id),
                    )
                else:
                    cur.execute(
                        "UPDATE produtos SET quantidade_estoque = GREATEST(quantidade_estoque + %s, 0), updatedAt = NOW() WHERE id = %s",
                        (abs(ajuste), produto_id),
                    )

    @staticmethod
    def buscar_para_venda(termo: str, limite: int = 10) -> list[dict[str, Any]]:
        with db_cursor() as cur:
            termo_limpo = str(termo or "").strip()
            termo_nome = f"%{termo_limpo.upper()}%"
            termo_codigo = f"{termo_limpo}%"
            cur.execute(
                """
                SELECT
                    k.id AS kit_id,
                    k.nome AS kit_nome,
                    k.preco_kit AS preco_venda,
                    k.quantidade_estoque,
                    k.id AS id,
                    k.cod_produto,
                    NULL AS codigo_barras,
                    k.nome AS nome,
                    NULL AS imagem_path,
                    'KIT' AS tipo_item
                FROM kits k
                WHERE k.ativo = 'S'
                  AND k.quantidade_estoque > 0
                  AND (
                    k.cod_produto = %s
                    OR k.cod_produto LIKE %s
                    OR UPPER(k.nome) LIKE %s
                  )
                ORDER BY
                    CASE
                        WHEN k.cod_produto = %s THEN 0
                        WHEN k.cod_produto LIKE %s THEN 1
                        WHEN UPPER(k.nome) = UPPER(%s) THEN 2
                        WHEN UPPER(k.nome) LIKE %s THEN 3
                        ELSE 4
                    END,
                    k.nome
                LIMIT %s
                """,
                (
                    termo_limpo, termo_codigo, termo_nome,
                    termo_limpo, termo_codigo, termo_limpo, termo_nome,
                    int(limite),
                ),
            )
            return list(cur.fetchall())
