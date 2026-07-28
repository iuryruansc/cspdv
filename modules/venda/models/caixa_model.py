from __future__ import annotations

from typing import Any, cast

from database.connection import db_cursor, db_transaction
from modules.shared.constants import (
    FLAG_SIM,
    STATUS_CAIXA_ABERTO,
    STATUS_CAIXA_FECHADO,
    STATUS_PDV_ATIVO,
    STATUS_REEMBOLSO_CONCLUIDO,
)

class CaixaModel:
    _TIPOS_MOVIMENTACAO = {
        "sangria": "Sangria",
        "suprimento": "Suprimento",
        "troco": "Reforco de Troco",
    }

    @staticmethod
    def listar_pdvs_ativos() -> list[dict[str, Any]]:
        with db_cursor() as cur:
            cur.execute(
                """
                SELECT id, identificacao, descricao
                FROM pdvs
                WHERE ativo = %s AND status = %s
                ORDER BY identificacao
                """,
                (FLAG_SIM, STATUS_PDV_ATIVO),
            )
            return cast(list[dict[str, Any]], cur.fetchall())
    @staticmethod
    def buscar_caixa_aberto_por_pdv(pdv_id: int) -> dict[str, Any] | None:
        with db_cursor() as cur:
            cur.execute(
                """
                SELECT id, pdv_id, usuario_abertura_id, data_abertura, valor_abertura, status
                FROM caixas
                WHERE pdv_id = %s AND status = %s AND ativo = %s
                ORDER BY data_abertura DESC
                LIMIT 1
                """,
                (pdv_id, STATUS_CAIXA_ABERTO, FLAG_SIM),
            )
            return cast(dict[str, Any] | None, cur.fetchone())
    @staticmethod
    def buscar_caixa_aberto_por_usuario(usuario_id: int) -> dict[str, Any] | None:
        with db_cursor() as cur:
            cur.execute(
                """
                SELECT
                    c.id,
                    c.pdv_id,
                    c.usuario_abertura_id,
                    c.data_abertura,
                    c.valor_abertura,
                    c.status,
                    p.identificacao,
                    p.descricao,
                    u.nome AS usuario_nome
                FROM caixas c
                INNER JOIN pdvs p ON p.id = c.pdv_id
                INNER JOIN usuarios u ON u.id = c.usuario_abertura_id
                WHERE c.usuario_abertura_id = %s
                  AND c.status = %s
                  AND c.ativo = %s
                ORDER BY c.data_abertura DESC
                LIMIT 1
                """,
                (usuario_id, STATUS_CAIXA_ABERTO, FLAG_SIM),
            )
            return cast(dict[str, Any] | None, cur.fetchone())
    @staticmethod
    def buscar_caixa_por_id(caixa_id: int) -> dict[str, Any] | None:
        with db_cursor() as cur:
            cur.execute(
                """
                SELECT
                    c.id,
                    c.pdv_id,
                    c.usuario_abertura_id,
                    c.data_abertura,
                    c.valor_abertura,
                    c.status,
                    p.identificacao,
                    p.descricao,
                    u.nome AS usuario_nome
                FROM caixas c
                INNER JOIN pdvs p ON p.id = c.pdv_id
                INNER JOIN usuarios u ON u.id = c.usuario_abertura_id
                WHERE c.id = %s
                LIMIT 1
                """,
                (caixa_id,),
            )
            return cast(dict[str, Any] | None, cur.fetchone())
    @staticmethod
    def abrir_caixa(
        pdv_id: int,
        usuario_id: int,
        valor_abertura: float,
    ) -> int:
        with db_transaction(dictionary=False) as cur:
            cur.execute(
                """
                INSERT INTO caixas
                    (pdv_id, usuario_abertura_id, data_abertura, valor_abertura,
                     status, usuario_fechamento_id, ativo, createdAt, updatedAt)
                VALUES
                    (%s, %s, NOW(), %s, %s, %s, %s, NOW(), NOW())
                """,
                (pdv_id, usuario_id, valor_abertura, STATUS_CAIXA_ABERTO, usuario_id, FLAG_SIM),
            )
            lastrowid = cur.lastrowid
            if lastrowid is None:
                raise RuntimeError("Não foi possível obter o ID da abertura de caixa criada.")
            return int(lastrowid)
    @staticmethod
    def listar_ultimas_aberturas(limit: int = 10) -> list[dict[str, Any]]:
        with db_cursor() as cur:
            cur.execute(
                """
                SELECT
                    DATE_FORMAT(c.data_abertura, '%d/%m %H:%i') AS data_abertura_fmt,
                    u.nome AS operador,
                    c.valor_abertura
                FROM caixas c
                INNER JOIN usuarios u ON u.id = c.usuario_abertura_id
                ORDER BY c.data_abertura DESC
                LIMIT %s
                """,
                (limit,),
            )
            return cast(list[dict[str, Any]], cur.fetchall())
    @staticmethod
    def listar_caixas_admin(limit: int = 120) -> list[dict[str, Any]]:
        with db_cursor() as cur:
            cur.execute(
                """
                SELECT
                    c.id,
                    c.pdv_id,
                    p.identificacao,
                    p.descricao,
                    ua.nome AS operador_abertura,
                    c.data_abertura,
                    c.data_fechamento,
                    c.valor_abertura,
                    c.valor_fechamento,
                    c.diferenca_fechamento,
                    c.status,
                    COALESCE(c.ativo, %s) AS ativo
                FROM caixas c
                INNER JOIN pdvs p ON p.id = c.pdv_id
                INNER JOIN usuarios ua ON ua.id = c.usuario_abertura_id
                ORDER BY c.data_abertura DESC, c.id DESC
                LIMIT %s
                """,
                (FLAG_SIM, limit),
            )
            return cast(list[dict[str, Any]], cur.fetchall())
    @staticmethod
    def fechar_caixa(
        caixa_id: int,
        usuario_fechamento_id: int,
        valor_fechamento: float,
        diferenca: float,
        observacoes: str,
    ) -> None:
        with db_transaction(dictionary=False) as cur:
            cur.execute(
                """
                UPDATE caixas
                SET
                    status = %s,
                    usuario_fechamento_id = %s,
                    data_fechamento = NOW(),
                    valor_fechamento = %s,
                    diferenca_fechamento = %s,
                    observacoes_fechamento = %s,
                    updatedAt = NOW()
                WHERE id = %s
                """,
                (
                    STATUS_CAIXA_FECHADO,
                    usuario_fechamento_id,
                    valor_fechamento,
                    diferenca,
                    observacoes or "",
                    caixa_id,
                ),
            )
    @staticmethod
    def obter_resumo_operacional(caixa_id: int) -> dict[str, Any]:
        from modules.venda.models.venda_model import VendaModel

        return VendaModel.obter_resumo_por_caixa(caixa_id)

    @staticmethod
    def registrar_movimentacao(
        *,
        caixa_id: int,
        usuario_id: int,
        tipo: str,
        valor: float,
        observacao: str,
    ) -> None:
        with db_transaction(dictionary=False) as cur:
            forma_pagamento_id = CaixaModel._garantir_forma_pagamento_dinheiro(cur)
            caixa_motivo_id = CaixaModel._garantir_caixa_motivo(cur, tipo)

            cur.execute(
                """
                INSERT INTO caixa_movimentacoes
                    (caixa_id, usuario_id, caixa_motivo_id, valor, data_hora, forma_pagamento_id, observacao, estornado, createdAt, updatedAt, ativo)
                VALUES
                    (%s, %s, %s, %s, NOW(), %s, %s, 0, NOW(), NOW(), 'S')
                """,
                (
                    caixa_id,
                    usuario_id,
                    caixa_motivo_id,
                    valor,
                    forma_pagamento_id,
                    observacao or None,
                ),
            )
    @staticmethod
    def listar_movimentacoes(caixa_id: int, tipo: str | None = None) -> list[dict[str, Any]]:
        with db_cursor() as cur:
            parametros: list[Any] = [caixa_id]
            filtro_tipo = ""
            if tipo and tipo.lower() != "todas":
                filtro_tipo = "AND LOWER(cm_tipo.tipo_padrao) = %s"
                parametros.append(tipo.lower())

            cur.execute(
                f"""
                SELECT
                    DATE_FORMAT(cm.data_hora, '%H:%i') AS hora_fmt,
                    COALESCE(cm_tipo.descricao, 'Movimentacao') AS tipo_descricao,
                    COALESCE(u.nome, 'Operador') AS operador,
                    cm.valor,
                    cm.observacao,
                    COALESCE(cm_tipo.tipo_padrao, '') AS tipo_padrao
                FROM caixa_movimentacoes cm
                LEFT JOIN caixa_motivos cm_tipo ON cm_tipo.id = cm.caixa_motivo_id
                LEFT JOIN usuarios u ON u.id = cm.usuario_id
                WHERE cm.caixa_id = %s
                  AND COALESCE(cm.ativo, %s) = %s
                  AND COALESCE(cm.estornado, 0) = 0
                  {filtro_tipo}
                ORDER BY cm.data_hora DESC, cm.id DESC
                """,
                (caixa_id, FLAG_SIM, FLAG_SIM, *tuple(parametros[1:])),
            )
            return cast(list[dict[str, Any]], cur.fetchall())
    @staticmethod
    def obter_resumo_movimentacoes(caixa_id: int) -> dict[str, float]:
        with db_cursor() as cur:
            cur.execute(
                """
                SELECT
                    LOWER(COALESCE(cm_tipo.tipo_padrao, '')) AS tipo_padrao,
                    COALESCE(SUM(cm.valor), 0) AS total
                FROM caixa_movimentacoes cm
                LEFT JOIN caixa_motivos cm_tipo ON cm_tipo.id = cm.caixa_motivo_id
                WHERE cm.caixa_id = %s
                  AND COALESCE(cm.ativo, %s) = %s
                  AND COALESCE(cm.estornado, 0) = 0
                GROUP BY LOWER(COALESCE(cm_tipo.tipo_padrao, ''))
                """,
                (caixa_id, FLAG_SIM, FLAG_SIM),
            )
            totais_rows = cast(list[dict[str, Any]], cur.fetchall())
            totais = {
                str(row.get("tipo_padrao") or ""): float(row.get("total") or 0.0)
                for row in totais_rows
            }
            total_sangrias = totais.get("sangria", 0.0)
            total_suprimentos = totais.get("suprimento", 0.0)
            total_troco = totais.get("troco", 0.0)
            return {
                "total_sangrias": total_sangrias,
                "total_suprimentos": total_suprimentos,
                "total_troco": total_troco,
                "total_entradas_manuais": total_suprimentos + total_troco,
            }
    @staticmethod
    def obter_total_reembolsos(caixa_id: int) -> float:
        with db_cursor() as cur:
            cur.execute(
                """
                SELECT COALESCE(SUM(vr.valor_total), 0) AS total
                FROM venda_reembolsos vr
                INNER JOIN vendas v ON v.id = vr.venda_id
                WHERE v.caixa_id = %s
                  AND vr.ativo = %s
                  AND vr.status = %s
                """,
                (caixa_id, FLAG_SIM, STATUS_REEMBOLSO_CONCLUIDO),
            )
            row = cast(dict[str, Any], cur.fetchone() or {})
            return float(row.get("total") or 0.0)
    @staticmethod
    def _garantir_forma_pagamento_dinheiro(cursor) -> int:
        cursor.execute(
            """
            SELECT id
            FROM formas_pagamento
            WHERE UPPER(nome) = 'DINHEIRO'
            LIMIT 1
            """
        )
        row = cursor.fetchone()
        if row:
            return int(row[0])

        cursor.execute(
            """
            INSERT INTO formas_pagamento
                (nome, tipo_sefaz, permite_parcelamento, taxa_administrativa, ativo)
            VALUES
                ('Dinheiro', '01', 'N', 0.00, 'S')
            """
        )
        forma_pagamento_id = cursor.lastrowid
        if forma_pagamento_id is None:
            raise RuntimeError("Não foi possível criar a forma de pagamento Dinheiro.")
        return int(forma_pagamento_id)

    @staticmethod
    def _garantir_caixa_motivo(cursor, tipo: str) -> int:
        tipo_normalizado = str(tipo or "").strip().lower()
        if tipo_normalizado not in CaixaModel._TIPOS_MOVIMENTACAO:
            raise ValueError("Tipo de movimentação inválido.")

        descricao = CaixaModel._TIPOS_MOVIMENTACAO[tipo_normalizado]
        cursor.execute(
            """
            SELECT id
            FROM caixa_motivos
            WHERE LOWER(tipo_padrao) = %s
            LIMIT 1
            """,
            (tipo_normalizado,),
        )
        row = cursor.fetchone()
        if row:
            return int(row[0])

        cursor.execute(
            """
            INSERT INTO caixa_motivos
                (descricao, tipo_padrao, ativo, createdAt, updatedAt)
            VALUES
                (%s, %s, 'S', NOW(), NOW())
            """,
            (descricao, tipo_normalizado),
        )
        motivo_id = cursor.lastrowid
        if motivo_id is None:
            raise RuntimeError("Não foi possível criar o motivo de caixa.")
        return int(motivo_id)
