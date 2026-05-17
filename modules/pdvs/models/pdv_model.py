from typing import Any, Dict, List, Optional, cast

from database.connection import get_connection


class PdvModel:
    @staticmethod
    def listar() -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
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
            return cast(List[Dict[str, Any]], cursor.fetchall())
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def buscar_por_id(pdv_id: int) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
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
            return cast(Optional[Dict[str, Any]], cursor.fetchone())
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def buscar_por_identificacao(identificacao: str) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT id, identificacao, descricao, status, ativo
                FROM pdvs
                WHERE UPPER(TRIM(identificacao)) = UPPER(TRIM(%s))
                LIMIT 1
                """,
                (identificacao,),
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
                INSERT INTO pdvs
                    (identificacao, descricao, status, ativo, createdAt, updatedAt)
                VALUES
                    (%(identificacao)s, %(descricao)s, %(status)s, %(ativo)s, NOW(), NOW())
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
    def atualizar(pdv_id: int, dados: Dict[str, Any]) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
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
            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def atualizar_status(pdv_id: int, ativo: str, status: str) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE pdvs SET ativo = %s, status = %s WHERE id = %s",
                (ativo, status, int(pdv_id)),
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()
