from __future__ import annotations

from typing import Any, Mapping, Sequence, cast

from database.migrations.runner import CursorLike

VERSION = "20260805_004"
DESCRIPTION = "itens_venda: tornar lote_id nullable para kits"


def _columns(cursor: CursorLike, table_name: str) -> set[str]:
    cursor.execute(f"SHOW COLUMNS FROM {table_name}")
    rows = cast(Sequence[Sequence[Any] | Mapping[str, Any]], cursor.fetchall())
    return {
        str(row["Field"] if isinstance(row, Mapping) else row[0])
        for row in rows
        if row
    }


def apply(cursor: CursorLike) -> None:
    cols = _columns(cursor, "itens_venda")
    if "lote_id" in cols:
        cursor.execute("ALTER TABLE `itens_venda` MODIFY COLUMN `lote_id` int NULL")
