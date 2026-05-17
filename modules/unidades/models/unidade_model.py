from typing import Any, Dict, List, Optional, Sequence, cast

from database.connection import get_connection


class UnidadeModel:
    @staticmethod
    def listar() -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
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
            return cast(List[Dict[str, Any]], cursor.fetchall())
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def buscar_por_id(unidade_id: int) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
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
            return cast(Optional[Dict[str, Any]], cursor.fetchone())
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def buscar_por_sigla(sigla: str) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT id, sigla, descricao, codigo_sefaz, COALESCE(`fracionável`, 0) AS fracionavel, ativo
                FROM unidades_medida
                WHERE UPPER(TRIM(sigla)) = UPPER(TRIM(%s))
                LIMIT 1
                """,
                (sigla,),
            )
            return cast(Optional[Dict[str, Any]], cursor.fetchone())
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def inserir(dados: Dict[str, Any]) -> Optional[int]:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO unidades_medida
                    (sigla, descricao, codigo_sefaz, `fracionável`, ativo, createdAt, updatedAt)
                VALUES
                    (%(sigla)s, %(descricao)s, %(codigo_sefaz)s, %(fracionavel)s, %(ativo)s, NOW(), NOW())
                """,
                dados,
            )
            conn.commit()
            return cursor.lastrowid
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def atualizar(unidade_id: int, dados: Dict[str, Any]) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
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
            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def atualizar_status(unidade_id: int, ativo: str) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE unidades_medida SET ativo = %s WHERE id = %s",
                (ativo, int(unidade_id)),
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def contar_produtos_vinculados(unidade_id: int) -> int:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM produtos
                WHERE unidade_id = %s OR unidade_tributavel_id = %s
                """,
                (int(unidade_id), int(unidade_id)),
            )
            row = cast(Sequence[Any] | None, cursor.fetchone())
            if not row:
                return 0
            return int(row[0] or 0)
        finally:
            cursor.close()
            conn.close()
