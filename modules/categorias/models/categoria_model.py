from typing import Any, Dict, List, Optional, cast

from database.connection import get_connection

class CategoriaModel:
    @staticmethod
    def listar() -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT id, nome, ativo
                FROM categorias
                ORDER BY nome
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
                INSERT INTO categorias (nome, ativo)
                VALUES (%(nome)s, %(ativo)s)
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
    def buscar_por_id(categoria_id: int) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT id, nome, ativo
                FROM categorias
                WHERE id = %s
                LIMIT 1
                """,
                (categoria_id,),
            )
            return cast(Optional[Dict[str, Any]], cursor.fetchone())
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def atualizar(categoria_id: int, dados: Dict[str, Any]) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                UPDATE categorias
                SET nome = %(nome)s,
                    ativo = %(ativo)s
                WHERE id = %(id)s
                """,
                {**dados, "id": categoria_id},
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
    def atualizar_status(categoria_id: int, ativo: str) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE categorias SET ativo = %s WHERE id = %s",
                (ativo, categoria_id),
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()
