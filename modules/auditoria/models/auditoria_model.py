from __future__ import annotations

from typing import Any, cast

from database.connection import db_cursor, db_transaction

class AuditoriaModel:
    @staticmethod
    def registrar_evento(
        *,
        evento: str,
        categoria: str,
        entidade: str | None,
        entidade_id: int | None,
        usuario_id: int | None,
        caixa_id: int | None,
        detalhes_json: str | None,
    ) -> None:
        with db_transaction(dictionary=False) as cur:
            cur.execute(
                """
                INSERT INTO auditoria_eventos
                    (evento, categoria, entidade, entidade_id, usuario_id, caixa_id, detalhes_json, createdAt)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s, NOW())
                """,
                (
                    evento,
                    categoria,
                    entidade,
                    entidade_id,
                    usuario_id,
                    caixa_id,
                    detalhes_json,
                ),
            )
    @staticmethod
    def listar(limit: int = 300) -> list[dict[str, Any]]:
        with db_cursor() as cur:
            cur.execute(
                """
                SELECT
                    ae.id,
                    ae.createdAt AS data_hora,
                    ae.categoria,
                    ae.evento,
                    ae.entidade,
                    ae.entidade_id,
                    ae.usuario_id,
                    ae.caixa_id,
                    COALESCE(u.nome, '-') AS usuario_nome
                FROM auditoria_eventos ae
                LEFT JOIN usuarios u ON u.id = ae.usuario_id
                ORDER BY ae.createdAt DESC, ae.id DESC
                LIMIT %s
                """,
                (int(limit),),
            )
            return cast(list[dict[str, Any]], cur.fetchall())
    @staticmethod
    def buscar_por_id(evento_id: int) -> dict[str, Any] | None:
        with db_cursor() as cur:
            cur.execute(
                """
                SELECT
                    ae.id,
                    ae.createdAt AS data_hora,
                    ae.categoria,
                    ae.evento,
                    ae.entidade,
                    ae.entidade_id,
                    ae.usuario_id,
                    ae.caixa_id,
                    ae.detalhes_json,
                    COALESCE(u.nome, '-') AS usuario_nome,
                    COALESCE(p.identificacao, '-') AS pdv_identificacao
                FROM auditoria_eventos ae
                LEFT JOIN usuarios u ON u.id = ae.usuario_id
                LEFT JOIN caixas c ON c.id = ae.caixa_id
                LEFT JOIN pdvs p ON p.id = c.pdv_id
                WHERE ae.id = %s
                LIMIT 1
                """,
                (int(evento_id),),
            )
            return cast(dict[str, Any] | None, cur.fetchone())
