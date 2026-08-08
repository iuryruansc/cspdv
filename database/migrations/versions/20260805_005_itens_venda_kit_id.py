from __future__ import annotations

from typing import Any, Mapping, Sequence, cast

from database.migrations.runner import CursorLike

VERSION = "20260805_005"
DESCRIPTION = "itens_venda: adicionar kit_id e tornar produto_id nullable"


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

    if "kit_id" not in cols:
        cursor.execute(
            "ALTER TABLE `itens_venda` ADD COLUMN `kit_id` int NULL AFTER `lote_id`"
        )

    if "produto_id" in cols:
        cursor.execute(
            "ALTER TABLE `itens_venda` MODIFY COLUMN `produto_id` int NULL"
        )
