from __future__ import annotations

from typing import Any

from database.connection import get_connection


class PromocaoModel:
    @staticmethod
    def gerar_proximo_codigo() -> str:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT COALESCE(MAX(id), 0) AS ultimo_id FROM promocoes")
            row = cursor.fetchone() or {}
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
                    DATE_FORMAT(p.data_inicio, '%%d/%%m/%%Y %%H:%%i') AS data_inicio_fmt,
                    DATE_FORMAT(p.data_fim, '%%d/%%m/%%Y %%H:%%i') AS data_fim_fmt,
                    CONCAT(
                        DATE_FORMAT(p.data_inicio, '%%d/%%m/%%Y'),
                        ' a ',
                        DATE_FORMAT(p.data_fim, '%%d/%%m/%%Y')
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
                LEFT JOIN promocao_produtos pp2 ON pp2.promocao_id = p.id AND pp2.ativo = 'S'
                LEFT JOIN (
                    SELECT
                        pp.promocao_id,
                        GROUP_CONCAT(pr.nome SEPARATOR ' | ') AS produtos_texto
                    FROM promocao_produtos pp
                    INNER JOIN produtos pr ON pr.id = pp.produto_id
                    WHERE pp.ativo = 'S'
                    GROUP BY pp.promocao_id
                ) pp ON pp.promocao_id = p.id
                WHERE {" AND ".join(filtros)}
                GROUP BY
                    p.id, p.codigo, p.nome, p.classificacao, p.tipo_desconto, p.status,
                    p.data_inicio, p.data_fim, p.desconto_percentual, p.desconto_valor, p.preco_fixo
                ORDER BY p.data_inicio DESC, p.id DESC
                """,
                params,
            )
            return list(cursor.fetchall() or [])
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
                    pr.nome AS produto,
                    pp.preco_original,
                    pp.preco_promocional,
                    pp.desconto_aplicado,
                    COALESCE(pp.observacao, '') AS observacao
                FROM promocao_produtos pp
                INNER JOIN produtos pr ON pr.id = pp.produto_id
                WHERE pp.promocao_id = %s AND pp.ativo = 'S'
                ORDER BY pr.nome
                """,
                (int(promocao_id),),
            )
            return list(cursor.fetchall() or [])
        finally:
            cursor.close()
            conn.close()
