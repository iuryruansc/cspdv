from __future__ import annotations

from typing import Any, Mapping, Sequence, cast

from database.migrations.runner import CursorLike

VERSION = "20260517_008"
DESCRIPTION = "Adiciona flag de registro de sistema para clientes base"

def _rows(cursor: CursorLike) -> Sequence[Sequence[Any] | Mapping[str, Any]]:
    return cast(Sequence[Sequence[Any] | Mapping[str, Any]], cursor.fetchall())

def _column_exists(cursor: CursorLike, table_name: str, column_name: str) -> bool:
    cursor.execute(
        """
        SELECT 1
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = %s
          AND COLUMN_NAME = %s
        LIMIT 1
        """,
        (table_name, column_name),
    )
    return bool(_rows(cursor))

def apply(cursor: CursorLike) -> None:
    if not _column_exists(cursor, "clientes", "cliente_sistema"):
        cursor.execute(
            """
            ALTER TABLE clientes
            ADD COLUMN cliente_sistema CHAR(1) NOT NULL DEFAULT 'N'
            AFTER observacao
            """
        )

    cursor.execute(
        """
        UPDATE clientes
        SET cliente_sistema = 'S'
        WHERE UPPER(TRIM(nome)) = 'CONSUMIDOR FINAL'
        """
    )
