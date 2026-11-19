from __future__ import annotations

from typing import Any, cast

from database.connection import db_cursor, db_transaction
from modules.estoque.models.estoque_lote_model import EstoqueLoteModel
from modules.shared.constants import FLAG_SIM, TIPO_MOVIMENTACAO_SAIDA_FORNECIMENTO

class EstoqueModel:
    ESTOQUE_CRITICO_PADRAO = 5

    @staticmethod
    def listar_categorias() -> list[dict[str, Any]]:
        with db_cursor() as cur:
            cur.execute(
                """
                SELECT id, nome
                FROM categorias
                WHERE ativo = 'S'
                ORDER BY nome
                """
            )
            return cast(list[dict[str, Any]], cur.fetchall())
    @staticmethod
    def listar_fornecedores() -> list[dict[str, Any]]:
        with db_cursor() as cur:
            cur.execute(
                """
                SELECT id_fornecedor, nome_fantasia
                FROM fornecedores
                WHERE ativo = 'S'
                ORDER BY nome_fantasia
                """
            )
            return cast(list[dict[str, Any]], cur.fetchall())

    @staticmethod
    def buscar_produtos_fornecimento(termo: str, limite: int = 20) -> list[dict[str, Any]]:
        termo_limpo = str(termo or "").strip()
        if len(termo_limpo) < 2:
            return []

        with db_cursor() as cur:
            cur.execute(
                """
                SELECT
                    p.id,
                    p.codigo_barras,
                    p.cod_produto,
                    p.nome,
                    p.quantidade_estoque
                FROM produtos p
                WHERE p.ativo = 'S'
                  AND COALESCE(p.quantidade_estoque, 0) > 0
                  AND (
                      p.codigo_barras = %s
                      OR p.cod_produto = %s
                      OR p.codigo_barras LIKE %s
                      OR p.cod_produto LIKE %s
                      OR UPPER(p.nome) LIKE %s
                  )
                ORDER BY
                    CASE
                        WHEN p.codigo_barras = %s THEN 0
                        WHEN p.cod_produto = %s THEN 1
                        WHEN UPPER(p.nome) = UPPER(%s) THEN 2
                        ELSE 3
                    END,
                    p.nome
                LIMIT %s
                """,
                (
                    termo_limpo,
                    termo_limpo,
                    f"{termo_limpo}%",
                    f"{termo_limpo}%",
                    f"%{termo_limpo.upper()}%",
                    termo_limpo,
                    termo_limpo,
                    termo_limpo,
                    int(limite),
                ),
            )
            return cast(list[dict[str, Any]], cur.fetchall())

    @staticmethod
    def registrar_fornecimento(
        produto_id: int,
        cliente_id: int,
        cliente_nome: str,
        quantidade: int,
        usuario_id: int,
        observacao: str = "",
    ) -> None:
        nome_destinatario = str(cliente_nome or "").strip()
        if not nome_destinatario:
            raise ValueError("Selecione o destinatário do fornecimento.")
        if int(cliente_id) <= 0:
            raise ValueError("Destinatário inválido.")
        if int(quantidade) <= 0:
            raise ValueError("Informe uma quantidade maior que zero.")

        with db_transaction(dictionary=True) as cur:
            cur.execute(
                """
                INSERT INTO estoque_fornecimentos
                    (cliente_id, usuario_id, observacao, ativo, createdAt, updatedAt)
                VALUES (%s, %s, %s, %s, NOW(), NOW())
                """,
                (int(cliente_id), int(usuario_id), str(observacao or '').strip() or None, FLAG_SIM),
            )
            fornecimento_id = int(cur.lastrowid)
            cur.execute(
                """
                SELECT id, nome, preco_compra, preco_venda, quantidade_estoque
                FROM produtos
                WHERE id = %s AND ativo = 'S'
                FOR UPDATE
                """,
                (int(produto_id),),
            )
            produto = cur.fetchone()
            if not produto:
                raise ValueError("Produto não localizado ou inativo.")

            quantidade_fornecida = int(quantidade)
            estoque_atual = int(produto.get("quantidade_estoque") or 0)
            if quantidade_fornecida > estoque_atual:
                raise ValueError(
                    f"Estoque insuficiente. Disponível: {estoque_atual} unidade(s)."
                )

            lotes_baixados = EstoqueLoteModel.baixar_quantidade(cur, int(produto_id), quantidade_fornecida)
            observacao_final = f"Fornecimento para {nome_destinatario}"
            if str(observacao or "").strip():
                observacao_final += f" - {str(observacao).strip()}"

            for lote_id, retirada in lotes_baixados:
                cur.execute(
                    """
                    INSERT INTO movimentacao_estoque
                        (lote_id, venda_id, fornecimento_id, data_hora, tipo, quantidade, usuario_id,
                         observacao, tipo_movimento_id, ativo, createdAt, updatedAt)
                    VALUES
                        (%s, NULL, %s, NOW(), %s, %s, %s, %s, NULL, %s, NOW(), NOW())
                    """,
                    (int(lote_id), fornecimento_id, TIPO_MOVIMENTACAO_SAIDA_FORNECIMENTO, retirada, int(usuario_id), observacao_final, FLAG_SIM),
                )
                cur.execute(
                    """
                    INSERT INTO estoque_fornecimentos_itens
                        (fornecimento_id, produto_id, quantidade, createdAt, updatedAt)
                    VALUES (%s, %s, %s, NOW(), NOW())
                    """,
                    (fornecimento_id, int(produto_id), retirada),
                )

            cur.execute(
                """
                UPDATE produtos
                SET quantidade_estoque = quantidade_estoque - %s, updatedAt = NOW()
                WHERE id = %s
                """,
                (quantidade_fornecida, int(produto_id)),
            )
    @staticmethod
    def obter_metricas() -> dict[str, int]:
        with db_cursor() as cur:
            cur.execute(
                """
                SELECT COUNT(*) AS total
                FROM produtos
                WHERE ativo = 'S'
                """
            )
            produtos = cast(dict[str, Any], cur.fetchone() or {})

            cur.execute(
                """
                SELECT COUNT(*) AS total
                FROM lotes
                WHERE ativo = 'S'
                  AND quantidade > 0
                """
            )
            lotes = cast(dict[str, Any], cur.fetchone() or {})

            cur.execute(
                """
                SELECT COUNT(*) AS total
                FROM produtos
                WHERE ativo = 'S'
                  AND quantidade_estoque <= %s
                """,
                (EstoqueModel.ESTOQUE_CRITICO_PADRAO,),
            )
            critico = cast(dict[str, Any], cur.fetchone() or {})

            cur.execute(
                """
                SELECT COUNT(*) AS total
                FROM movimentacao_estoque
                WHERE ativo = 'S'
                  AND DATE(data_hora) = CURDATE()
                """
            )
            movimentacoes = cast(dict[str, Any], cur.fetchone() or {})

            return {
                "produtos_ativos": int(produtos.get("total") or 0),
                "lotes_ativos": int(lotes.get("total") or 0),
                "estoque_critico": int(critico.get("total") or 0),
                "movimentacoes_dia": int(movimentacoes.get("total") or 0),
            }
    @staticmethod
    def listar_produtos_lotes(
        *,
        busca: str = "",
        categoria_id: int | None = None,
        fornecedor_id: int | None = None,
        pagina: int | None = None,
        por_pagina: int = 50,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        with db_cursor() as cur:
            where: list[str] = ["p.ativo = 'S'"]
            params: list[Any] = []

            busca_limpa = str(busca or "").strip()
            if busca_limpa:
                termo = f"%{busca_limpa}%"
                where.append(
                    """
                    (
                        p.nome LIKE %s
                        OR p.codigo_barras LIKE %s
                        OR COALESCE(l.numero_lote, '') LIKE %s
                        OR COALESCE(m.nome_marca, '') LIKE %s
                    )
                    """
                )
                params.extend([termo, termo, termo, termo])

            if categoria_id:
                where.append("p.categoria_id = %s")
                params.append(int(categoria_id))

            if fornecedor_id:
                where.append("p.fornecedor_id = %s")
                params.append(int(fornecedor_id))

            where_sql = " AND ".join(where)
            total = None
            pagina_segura = None
            limite = None
            offset = None
            if pagina is not None:
                cur.execute(
                    f"""
                    SELECT COUNT(*) AS total
                    FROM produtos p
                    LEFT JOIN categorias c ON c.id = p.categoria_id
                    LEFT JOIN marcas m ON m.id = p.marca_id
                    LEFT JOIN lotes l
                        ON l.produto_id = p.id
                       AND l.ativo = 'S'
                    WHERE {where_sql}
                    """,
                    tuple(params),
                )
                total = int((cur.fetchone() or {}).get("total") or 0)
                pagina_segura = max(1, int(pagina))
                limite = max(1, int(por_pagina))
                offset = (pagina_segura - 1) * limite

            sql = f"""
                SELECT
                    p.id,
                    p.codigo_barras,
                    p.nome,
                    COALESCE(c.nome, '-') AS categoria,
                    COALESCE(m.nome_marca, '-') AS marca,
                    COALESCE(l.numero_lote, '-') AS lote,
                    l.data_validade,
                    COALESCE(l.quantidade, p.quantidade_estoque, 0) AS quantidade,
                    COALESCE(l.preco_venda, p.preco_venda, 0) AS preco_venda
                FROM produtos p
                LEFT JOIN categorias c ON c.id = p.categoria_id
                LEFT JOIN marcas m ON m.id = p.marca_id
                LEFT JOIN lotes l
                    ON l.produto_id = p.id
                   AND l.ativo = 'S'
                WHERE {where_sql}
                ORDER BY p.nome, l.data_validade, l.numero_lote
            """
            parametros = list(params)
            if pagina is not None:
                sql += " LIMIT %s OFFSET %s"
                parametros.extend([limite, offset])
            cur.execute(sql, tuple(parametros))
            registros = cast(list[dict[str, Any]], cur.fetchall())
            if pagina is None:
                return registros
            return {
                "registros": registros,
                "total": total,
                "pagina": pagina_segura,
                "por_pagina": limite,
            }
    @staticmethod
    def listar_movimentacoes_recentes(
        limite: int = 20,
        tipos: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        with db_cursor() as cur:
            filtro_tipos = ""
            parametros: list[Any] = []
            if tipos:
                placeholders = ", ".join(["%s"] * len(tipos))
                filtro_tipos = f" AND me.tipo IN ({placeholders})"
                parametros.extend(tipos)
            parametros.append(int(limite))
            cur.execute(
                f"""
                SELECT
                    me.id,
                    me.data_hora,
                    COALESCE(p.nome, '-') AS produto,
                    me.tipo,
                    me.quantidade,
                    me.observacao,
                    COALESCE(u.nome, '-') AS usuario
                FROM movimentacao_estoque me
                LEFT JOIN lotes l ON l.id = me.lote_id
                LEFT JOIN produtos p ON p.id = l.produto_id
                LEFT JOIN usuarios u ON u.id = me.usuario_id
                WHERE me.ativo = 'S'
                  {filtro_tipos}
                ORDER BY me.data_hora DESC, me.id DESC
                LIMIT %s
                """,
                tuple(parametros),
            )
            return cast(list[dict[str, Any]], cur.fetchall())

    @staticmethod
    def listar_fornecimentos_recentes(limite: int = 20) -> list[dict[str, Any]]:
        with db_cursor() as cur:
            cur.execute(
                """
                SELECT
                    me.id,
                    me.data_hora,
                    COALESCE(p.nome, '-') AS produto,
                    me.quantidade,
                    me.observacao,
                    COALESCE(c.nome, '-') AS destinatario,
                    COALESCE(u.nome, '-') AS usuario
                FROM movimentacao_estoque me
                LEFT JOIN lotes l ON l.id = me.lote_id
                LEFT JOIN produtos p ON p.id = l.produto_id
                LEFT JOIN estoque_fornecimentos ef ON ef.id = me.fornecimento_id
                LEFT JOIN clientes c ON c.id = ef.cliente_id
                LEFT JOIN usuarios u ON u.id = me.usuario_id
                WHERE me.ativo = 'S'
                  AND me.tipo = %s
                ORDER BY me.data_hora DESC, me.id DESC
                LIMIT %s
                """,
                (TIPO_MOVIMENTACAO_SAIDA_FORNECIMENTO, int(limite)),
            )
            return cast(list[dict[str, Any]], cur.fetchall())
