from typing import Optional, Dict, Any, List, cast
from database.connection import get_connection
from modules.admin.models.configuracoes_model import ConfiguracoesModel
from utils.app_logger import log_error

class ProdutoModel:
    @staticmethod
    def buscar_para_venda(termo: str, limite: int = 10) -> List[Dict[str, Any]]:
        parametros_promocoes = ConfiguracoesModel.carregar_empresa_pdv()
        ativar_por_vigencia = bool(parametros_promocoes.get("ativar_promocoes_por_vigencia", True))

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        termo_limpo = str(termo or "").strip()
        termo_nome = f"%{termo_limpo.upper()}%"
        termo_prefixo = f"{termo_limpo.upper()}%"
        termo_codigo = f"{termo_limpo}%"
        
        # Build query based on vigencia setting
        if ativar_por_vigencia:
            query = """
                SELECT
                    p.id,
                    p.codigo_barras,
                    p.nome,
                    COALESCE(ppromo.preco_promocional, p.preco_venda) AS preco_venda,
                    p.preco_venda AS preco_venda_base,
                    ppromo.preco_original AS preco_original_promocao,
                    ppromo.preco_promocional,
                    promo.id AS promocao_id,
                    promo.nome AS promocao_nome,
                    p.quantidade_estoque,
                    p.ativo,
                    p.imagem_path,
                    COALESCE(uc.sigla, '-') AS unidade,
                    c.nome AS categoria,
                    m.nome_marca AS marca,
                    f.nome_fantasia AS fornecedor
                FROM produtos p
                LEFT JOIN promocao_produtos ppromo
                    ON ppromo.id = (
                        SELECT pp2.id
                        FROM promocao_produtos pp2
                        INNER JOIN promocoes pr2 ON pr2.id = pp2.promocao_id
                        WHERE pp2.produto_id = p.id
                          AND pp2.ativo = 'S'
                          AND pr2.ativo = 'S'
                          AND pr2.status IN ('ATIVA', 'AGENDADA')
                          AND NOW() BETWEEN pr2.data_inicio AND pr2.data_fim
                        ORDER BY pp2.preco_promocional ASC, pr2.data_inicio DESC, pp2.id DESC
                        LIMIT 1
                    )
                LEFT JOIN promocoes promo ON promo.id = ppromo.promocao_id
                LEFT JOIN categorias c ON c.id = p.categoria_id
                LEFT JOIN marcas m ON m.id = p.marca_id
                LEFT JOIN fornecedores f ON f.id_fornecedor = p.fornecedor_id
                LEFT JOIN unidades_medida uc ON uc.id = p.unidade_id
                WHERE p.ativo = 'S'
                  AND (
                    p.codigo_barras = %s
                    OR p.codigo_barras LIKE %s
                    OR UPPER(p.nome) LIKE %s
                  )
                ORDER BY
                    CASE
                        WHEN p.codigo_barras = %s THEN 0
                        WHEN UPPER(p.nome) = UPPER(%s) THEN 1
                        WHEN UPPER(p.nome) LIKE %s THEN 2
                        WHEN p.codigo_barras LIKE %s THEN 3
                        ELSE 4
                    END,
                    p.nome
                LIMIT %s
                """
        else:
            query = """
                SELECT
                    p.id,
                    p.codigo_barras,
                    p.nome,
                    COALESCE(ppromo.preco_promocional, p.preco_venda) AS preco_venda,
                    p.preco_venda AS preco_venda_base,
                    ppromo.preco_original AS preco_original_promocao,
                    ppromo.preco_promocional,
                    promo.id AS promocao_id,
                    promo.nome AS promocao_nome,
                    p.quantidade_estoque,
                    p.ativo,
                    p.imagem_path,
                    COALESCE(uc.sigla, '-') AS unidade,
                    c.nome AS categoria,
                    m.nome_marca AS marca,
                    f.nome_fantasia AS fornecedor
                FROM produtos p
                LEFT JOIN promocao_produtos ppromo
                    ON ppromo.id = (
                        SELECT pp2.id
                        FROM promocao_produtos pp2
                        INNER JOIN promocoes pr2 ON pr2.id = pp2.promocao_id
                        WHERE pp2.produto_id = p.id
                          AND pp2.ativo = 'S'
                          AND pr2.ativo = 'S'
                          AND pr2.status = 'ATIVA'
                        ORDER BY pp2.preco_promocional ASC, pr2.data_inicio DESC, pp2.id DESC
                        LIMIT 1
                    )
                LEFT JOIN promocoes promo ON promo.id = ppromo.promocao_id
                LEFT JOIN categorias c ON c.id = p.categoria_id
                LEFT JOIN marcas m ON m.id = p.marca_id
                LEFT JOIN fornecedores f ON f.id_fornecedor = p.fornecedor_id
                LEFT JOIN unidades_medida uc ON uc.id = p.unidade_id
                WHERE p.ativo = 'S'
                  AND (
                    p.codigo_barras = %s
                    OR p.codigo_barras LIKE %s
                    OR UPPER(p.nome) LIKE %s
                  )
                ORDER BY
                    CASE
                        WHEN p.codigo_barras = %s THEN 0
                        WHEN UPPER(p.nome) = UPPER(%s) THEN 1
                        WHEN UPPER(p.nome) LIKE %s THEN 2
                        WHEN p.codigo_barras LIKE %s THEN 3
                        ELSE 4
                    END,
                    p.nome
                LIMIT %s
                """
        
        try:
            cursor.execute(
                query,
                (
                    termo_limpo,
                    termo_codigo,
                    termo_nome,
                    termo_limpo,
                    termo_limpo,
                    termo_prefixo,
                    termo_codigo,
                    limite,
                ),
            )
            return cast(List[Dict[str, Any]], cursor.fetchall())
        except Exception as e:
            log_error("Erro ao buscar produtos para venda.", e)
            raise
        finally:
            cursor.close()
            conn.close()

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
            log_error("Erro ao listar produtos.", e)
            raise
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def buscar_por_codigo_barras(codigo: str) -> Optional[Dict[str, Any]]:
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
            log_error("Erro ao buscar produto por código de barras.", e)
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
                "SELECT * FROM produtos WHERE cod_produto = %s LIMIT 1",
                (codigo,)
            )
            resultado = cursor.fetchone()
            return cast(Optional[Dict[str, Any]], resultado)
        except Exception as e:
            log_error("Erro ao buscar produto por código de fabricante.", e)
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
                SELECT
                    p.id,
                    p.codigo_barras,
                    p.nome,
                    p.ncm,
                    p.cest,
                    p.preco_compra,
                    p.preco_venda,
                    p.quantidade_estoque,
                    p.categoria_id,
                    p.marca_id,
                    p.fornecedor_id,
                    p.unidade_id,
                    p.unidade_tributavel_id,
                    p.ativo,
                    p.imagem_path,
                    c.nome AS categoria_nome,
                    m.nome_marca AS marca_nome,
                    f.nome_fantasia AS fornecedor_nome,
                    uc.sigla AS unidade_sigla,
                    ut.sigla AS unidade_tributavel_sigla
                FROM produtos p
                LEFT JOIN categorias c ON c.id = p.categoria_id
                LEFT JOIN marcas m ON m.id = p.marca_id
                LEFT JOIN fornecedores f ON f.id_fornecedor = p.fornecedor_id
                LEFT JOIN unidades_medida uc ON uc.id = p.unidade_id
                LEFT JOIN unidades_medida ut ON ut.id = p.unidade_tributavel_id
                WHERE p.id = %s
                LIMIT 1
                """,
                (produto_id,),
            )
            resultado = cursor.fetchone()
            return cast(Optional[Dict[str, Any]], resultado)
        except Exception as e:
            log_error("Erro ao buscar produto por ID.", e)
            raise
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def atualizar(produto_id: int, dados: Dict[str, Any]) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                UPDATE produtos
                SET
                    codigo_barras = %(codigo_barras)s,
                    nome = %(nome)s,
                    ncm = %(ncm)s,
                    cest = %(cest)s,
                    preco_compra = %(preco_compra)s,
                    preco_venda = %(preco_venda)s,
                    quantidade_estoque = %(quantidade_estoque)s,
                    categoria_id = %(categoria_id)s,
                    marca_id = %(marca_id)s,
                    fornecedor_id = %(fornecedor_id)s,
                    unidade_id = %(unidade_id)s,
                    unidade_tributavel_id = %(unidade_tributavel_id)s,
                    ativo = %(ativo)s,
                    imagem_path = %(imagem_path)s
                WHERE id = %(id)s
                """,
                {**dados, "id": produto_id},
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            log_error("Erro ao atualizar produto.", e)
            raise
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def atualizar_status(produto_id: int, ativo: str) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                UPDATE produtos
                SET ativo = %s
                WHERE id = %s
                """,
                (ativo, produto_id),
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            log_error("Erro ao atualizar status do produto.", e)
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

            ProdutoModel._sincronizar_lotes_quantidade(
                cursor=cursor,
                produto_id=produto_id,
                nova_quantidade=int(nova_quantidade),
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
            log_error("Erro ao ajustar quantidade do produto.", e)
            raise
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def _sincronizar_lotes_quantidade(cursor, produto_id: int, nova_quantidade: int) -> None:
        cursor.execute(
            """
            SELECT id, numero_lote, quantidade
            FROM lotes
            WHERE produto_id = %s
              AND ativo = 'S'
            ORDER BY
                CASE WHEN numero_lote LIKE 'AUTO-%%' THEN 0 ELSE 1 END,
                data_validade DESC,
                id DESC
            """,
            (produto_id,),
        )
        lotes = cursor.fetchall()
        if not lotes:
            return

        total_lotes = sum(int(lote[2] or 0) for lote in lotes)
        diferenca = int(nova_quantidade) - total_lotes
        if diferenca == 0:
            return

        if diferenca > 0:
            lote_id = int(lotes[0][0])
            cursor.execute(
                """
                UPDATE lotes
                SET quantidade = quantidade + %s,
                    updatedAt = NOW()
                WHERE id = %s
                """,
                (diferenca, lote_id),
            )
            return

        restante_reduzir = abs(diferenca)
        for lote in lotes:
            lote_id = int(lote[0])
            quantidade_atual = int(lote[2] or 0)
            if quantidade_atual <= 0:
                continue
            reduzir = min(quantidade_atual, restante_reduzir)
            if reduzir <= 0:
                continue
            cursor.execute(
                """
                UPDATE lotes
                SET quantidade = quantidade - %s,
                    updatedAt = NOW()
                WHERE id = %s
                """,
                (reduzir, lote_id),
            )
            restante_reduzir -= reduzir
            if restante_reduzir == 0:
                break

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
            log_error("Erro ao inserir produto.", e)
            raise
        finally:
            cursor.close()
            conn.close()
