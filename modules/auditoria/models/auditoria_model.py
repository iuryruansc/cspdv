from typing import Any, Dict, List, Optional, cast

from database.connection import get_connection


class AuditoriaModel:
    @staticmethod
    def registrar_evento(
        *,
        evento: str,
        categoria: str,
        entidade: Optional[str],
        entidade_id: Optional[int],
        usuario_id: Optional[int],
        caixa_id: Optional[int],
        detalhes_json: Optional[str],
    ) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
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
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def listar(limit: int = 300) -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
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
            return cast(List[Dict[str, Any]], cursor.fetchall())
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def buscar_por_id(evento_id: int) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
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
            return cast(Optional[Dict[str, Any]], cursor.fetchone())
        finally:
            cursor.close()
            conn.close()
