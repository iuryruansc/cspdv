from typing import List, Dict, Any, cast
from database.connection import get_connection


class CategoriaModel:
    @staticmethod
    def listar_ativas() -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT id, nome FROM categorias WHERE ativo = 'S' ORDER BY nome"
            )
            return cast(List[Dict[str, Any]], cursor.fetchall())
        finally:
            cursor.close()
            conn.close()


class MarcaModel:
    @staticmethod
    def listar_ativas() -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT id, nome_marca AS nome FROM marcas WHERE ativo = 'S' ORDER BY nome_marca"
            )
            return cast(List[Dict[str, Any]], cursor.fetchall())
        finally:
            cursor.close()
            conn.close()


class FornecedorModel:
    @staticmethod
    def listar_ativos() -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT id_fornecedor AS id, nome_fantasia AS nome
                FROM   fornecedores
                WHERE  ativo = 'S'
                ORDER  BY nome_fantasia
                """
            )
            return cast(List[Dict[str, Any]], cursor.fetchall())
        finally:
            cursor.close()
            conn.close()


class UnidadeModel:
    @staticmethod
    def listar_ativas() -> List[Dict[str, Any]]:
        """Retorna sigla + descricao como texto visivel: 'UN - Unidade'"""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT id,
                       CONCAT(sigla, ' - ', descricao) AS nome
                FROM   unidades_medida
                WHERE  ativo = 'S'
                ORDER  BY sigla
                """
            )
            return cast(List[Dict[str, Any]], cursor.fetchall())
        finally:
            cursor.close()
            conn.close()