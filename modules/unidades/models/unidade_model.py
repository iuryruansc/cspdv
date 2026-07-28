from __future__ import annotations

from typing import Any, Sequence, cast

from database.connection import db_cursor, db_transaction

class UnidadeModel:
    @staticmethod
    def listar() -> list[dict[str, Any]]:
        with db_cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    sigla,
                    descricao,
                    codigo_sefaz,
                    COALESCE(`fracionável`, 0) AS fracionavel,
                    ativo
                FROM unidades_medida
                ORDER BY sigla
                """
            )
            return cast(list[dict[str, Any]], cur.fetchall())
    @staticmethod
    def buscar_por_id(unidade_id: int) -> dict[str, Any] | None:
        with db_cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    sigla,
                    descricao,
                    codigo_sefaz,
                    COALESCE(`fracionável`, 0) AS fracionavel,
                    ativo
                FROM unidades_medida
                WHERE id = %s
                LIMIT 1
                """,
                (int(unidade_id),),
            )
            return cast(dict[str, Any] | None, cur.fetchone())
    @staticmethod
    def buscar_por_sigla(sigla: str) -> dict[str, Any] | None:
        with db_cursor() as cur:
            cur.execute(
                """
                SELECT id, sigla, descricao, codigo_sefaz, COALESCE(`fracionável`, 0) AS fracionavel, ativo
                FROM unidades_medida
                WHERE UPPER(TRIM(sigla)) = UPPER(TRIM(%s))
                LIMIT 1
                """,
                (sigla,),
            )
            return cast(dict[str, Any] | None, cur.fetchone())
    @staticmethod
    def inserir(dados: dict[str, Any]) -> int | None:
        with db_transaction(dictionary=False) as cur:
            cur.execute(
                """
                INSERT INTO unidades_medida
                    (sigla, descricao, codigo_sefaz, `fracionável`, ativo, createdAt, updatedAt)
                VALUES
                    (%(sigla)s, %(descricao)s, %(codigo_sefaz)s, %(fracionavel)s, %(ativo)s, NOW(), NOW())
                """,
                dados,
            )
            return cur.lastrowid
    @staticmethod
    def atualizar(unidade_id: int, dados: dict[str, Any]) -> bool:
        with db_transaction(dictionary=False) as cur:
            cur.execute(
                """
                UPDATE unidades_medida
                SET
                    sigla = %(sigla)s,
                    descricao = %(descricao)s,
                    codigo_sefaz = %(codigo_sefaz)s,
                    `fracionável` = %(fracionavel)s,
                    ativo = %(ativo)s,
                    updatedAt = NOW()
                WHERE id = %(id)s
                """,
                {**dados, "id": int(unidade_id)},
            )
            return cur.rowcount > 0
    @staticmethod
    def atualizar_status(unidade_id: int, ativo: str) -> bool:
        with db_transaction(dictionary=False) as cur:
            cur.execute(
                "UPDATE unidades_medida SET ativo = %s WHERE id = %s",
                (ativo, int(unidade_id)),
            )
            return cur.rowcount > 0
    @staticmethod
    def contar_produtos_vinculados(unidade_id: int) -> int:
        with db_cursor(dictionary=False) as cur:
            cur.execute(
                """
                SELECT COUNT(*)
                FROM produtos
                WHERE unidade_id = %s OR unidade_tributavel_id = %s
                """,
                (int(unidade_id), int(unidade_id)),
            )
            row = cast(Sequence[Any] | None, cur.fetchone())
            if not row:
                return 0
            return int(row[0] or 0)
