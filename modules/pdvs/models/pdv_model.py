from __future__ import annotations

from typing import Any, cast

from database.connection import db_cursor, db_transaction

class PdvModel:
    @staticmethod
    def listar() -> list[dict[str, Any]]:
        with db_cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    identificacao,
                    descricao,
                    status,
                    ativo
                FROM pdvs
                ORDER BY identificacao
                """
            )
            return cast(list[dict[str, Any]], cur.fetchall())
    @staticmethod
    def buscar_por_id(pdv_id: int) -> dict[str, Any] | None:
        with db_cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    identificacao,
                    descricao,
                    status,
                    ativo
                FROM pdvs
                WHERE id = %s
                LIMIT 1
                """,
                (int(pdv_id),),
            )
            return cast(dict[str, Any] | None, cur.fetchone())
    @staticmethod
    def buscar_por_identificacao(identificacao: str) -> dict[str, Any] | None:
        with db_cursor() as cur:
            cur.execute(
                """
                SELECT id, identificacao, descricao, status, ativo
                FROM pdvs
                WHERE UPPER(TRIM(identificacao)) = UPPER(TRIM(%s))
                LIMIT 1
                """,
                (identificacao,),
            )
            return cast(dict[str, Any] | None, cur.fetchone())
    @staticmethod
    def inserir(dados: dict[str, Any]) -> int | None:
        with db_transaction(dictionary=False) as cur:
            cur.execute(
                """
                INSERT INTO pdvs
                    (identificacao, descricao, status, ativo, createdAt, updatedAt)
                VALUES
                    (%(identificacao)s, %(descricao)s, %(status)s, %(ativo)s, NOW(), NOW())
                """,
                dados,
            )
            return cur.lastrowid
    @staticmethod
    def atualizar(pdv_id: int, dados: dict[str, Any]) -> bool:
        with db_transaction(dictionary=False) as cur:
            cur.execute(
                """
                UPDATE pdvs
                SET
                    identificacao = %(identificacao)s,
                    descricao = %(descricao)s,
                    status = %(status)s,
                    ativo = %(ativo)s,
                    updatedAt = NOW()
                WHERE id = %(id)s
                """,
                {**dados, "id": int(pdv_id)},
            )
            return cur.rowcount > 0
    @staticmethod
    def atualizar_status(pdv_id: int, ativo: str, status: str) -> bool:
        with db_transaction(dictionary=False) as cur:
            cur.execute(
                "UPDATE pdvs SET ativo = %s, status = %s WHERE id = %s",
                (ativo, status, int(pdv_id)),
            )
            return cur.rowcount > 0
