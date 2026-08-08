from __future__ import annotations

from typing import Any, Mapping, Sequence, cast

from database.migrations.runner import CursorLike

VERSION = "20260805_006"
DESCRIPTION = "Kits: adicionar cod_produto"


def _columns(cursor: CursorLike, table_name: str) -> set[str]:
    cursor.execute(f"SHOW COLUMNS FROM {table_name}")
    rows = cast(Sequence[Sequence[Any] | Mapping[str, Any]], cursor.fetchall())
    return {
        str(row["Field"] if isinstance(row, Mapping) else row[0])
        for row in rows
        if row
    }


def apply(cursor: CursorLike) -> None:
    cols = _columns(cursor, "kits")
    if "cod_produto" not in cols:
        cursor.execute(
            "ALTER TABLE `kits` ADD COLUMN `cod_produto` varchar(60) NULL AFTER `nome`"
        )
