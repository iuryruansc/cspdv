from database.connection import get_connection

class CategoriaModel:
    @staticmethod
    def listar_todas():
        connection = get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT id, descricao FROM categorias ORDER BY descricao")
                return cursor.fetchall()
        except Exception as e:
            print(f"Erro ao buscar categorias: {e}")
            return []
        finally:
            connection.close()