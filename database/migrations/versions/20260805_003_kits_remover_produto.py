from __future__ import annotations

from typing import Any, Mapping, Sequence, cast

from database.migrations.runner import CursorLike

VERSION = "20260805_003"
DESCRIPTION = "Kits: remover produto_id (kit e item independente)"


def _columns(cursor: CursorLike, table_name: str) -> set[str]:
    cursor.execute(f"SHOW COLUMNS FROM {table_name}")
    rows = cast(Sequence[Sequence[Any] | Mapping[str, Any]], cursor.fetchall())
    return {
        str(row["Field"] if isinstance(row, Mapping) else row[0])
        for row in rows
        if row
    }


def _foreign_keys(cursor: CursorLike, table_name: str) -> set[str]:
    cursor.execute(
        f"""
        SELECT CONSTRAINT_NAME
        FROM information_schema.TABLE_CONSTRAINTS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = '{table_name}'
          AND CONSTRAINT_TYPE = 'FOREIGN KEY'
        """
    )
    return {str(row[0]) for row in cursor.fetchall()}


def _indexes(cursor: CursorLike, table_name: str) -> set[str]:
    cursor.execute(f"SHOW INDEX FROM {table_name}")
    rows = cast(Sequence[Sequence[Any] | Mapping[str, Any]], cursor.fetchall())
    return {
        str(row["Key_name"] if isinstance(row, Mapping) else row[2])
        for row in rows
        if row
    }


def apply(cursor: CursorLike) -> None:
    fks = _foreign_keys(cursor, "kits")
    if "fk_kits_produto" in fks:
        cursor.execute("ALTER TABLE `kits` DROP FOREIGN KEY `fk_kits_produto`")

    idxs = _indexes(cursor, "kits")
    if "idx_kits_produto" in idxs:
        cursor.execute("ALTER TABLE `kits` DROP INDEX `idx_kits_produto`")

    cols = _columns(cursor, "kits")
    if "produto_id" in cols:
        cursor.execute("ALTER TABLE `kits` MODIFY COLUMN `produto_id` int NULL")
