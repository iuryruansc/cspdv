from __future__ import annotations

from typing import Any, Sequence, cast

from database.migrations.runner import CursorLike

VERSION = "20260517_012"
DESCRIPTION = "Cria tabela de auditoria para eventos operacionais e administrativos"

def _index_exists(cursor: CursorLike, table_name: str, index_name: str) -> bool:
    cursor.execute(f"SHOW INDEX FROM {table_name}")
    rows = cast(list[Sequence[Any]], cursor.fetchall())
    for row in rows:
        if len(row) > 2 and str(row[2]) == index_name:
            return True
    return False

def apply(cursor: CursorLike) -> None:
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS auditoria_eventos (
            id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            evento VARCHAR(80) NOT NULL,
            categoria VARCHAR(80) NOT NULL,
            entidade VARCHAR(80) NULL,
            entidade_id INT NULL,
            usuario_id INT NULL,
            caixa_id INT NULL,
            detalhes_json LONGTEXT NULL,
            createdAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    if not _index_exists(cursor, "auditoria_eventos", "idx_auditoria_categoria_data"):
        cursor.execute(
            """
            CREATE INDEX idx_auditoria_categoria_data
            ON auditoria_eventos (categoria, createdAt)
            """
        )
    if not _index_exists(cursor, "auditoria_eventos", "idx_auditoria_usuario_data"):
        cursor.execute(
            """
            CREATE INDEX idx_auditoria_usuario_data
            ON auditoria_eventos (usuario_id, createdAt)
            """
        )
    if not _index_exists(cursor, "auditoria_eventos", "idx_auditoria_caixa_data"):
        cursor.execute(
            """
            CREATE INDEX idx_auditoria_caixa_data
            ON auditoria_eventos (caixa_id, createdAt)
            """
        )
