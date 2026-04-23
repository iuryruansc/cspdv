from typing import Any, Dict, List, Optional, cast

from database.connection import get_connection

class MarcaModel:
    @staticmethod
    def listar() -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT id, nome_marca, ativo
                FROM marcas
                ORDER BY nome_marca
                """
            )
            return cast(List[Dict[str, Any]], cursor.fetchall())
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
                INSERT INTO marcas (nome_marca, ativo)
                VALUES (%(nome_marca)s, %(ativo)s)
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
    def buscar_por_id(marca_id: int) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT id, nome_marca, ativo
                FROM marcas
                WHERE id = %s
                LIMIT 1
                """,
                (marca_id,),
            )
            return cast(Optional[Dict[str, Any]], cursor.fetchone())
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def atualizar(marca_id: int, dados: Dict[str, Any]) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                UPDATE marcas
                SET nome_marca = %(nome_marca)s,
                    ativo = %(ativo)s
                WHERE id = %(id)s
                """,
                {**dados, "id": marca_id},
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
    def atualizar_status(marca_id: int, ativo: str) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE marcas SET ativo = %s WHERE id = %s",
                (ativo, marca_id),
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()
