from typing import Optional, Dict, Any, List, cast
from database.connection import get_connection

class ProdutoModel:
    @staticmethod
    def listar_resumo() -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    p.id,
                    p.codigo_barras,
                    p.nome,
                    p.preco_venda,
                    p.quantidade_estoque,
                    p.ativo,
                    c.nome AS categoria,
                    m.nome_marca AS marca,
                    f.nome_fantasia AS fornecedor
                FROM produtos p
                LEFT JOIN categorias c ON c.id = p.categoria_id
                LEFT JOIN marcas m ON m.id = p.marca_id
                LEFT JOIN fornecedores f ON f.id_fornecedor = p.fornecedor_id
                ORDER BY p.nome
                """
            )
            return cast(List[Dict[str, Any]], cursor.fetchall())
        except Exception as e:
            print(f"Erro ao listar produtos: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

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
    def buscar_por_id(produto_id: int) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT id, nome, codigo_barras, quantidade_estoque, ativo
                FROM produtos
                WHERE id = %s
                LIMIT 1
                """,
                (produto_id,),
            )
            resultado = cursor.fetchone()
            return cast(Optional[Dict[str, Any]], resultado)
        except Exception as e:
            print(f"Erro ao buscar produto por id: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def ajustar_quantidade(
        produto_id: int,
        nova_quantidade: float,
        quantidade_anterior: float,
        quantidade_ajuste: float,
        usuario_id: int,
        observacoes: str,
    ) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                UPDATE produtos
                SET quantidade_estoque = %s
                WHERE id = %s
                """,
                (nova_quantidade, produto_id),
            )

            cursor.execute(
                """
                INSERT INTO estoque_ajustes (usuario_id, observacoes)
                VALUES (%s, %s)
                """,
                (usuario_id, observacoes or None),
            )
            estoque_ajuste_id = cursor.lastrowid

            cursor.execute(
                """
                INSERT INTO estoque_ajustes_itens
                    (estoque_ajuste_id, produto_id, quantidade_informada, quantidade_anterior, quantidade_ajuste)
                VALUES
                    (%s, %s, %s, %s, %s)
                """,
                (
                    estoque_ajuste_id,
                    produto_id,
                    nova_quantidade,
                    quantidade_anterior,
                    quantidade_ajuste,
                ),
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Erro ao ajustar quantidade: {e}")
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
