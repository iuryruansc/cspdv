from database.connection import get_connection

class CategoriaModel:
    @staticmethod
    def listar_ativas() -> list[dict]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT id, nome FROM categorias WHERE ativo = 'S' ORDER BY nome"
            )
            return cursor.fetchall()
        finally:
            cursor.close()


class MarcaModel:
    @staticmethod
    def listar_ativas() -> list[dict]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT id, nome_marca AS nome FROM marcas WHERE ativo = 'S' ORDER BY nome_marca"
            )
            return cursor.fetchall()
        finally:
            cursor.close()


class FornecedorModel:
    @staticmethod
    def listar_ativos() -> list[dict]:
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
            return cursor.fetchall()
        finally:
            cursor.close()


class UnidadeModel:
    @staticmethod
    def listar_ativas() -> list[dict]:
        """Retorna sigla + descrição como texto visível: 'UN — Unidade'"""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT id,
                       CONCAT(sigla, ' — ', descricao) AS nome
                FROM   unidades_medida
                WHERE  ativo = 'S'
                ORDER  BY sigla
                """
            )
            return cursor.fetchall()
        finally:
            cursor.close()