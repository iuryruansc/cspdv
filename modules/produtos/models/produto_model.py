from typing import Optional, Dict, Any, cast
from database.connection import get_connection

class ProdutoModel:

    @staticmethod
    def buscar_por_codigo(codigo: str) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT * FROM produtos WHERE codigo_barras = %s LIMIT 1",
                (codigo,)
            )
            resultado = cursor.fetchone()
            return cast(Optional[Dict[str, Any]], resultado)
        except Exception as e:
            print(f"Erro ao buscar produto por código: {e}")
            raise
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
                INSERT INTO produtos
                    (codigo_barras, nome, ncm, cest,
                     preco_compra, preco_venda, quantidade_estoque,
                     categoria_id, marca_id, fornecedor_id,
                     unidade_id, unidade_tributavel_id, ativo, imagem_path)
                VALUES
                    (%(codigo_barras)s, %(nome)s, %(ncm)s, %(cest)s,
                     %(preco_compra)s, %(preco_venda)s, %(quantidade_estoque)s,
                     %(categoria_id)s, %(marca_id)s, %(fornecedor_id)s,
                     %(unidade_id)s, %(unidade_tributavel_id)s, %(ativo)s, %(imagem_path)s)
                """,
                dados,
            )
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            conn.rollback()
            print(f"Erro ao inserir: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
