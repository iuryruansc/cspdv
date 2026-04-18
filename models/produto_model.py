from database.connection import get_connection

class ProdutoModel:
    @staticmethod
    def buscar_por_codigo(codigo):
        connection = get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = "SELECT * FROM produtos WHERE codigo_barras = %s LIMIT 1"
                cursor.execute(sql, (codigo,))
                return cursor.fetchone()
        except Exception as e:
            print(f"Erro de SQL na ProdutoModel: {e}")
            raise e
        finally:
            connection.close()

    @staticmethod
    def inserir(dados):
        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                    INSERT INTO produtos 
                    (codigo_barras, descricao, ncm, cest, preco_custo, preco_venda, estoque_atual, id_categoria, id_unidade) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                valores = (
                    dados['codigo_barras'], dados['descricao'], dados['ncm'],
                    dados['cest'], dados['preco_custo'], dados['preco_venda'],
                    dados['estoque'], dados['id_categoria'], dados['id_unidade']
                )
                cursor.execute(sql, valores)
                connection.commit()
        finally:
            connection.close()