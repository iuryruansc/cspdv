from __future__ import annotations

from typing import Any, Mapping, Sequence, cast

from database.migrations.runner import CursorLike

VERSION = "20260821_002"
DESCRIPTION = "reembolsos: permitir item de kit sem produto ou lote direto"


def _columns(cursor: CursorLike, table_name: str) -> set[str]:
    cursor.execute(f"SHOW COLUMNS FROM `{table_name}`")
    rows = cast(Sequence[Sequence[Any] | Mapping[str, Any]], cursor.fetchall())
    return {
        str(row["Field"] if isinstance(row, Mapping) else row[0])
        for row in rows
        if row
    }


def apply(cursor: CursorLike) -> None:
    columns = _columns(cursor, "venda_reembolso_itens")
    if "produto_id" in columns:
        cursor.execute(
            "ALTER TABLE `venda_reembolso_itens` MODIFY COLUMN `produto_id` int NULL"
        )
