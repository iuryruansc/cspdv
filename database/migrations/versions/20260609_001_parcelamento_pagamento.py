from __future__ import annotations

from typing import Any, Mapping, Sequence, cast

from database.migrations.runner import CursorLike

VERSION = "20260609_001"
DESCRIPTION = "Adiciona colunas de parcelamento e taxa administrativa em pagamento_parcial"


def _columns(cursor: CursorLike, table_name: str) -> set[str]:
    cursor.execute(f"SHOW COLUMNS FROM {table_name}")
    rows = cast(Sequence[Sequence[Any] | Mapping[str, Any]], cursor.fetchall())
    return {
        str(row["Field"] if isinstance(row, Mapping) else row[0])
        for row in rows
        if row
    }


def _add_column_if_missing(cursor: CursorLike, table_name: str, column_name: str, ddl: str) -> None:
    if column_name not in _columns(cursor, table_name):
        cursor.execute(ddl)


def apply(cursor: CursorLike) -> None:
    _add_column_if_missing(
        cursor,
        "pagamento_parcial",
        "parcelas",
        "ALTER TABLE pagamento_parcial ADD COLUMN parcelas int DEFAULT NULL",
    )
    _add_column_if_missing(
        cursor,
        "pagamento_parcial",
        "taxa_administrativa",
        "ALTER TABLE pagamento_parcial ADD COLUMN taxa_administrativa decimal(5,2) DEFAULT 0.00",
    )
