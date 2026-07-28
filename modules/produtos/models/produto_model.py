from __future__ import annotations

from typing import Any, cast
from database.connection import db_cursor, db_transaction
from modules.admin.models.configuracoes_model import ConfiguracoesModel
from modules.shared.constants import STATUS_PROMOCAO_AGENDADA, STATUS_PROMOCAO_ATIVA
from utils.app_logger import log_error

class ProdutoModel:
    @staticmethod
    def buscar_para_venda(termo: str, limite: int = 10) -> list[dict[str, Any]]:
        parametros_promocoes = ConfiguracoesModel.carregar_empresa_pdv()
        ativar_por_vigencia = bool(parametros_promocoes.get("ativar_promocoes_por_vigencia", True))

        termo_limpo = str(termo or "").strip()
        termo_nome = f"%{termo_limpo.upper()}%"
        termo_prefixo = f"{termo_limpo.upper()}%"
        termo_codigo = f"{termo_limpo}%"

        # Build query based on vigencia setting
        if ativar_por_vigencia:
            query = """
                SELECT
                    p.id,
                    p.cod_produto,
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
                          AND pr2.status IN (%s, %s)
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
                  AND COALESCE(p.quantidade_estoque, 0) > 0
                  AND (
                    p.cod_produto = %s
                    OR p.cod_produto LIKE %s
                    OR
                    p.codigo_barras = %s
                    OR p.codigo_barras LIKE %s
                    OR UPPER(p.nome) LIKE %s
                  )
                ORDER BY
                    CASE
                        WHEN p.cod_produto = %s THEN 0
                        WHEN p.codigo_barras = %s THEN 1
                        WHEN UPPER(p.nome) = UPPER(%s) THEN 2
                        WHEN p.cod_produto LIKE %s THEN 3
                        WHEN UPPER(p.nome) LIKE %s THEN 4
                        WHEN p.codigo_barras LIKE %s THEN 5
                        ELSE 6
                    END,
                    p.nome
                LIMIT %s
                """
        else:
            query = """
                SELECT
                    p.id,
                    p.cod_produto,
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
                          AND pr2.status = %s
                        ORDER BY pp2.preco_promocional ASC, pr2.data_inicio DESC, pp2.id DESC
                        LIMIT 1
                    )
                LEFT JOIN promocoes promo ON promo.id = ppromo.promocao_id
                LEFT JOIN categorias c ON c.id = p.categoria_id
                LEFT JOIN marcas m ON m.id = p.marca_id
                LEFT JOIN fornecedores f ON f.id_fornecedor = p.fornecedor_id
                LEFT JOIN unidades_medida uc ON uc.id = p.unidade_id
                WHERE p.ativo = 'S'
                  AND COALESCE(p.quantidade_estoque, 0) > 0
                  AND (
                    p.cod_produto = %s
                    OR p.cod_produto LIKE %s
                    OR
                    p.codigo_barras = %s
                    OR p.codigo_barras LIKE %s
                    OR UPPER(p.nome) LIKE %s
                  )
                ORDER BY
                    CASE
                        WHEN p.cod_produto = %s THEN 0
                        WHEN p.codigo_barras = %s THEN 1
                        WHEN UPPER(p.nome) = UPPER(%s) THEN 2
                        WHEN p.cod_produto LIKE %s THEN 3
                        WHEN UPPER(p.nome) LIKE %s THEN 4
                        WHEN p.codigo_barras LIKE %s THEN 5
                        ELSE 6
                    END,
                    p.nome
                LIMIT %s
                """

        with db_cursor() as cur:
            try:
                parametros = [
                    termo_limpo,
                    termo_codigo,
                    termo_limpo,
                    termo_codigo,
                    termo_nome,
                    termo_limpo,
                    termo_limpo,
                    termo_limpo,
                    termo_codigo,
                    termo_prefixo,
                    termo_codigo,
                    limite,
                ]
                if ativar_por_vigencia:
                    parametros = [STATUS_PROMOCAO_ATIVA, STATUS_PROMOCAO_AGENDADA, *parametros]
                else:
                    parametros = [STATUS_PROMOCAO_ATIVA, *parametros]
                cur.execute(
                    query,
                    tuple(parametros),
                )
                return cast(list[dict[str, Any]], cur.fetchall())
            except Exception as e:
                log_error("Erro ao buscar produtos para venda.", e)
                raise

    @staticmethod
    def listar_resumo() -> list[dict[str, Any]]:
        with db_cursor() as cur:
            try:
                cur.execute(
                    """
                    SELECT
                        p.id,
                        p.cod_produto,
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
                return cast(list[dict[str, Any]], cur.fetchall())
            except Exception as e:
                log_error("Erro ao listar produtos.", e)
                raise
    @staticmethod
    def buscar_por_codigo_barras(codigo: str) -> dict[str, Any] | None:
        with db_cursor() as cur:
            try:
                cur.execute(
                    "SELECT * FROM produtos WHERE codigo_barras = %s LIMIT 1",
                    (codigo,)
                )
                resultado = cur.fetchone()
                return cast(dict[str, Any] | None, resultado)
            except Exception as e:
                log_error("Erro ao buscar produto por código de barras.", e)
                raise
    @staticmethod
    def buscar_por_codigo(codigo: str) -> dict[str, Any] | None:
        with db_cursor() as cur:
            try:
                cur.execute(
                    "SELECT * FROM produtos WHERE cod_produto = %s LIMIT 1",
                    (codigo,)
                )
                resultado = cur.fetchone()
                return cast(dict[str, Any] | None, resultado)
            except Exception as e:
                log_error("Erro ao buscar produto por código de fabricante.", e)
                raise
    @staticmethod
    def buscar_por_id(produto_id: int) -> dict[str, Any] | None:
        with db_cursor() as cur:
            try:
                cur.execute(
                    """
                    SELECT
                        p.id,
                        p.cod_produto,
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
                resultado = cur.fetchone()
                return cast(dict[str, Any] | None, resultado)
            except Exception as e:
                log_error("Erro ao buscar produto por ID.", e)
                raise
    @staticmethod
    def atualizar(produto_id: int, dados: dict[str, Any]) -> bool:
        with db_transaction(dictionary=False) as cur:
            cur.execute(
                """
                UPDATE produtos
                SET
                    cod_produto = %(cod_produto)s,
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
            return cur.rowcount > 0

    @staticmethod
    def atualizar_status(produto_id: int, ativo: str) -> bool:
        with db_transaction(dictionary=False) as cur:
            cur.execute(
                """
                UPDATE produtos
                SET ativo = %s
                WHERE id = %s
                """,
                (ativo, produto_id),
            )
            return cur.rowcount > 0
    @staticmethod
    def ajustar_quantidade(
        produto_id: int,
        nova_quantidade: float,
        quantidade_anterior: float,
        quantidade_ajuste: float,
        usuario_id: int,
        observacoes: str,
    ) -> None:
        with db_transaction(dictionary=False) as cur:
            cur.execute(
                """
                UPDATE produtos
                SET quantidade_estoque = %s
                WHERE id = %s
                """,
                (nova_quantidade, produto_id),
            )

            ProdutoModel._sincronizar_lotes_quantidade(
                cursor=cur,
                produto_id=produto_id,
                nova_quantidade=int(nova_quantidade),
            )

            cur.execute(
                """
                INSERT INTO estoque_ajustes (usuario_id, observacoes)
                VALUES (%s, %s)
                """,
                (usuario_id, observacoes or None),
            )
            estoque_ajuste_id = cur.lastrowid

            cur.execute(
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
    def inserir(dados: dict[str, Any]) -> int | None:
        with db_transaction(dictionary=False) as cur:
            cur.execute(
                """
                INSERT INTO produtos
                    (cod_produto, codigo_barras, nome, ncm, cest,
                     preco_compra, preco_venda, quantidade_estoque,
                     categoria_id, marca_id, fornecedor_id,
                     unidade_id, unidade_tributavel_id, ativo, imagem_path)
                VALUES
                    (%(cod_produto)s, %(codigo_barras)s, %(nome)s, %(ncm)s, %(cest)s,
                     %(preco_compra)s, %(preco_venda)s, %(quantidade_estoque)s,
                     %(categoria_id)s, %(marca_id)s, %(fornecedor_id)s,
                     %(unidade_id)s, %(unidade_tributavel_id)s, %(ativo)s, %(imagem_path)s)
                """,
                dados,
            )
            return cur.lastrowid
    @staticmethod
    def buscar_por_codigo_barras_completo(codigo: str) -> dict[str, Any] | None:
        parametros_promocoes = ConfiguracoesModel.carregar_empresa_pdv()
        ativar_por_vigencia = bool(parametros_promocoes.get("ativar_promocoes_por_vigencia", True))

        with db_cursor() as cur:
            try:
                campos_join= """
                    p.id,
                    p.cod_produto,
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
                """
                joins = """
                    FROM produtos p
                    LEFT JOIN promocao_produtos ppromo
                        On ppromo.id = (
                            SELECT pp2.id
                            FROM promocao_produtos pp2
                            INNER JOIN promocoes pr2 ON pr2.id = pp2.promocao_id
                            WHERE pp2.produto_id = p.id
                              AND pp2.ativo = 'S'
                              AND pr2.ativo = 'S'
                              AND {condicao_status}
                            ORDER BY pp2.preco_promocional ASC, pr2.data_inicio DESC, pp2.id DESC
                            LIMIT 1
                        )
                    LEFT JOIN promocoes promo ON promo.id = ppromo.promocao_id
                    LEFT JOIN categorias c ON c.id = p.categoria_id
                    LEFT JOIN marcas m ON m.id = p.marca_id
                    LEFT JOIN fornecedores f ON f.id_fornecedor = p.fornecedor_id
                    LEFT JOIN unidades_medida uc ON uc.id = p.unidade_id
                    WHERE p.codigo_barras = %s
                    LIMIT 1
                """

                if ativar_por_vigencia:
                    query = f"SELECT {campos_join} {joins.format(condicao_status='pr2.status IN (%s, %s) AND NOW() BETWEEN pr2.data_inicio AND pr2.data_fim')}"
                    parametros = (STATUS_PROMOCAO_ATIVA, STATUS_PROMOCAO_AGENDADA, codigo)
                else: 
                    query = f"SELECT {campos_join} {joins.format(condicao_status='pr2.status = %s')}"
                    parametros = (STATUS_PROMOCAO_ATIVA, codigo)

                cur.execute(query, parametros)
                resultado = cur.fetchone()
                return cast(dict[str, Any] | None, resultado)
            except Exception as e:
                log_error("Erro ao buscar produto por código de barras completo.", e)
                raise
