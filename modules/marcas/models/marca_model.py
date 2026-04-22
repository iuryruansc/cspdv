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
