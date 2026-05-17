from __future__ import annotations

from typing import Any, Dict, List, cast

from database.connection import get_connection
from modules.shared.constants import (
    FLAG_SIM,
    STATUS_PROMOCAO_AGENDADA,
    STATUS_PROMOCAO_ATIVA,
    STATUS_PROMOCAO_RASCUNHO,
)

class PromocaoModel:
    @staticmethod
    def gerar_proximo_codigo() -> str:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT COALESCE(MAX(id), 0) AS ultimo_id FROM promocoes")
            row = cast(Dict[str, Any], cursor.fetchone() or {})
            proximo = int(row.get("ultimo_id") or 0) + 1
            return f"PR-{proximo:03d}"
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def inserir(dados: dict[str, Any]) -> int | None:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO promocoes
                    (codigo, nome, classificacao, tipo_desconto, status, descricao, observacao,
                     desconto_percentual, desconto_valor, preco_fixo, data_inicio, data_fim,
                     cumulativa, aplica_em_todos_pdvs, ativo, usuario_id, createdAt, updatedAt)
                VALUES
                    (%(codigo)s, %(nome)s, %(classificacao)s, %(tipo_desconto)s, %(status)s, %(descricao)s, %(observacao)s,
                     %(desconto_percentual)s, %(desconto_valor)s, %(preco_fixo)s, %(data_inicio)s, %(data_fim)s,
                     %(cumulativa)s, 'S', %(ativo)s, %(usuario_id)s, NOW(), NOW())
                """,
                dados,
            )
            conn.commit()
            return int(cursor.lastrowid or 0)
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def atualizar(promocao_id: int, dados: dict[str, Any]) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT 1 FROM promocoes WHERE id = %s LIMIT 1", (int(promocao_id),))
            if not cursor.fetchone():
                return False

            payload = dict(dados)
            payload["id"] = int(promocao_id)
            cursor.execute(
                """
                UPDATE promocoes
                SET codigo = %(codigo)s,
                    nome = %(nome)s,
                    classificacao = %(classificacao)s,
                    tipo_desconto = %(tipo_desconto)s,
                    status = %(status)s,
                    descricao = %(descricao)s,
                    observacao = %(observacao)s,
                    desconto_percentual = %(desconto_percentual)s,
                    desconto_valor = %(desconto_valor)s,
                    preco_fixo = %(preco_fixo)s,
                    data_inicio = %(data_inicio)s,
                    data_fim = %(data_fim)s,
                    cumulativa = %(cumulativa)s,
                    ativo = %(ativo)s,
                    updatedAt = NOW()
                WHERE id = %(id)s
                """,
                payload,
            )
            conn.commit()
            return True
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def duplicar(promocao_id: int, novo_codigo: str) -> int | None:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    codigo,
                    nome,
                    classificacao,
                    tipo_desconto,
                    descricao,
                    observacao,
                    desconto_percentual,
                    desconto_valor,
                    preco_fixo,
                    data_inicio,
                    data_fim,
                    cumulativa,
                    ativo,
                    usuario_id
                FROM promocoes
                WHERE id = %s
                LIMIT 1
                """,
                (int(promocao_id),),
            )
            promocao = cast(Dict[str, Any], cursor.fetchone() or {})
            if not promocao:
                return None

            data_inicio = promocao.get("data_inicio")
            data_fim = promocao.get("data_fim")

            cursor.execute(
                """
                INSERT INTO promocoes
                    (codigo, nome, classificacao, tipo_desconto, status, descricao, observacao,
                     desconto_percentual, desconto_valor, preco_fixo, data_inicio, data_fim,
                     cumulativa, aplica_em_todos_pdvs, ativo, usuario_id, createdAt, updatedAt)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s,
                     %s, %s, %s, %s, %s,
                     %s, %s, %s, %s, NOW(), NOW())
                """,
                (
                    str(novo_codigo).strip().upper(),
                    str(promocao.get("nome") or ""),
                    str(promocao.get("classificacao") or "PROMOCAO"),
                    str(promocao.get("tipo_desconto") or "PERCENTUAL"),
                    STATUS_PROMOCAO_RASCUNHO,
                    str(promocao.get("descricao") or ""),
                    str(promocao.get("observacao") or ""),
                    float(promocao.get("desconto_percentual") or 0),
                    float(promocao.get("desconto_valor") or 0),
                    float(promocao.get("preco_fixo") or 0),
                    data_inicio,
                    data_fim,
                    str(promocao.get("cumulativa") or "N"),
                    FLAG_SIM,
                    str(promocao.get("ativo") or FLAG_SIM),
                    int(promocao.get("usuario_id") or 0),
                ),
            )
            novo_id = int(cursor.lastrowid or 0)
            if novo_id <= 0:
                conn.rollback()
                return None

            cursor.execute(
                """
                INSERT INTO promocao_produtos
                    (promocao_id, produto_id, preco_original, preco_promocional, desconto_aplicado, observacao, ativo, createdAt, updatedAt)
                SELECT
                    %s,
                    produto_id,
                    preco_original,
                    preco_promocional,
                    desconto_aplicado,
                    observacao,
                    ativo,
                    NOW(),
                    NOW()
                FROM promocao_produtos
                WHERE promocao_id = %s
                  AND ativo = %s
                """,
                (novo_id, int(promocao_id), FLAG_SIM),
            )
            conn.commit()
            return novo_id
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def atualizar_status(promocao_id: int, status: str) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                UPDATE promocoes
                SET status = %s,
                    updatedAt = NOW()
                WHERE id = %s
                """,
                (str(status).strip().upper(), int(promocao_id)),
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
    def listar(*, busca: str = "", status: str = "", tipo: str = "") -> list[dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            filtros = ["1=1"]
            params: list[Any] = []

            busca_limpa = busca.strip()
            if busca_limpa:
                filtros.append(
                    """
                    (
                        p.codigo LIKE %s OR
                        p.nome LIKE %s OR
                        p.classificacao LIKE %s OR
                        p.tipo_desconto LIKE %s OR
                        COALESCE(pp.produtos_texto, '') LIKE %s
                    )
                    """
                )
                termo = f"%{busca_limpa}%"
                params.extend([termo, termo, termo, termo, termo])

            if status and status.upper() != "TODOS OS STATUS":
                filtros.append("p.status = %s")
                params.append(status.upper())

            if tipo and tipo.upper() != "TODOS OS TIPOS":
                mapa_tipo = {
                    "DESCONTO POR PERCENTUAL": "PERCENTUAL",
                    "DESCONTO POR VALOR": "VALOR",
                    "PRECO PROMOCIONAL": "PRECO_FIXO",
                }
                filtros.append("p.tipo_desconto = %s")
                params.append(mapa_tipo.get(tipo.upper(), tipo.upper()))

            cursor.execute(
                f"""
                SELECT
                    p.id,
                    p.codigo,
                    p.nome,
                    p.classificacao,
                    p.tipo_desconto,
                    p.status,
                    DATE_FORMAT(p.data_inicio, '%d/%m/%Y %H:%i') AS data_inicio_fmt,
                    DATE_FORMAT(p.data_fim, '%d/%m/%Y %H:%i') AS data_fim_fmt,
                    CONCAT(
                        DATE_FORMAT(p.data_inicio, '%d/%m/%Y'),
                        ' a ',
                        DATE_FORMAT(p.data_fim, '%d/%m/%Y')
                    ) AS vigencia,
                    COUNT(DISTINCT pp2.produto_id) AS qtd_produtos,
                    CASE
                        WHEN COUNT(DISTINCT pp2.produto_id) > 0 THEN CONCAT(COUNT(DISTINCT pp2.produto_id), ' produtos')
                        ELSE 'Sem produtos vinculados'
                    END AS alcance,
                    p.desconto_percentual,
                    p.desconto_valor,
                    p.preco_fixo
                FROM promocoes p
                LEFT JOIN promocao_produtos pp2 ON pp2.promocao_id = p.id AND pp2.ativo = %s
                LEFT JOIN (
                    SELECT
                        pp.promocao_id,
                        GROUP_CONCAT(pr.nome SEPARATOR ' | ') AS produtos_texto
                    FROM promocao_produtos pp
                    INNER JOIN produtos pr ON pr.id = pp.produto_id
                    WHERE pp.ativo = %s
                    GROUP BY pp.promocao_id
                ) pp ON pp.promocao_id = p.id
                WHERE {" AND ".join(filtros)}
                GROUP BY
                    p.id, p.codigo, p.nome, p.classificacao, p.tipo_desconto, p.status,
                    p.data_inicio, p.data_fim, p.desconto_percentual, p.desconto_valor, p.preco_fixo
                ORDER BY p.data_inicio DESC, p.id DESC
                """,
                [FLAG_SIM, FLAG_SIM, *params],
            )
            return cast(List[Dict[str, Any]], list(cursor.fetchall() or []))
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def listar_itens_promocao(promocao_id: int) -> list[dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    pp.produto_id,
                    pr.nome AS produto,
                    pp.preco_original,
                    pp.preco_promocional,
                    pp.desconto_aplicado,
                    COALESCE(pp.observacao, '') AS observacao
                FROM promocao_produtos pp
                INNER JOIN produtos pr ON pr.id = pp.produto_id
                WHERE pp.promocao_id = %s AND pp.ativo = %s
                ORDER BY pr.nome
                """,
                (int(promocao_id), FLAG_SIM),
            )
            return cast(List[Dict[str, Any]], list(cursor.fetchall() or []))
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def buscar_por_id(promocao_id: int) -> dict[str, Any] | None:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    id,
                    codigo,
                    nome,
                    classificacao,
                    tipo_desconto,
                    status,
                    descricao,
                    observacao,
                    desconto_percentual,
                    desconto_valor,
                    preco_fixo,
                    data_inicio,
                    data_fim,
                    cumulativa,
                    ativo
                FROM promocoes
                WHERE id = %s
                LIMIT 1
                """,
                (int(promocao_id),),
            )
            return cast(Dict[str, Any] | None, cursor.fetchone())
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def buscar_produtos_disponiveis(promocao_id: int, busca: str = "") -> list[dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            filtros = ["p.ativo = %s"]
            params: list[Any] = [int(promocao_id)]

            termo = str(busca or "").strip()
            if termo:
                termo_like = f"%{termo}%"
                filtros.append(
                    """
                    (
                        p.codigo_barras LIKE %s OR
                        p.nome LIKE %s OR
                        COALESCE(m.nome_marca, '') LIKE %s OR
                        COALESCE(c.nome, '') LIKE %s
                    )
                    """
                )
                params.extend([termo_like, termo_like, termo_like, termo_like])

            cursor.execute(
                f"""
                SELECT
                    p.id,
                    p.codigo_barras,
                    p.nome,
                    p.preco_venda,
                    p.quantidade_estoque,
                    COALESCE(m.nome_marca, '-') AS marca,
                    COALESCE(c.nome, '-') AS categoria,
                    CASE
                        WHEN pp.id IS NULL THEN 'N'
                        ELSE 'S'
                    END AS vinculado
                FROM produtos p
                LEFT JOIN marcas m ON m.id = p.marca_id
                LEFT JOIN categorias c ON c.id = p.categoria_id
                LEFT JOIN promocao_produtos pp
                    ON pp.promocao_id = %s
                   AND pp.produto_id = p.id
                   AND pp.ativo = %s
                WHERE {" AND ".join(filtros)}
                ORDER BY
                    CASE WHEN pp.id IS NULL THEN 1 ELSE 0 END,
                    p.nome
                LIMIT 150
                """,
                [int(promocao_id), FLAG_SIM, *params, FLAG_SIM],
            )
            return cast(List[Dict[str, Any]], list(cursor.fetchall() or []))
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def buscar_conflito_produto_ativo(promocao_id: int, produto_id: int) -> dict[str, Any] | None:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    p.id,
                    p.codigo,
                    p.nome,
                    p.status,
                    DATE_FORMAT(p.data_inicio, '%d/%m/%Y %H:%i') AS data_inicio_fmt,
                    DATE_FORMAT(p.data_fim, '%d/%m/%Y %H:%i') AS data_fim_fmt
                FROM promocao_produtos pp
                INNER JOIN promocoes p
                    ON p.id = pp.promocao_id
                INNER JOIN promocoes atual
                    ON atual.id = %s
                WHERE pp.produto_id = %s
                  AND pp.ativo = %s
                  AND p.id <> %s
                  AND p.ativo = %s
                  AND p.status IN (%s, %s)
                  AND atual.data_inicio <= p.data_fim
                  AND atual.data_fim >= p.data_inicio
                ORDER BY
                    CASE p.status WHEN %s THEN 0 ELSE 1 END,
                    p.data_inicio,
                    p.id
                LIMIT 1
                """,
                (
                    int(promocao_id),
                    int(produto_id),
                    FLAG_SIM,
                    int(promocao_id),
                    FLAG_SIM,
                    STATUS_PROMOCAO_AGENDADA,
                    STATUS_PROMOCAO_ATIVA,
                    STATUS_PROMOCAO_ATIVA,
                ),
            )
            return cast(Dict[str, Any] | None, cursor.fetchone())
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def salvar_vinculo_produto(
        promocao_id: int,
        produto_id: int,
        preco_original: float,
        preco_promocional: float,
        desconto_aplicado: float,
        observacao: str,
    ) -> None:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT id
                FROM promocao_produtos
                WHERE promocao_id = %s AND produto_id = %s
                LIMIT 1
                """,
                (int(promocao_id), int(produto_id)),
            )
            existente = cast(Dict[str, Any], cursor.fetchone() or {})

            if existente:
                cursor.execute(
                    """
                    UPDATE promocao_produtos
                    SET preco_original = %s,
                        preco_promocional = %s,
                        desconto_aplicado = %s,
                        observacao = %s,
                        ativo = %s,
                        updatedAt = NOW()
                    WHERE id = %s
                    """,
                    (
                        preco_original,
                        preco_promocional,
                        desconto_aplicado,
                        observacao or None,
                        FLAG_SIM,
                        int(existente.get("id") or 0),
                    ),
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO promocao_produtos
                        (promocao_id, produto_id, preco_original, preco_promocional, desconto_aplicado, observacao, ativo, createdAt, updatedAt)
                    VALUES
                        (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                    """,
                    (
                        int(promocao_id),
                        int(produto_id),
                        preco_original,
                        preco_promocional,
                        desconto_aplicado,
                        observacao or None,
                        FLAG_SIM,
                    ),
                )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def desativar_vinculo_produto(promocao_id: int, produto_id: int) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                UPDATE promocao_produtos
                SET ativo = 'N',
                    updatedAt = NOW()
                WHERE promocao_id = %s
                  AND produto_id = %s
                  AND ativo = %s
                """,
                (int(promocao_id), int(produto_id), FLAG_SIM),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()
