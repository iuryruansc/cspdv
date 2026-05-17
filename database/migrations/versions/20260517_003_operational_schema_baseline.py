from __future__ import annotations

from typing import Any, Mapping, Sequence, cast

from database.migrations.runner import CursorLike

VERSION = "20260517_003"
DESCRIPTION = "Padroniza timestamps e indices basicos da operacao"

def _columns(cursor: CursorLike, table_name: str) -> set[str]:
    cursor.execute(f"SHOW COLUMNS FROM {table_name}")
    rows = cast(Sequence[Sequence[Any] | Mapping[str, Any]], cursor.fetchall())
    return {
        str(row["Field"] if isinstance(row, Mapping) else row[0])
        for row in rows
        if row
    }

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

def _add_column_if_missing(cursor: CursorLike, table_name: str, column_name: str, ddl: str) -> None:
    if column_name not in _columns(cursor, table_name):
        cursor.execute(ddl)

def _add_index_if_missing(cursor: CursorLike, table_name: str, index_name: str, ddl: str) -> None:
    if index_name not in _indexes(cursor, table_name):
        cursor.execute(ddl)

def apply(cursor: CursorLike) -> None:
    _add_column_if_missing(
        cursor,
        "formas_pagamento",
        "createdAt",
        "ALTER TABLE formas_pagamento ADD COLUMN createdAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
    )
    _add_column_if_missing(
        cursor,
        "formas_pagamento",
        "updatedAt",
        "ALTER TABLE formas_pagamento ADD COLUMN updatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
    )
    _add_column_if_missing(
        cursor,
        "pdvs",
        "createdAt",
        "ALTER TABLE pdvs ADD COLUMN createdAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
    )
    _add_column_if_missing(
        cursor,
        "pdvs",
        "updatedAt",
        "ALTER TABLE pdvs ADD COLUMN updatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
    )
    _add_column_if_missing(
        cursor,
        "unidades_medida",
        "createdAt",
        "ALTER TABLE unidades_medida ADD COLUMN createdAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
    )
    _add_column_if_missing(
        cursor,
        "unidades_medida",
        "updatedAt",
        "ALTER TABLE unidades_medida ADD COLUMN updatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
    )

    _add_index_if_missing(
        cursor,
        "caixas",
        "idx_caixas_pdv_status_ativo",
        "CREATE INDEX idx_caixas_pdv_status_ativo ON caixas (pdv_id, status, ativo)",
    )
    _add_index_if_missing(
        cursor,
        "caixas",
        "idx_caixas_usuario_status_ativo",
        "CREATE INDEX idx_caixas_usuario_status_ativo ON caixas (usuario_abertura_id, status, ativo)",
    )
    _add_index_if_missing(
        cursor,
        "caixa_movimentacoes",
        "idx_caixa_mov_caixa_ativo_estorno_data",
        "CREATE INDEX idx_caixa_mov_caixa_ativo_estorno_data ON caixa_movimentacoes (caixa_id, ativo, estornado, data_hora)",
    )
    _add_index_if_missing(
        cursor,
        "caixa_motivos",
        "uniq_caixa_motivos_tipo_padrao",
        "CREATE UNIQUE INDEX uniq_caixa_motivos_tipo_padrao ON caixa_motivos (tipo_padrao)",
    )
