from __future__ import annotations

from typing import Any, Mapping, Sequence, cast

from database.migrations.runner import CursorLike

VERSION = "20260517_005"
DESCRIPTION = "Completa integridade relacional basica entre caixa, venda e usuario"

def _indexes(cursor: CursorLike, table_name: str) -> set[str]:
    cursor.execute(f"SHOW INDEX FROM {table_name}")
    rows = cast(Sequence[Sequence[Any] | Mapping[str, Any]], cursor.fetchall())
    nomes: set[str] = set()
    for row in rows:
        if not row:
            continue
        if isinstance(row, Mapping):
            nomes.add(str(row.get("Key_name") or ""))
        else:
            nomes.add(str(row[2] or ""))
    return nomes

def _foreign_keys(cursor: CursorLike, table_name: str) -> set[str]:
    cursor.execute(
        """
        SELECT CONSTRAINT_NAME
        FROM information_schema.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = %s
          AND REFERENCED_TABLE_NAME IS NOT NULL
        """,
        (table_name,),
    )
    rows = cast(Sequence[Sequence[Any] | Mapping[str, Any]], cursor.fetchall())
    nomes: set[str] = set()
    for row in rows:
        if not row:
            continue
        if isinstance(row, Mapping):
            nomes.add(str(row.get("CONSTRAINT_NAME") or ""))
        else:
            nomes.add(str(row[0] or ""))
    return nomes

def apply(cursor: CursorLike) -> None:
    vendas_fks = _foreign_keys(cursor, "vendas")
    if "fk_vendas_usuario" not in vendas_fks:
        cursor.execute(
            """
            ALTER TABLE vendas
            ADD CONSTRAINT fk_vendas_usuario
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            ON DELETE SET NULL
            ON UPDATE RESTRICT
            """
        )

    caixas_indexes = _indexes(cursor, "caixas")
    if "idx_caixas_usuario_fechamento" not in caixas_indexes:
        cursor.execute(
            "CREATE INDEX idx_caixas_usuario_fechamento ON caixas (usuario_fechamento_id)"
        )

    caixas_fks = _foreign_keys(cursor, "caixas")
    if "fk_caixas_usuario_fechamento" not in caixas_fks:
        cursor.execute(
            """
            ALTER TABLE caixas
            ADD CONSTRAINT fk_caixas_usuario_fechamento
            FOREIGN KEY (usuario_fechamento_id) REFERENCES usuarios (id)
            ON DELETE RESTRICT
            ON UPDATE RESTRICT
            """
        )
