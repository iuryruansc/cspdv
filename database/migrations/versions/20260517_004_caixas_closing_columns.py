from __future__ import annotations

from typing import Any, Mapping, Sequence, cast

from database.migrations.runner import CursorLike

VERSION = "20260517_004"
DESCRIPTION = "Padroniza colunas de fechamento em caixas"

def _columns(cursor: CursorLike, table_name: str) -> set[str]:
    cursor.execute(f"SHOW COLUMNS FROM {table_name}")
    rows = cast(Sequence[Sequence[Any] | Mapping[str, Any]], cursor.fetchall())
    return {
        str(row["Field"] if isinstance(row, Mapping) else row[0])
        for row in rows
        if row
    }

def apply(cursor: CursorLike) -> None:
    colunas = _columns(cursor, "caixas")

    if "valor_fechamento" not in colunas:
        cursor.execute("ALTER TABLE caixas ADD COLUMN valor_fechamento DECIMAL(12,2) NULL")
    if "diferenca_fechamento" not in colunas:
        cursor.execute("ALTER TABLE caixas ADD COLUMN diferenca_fechamento DECIMAL(12,2) NULL")
    if "observacoes_fechamento" not in colunas and "observacao_fechamento" not in colunas:
        cursor.execute("ALTER TABLE caixas ADD COLUMN observacoes_fechamento TEXT NULL")

    colunas_atuais = _columns(cursor, "caixas")
    if "valor_fechamento_informado" in colunas_atuais:
        cursor.execute(
            """
            UPDATE caixas
            SET valor_fechamento = valor_fechamento_informado
            WHERE valor_fechamento IS NULL
              AND valor_fechamento_informado IS NOT NULL
            """
        )
    if "valor_fechamento_sistema" in colunas_atuais:
        cursor.execute(
            """
            UPDATE caixas
            SET diferenca_fechamento = ROUND(COALESCE(valor_fechamento, 0) - COALESCE(valor_fechamento_sistema, 0), 2)
            WHERE diferenca_fechamento IS NULL
              AND valor_fechamento_sistema IS NOT NULL
              AND valor_fechamento IS NOT NULL
            """
        )
