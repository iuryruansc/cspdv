from __future__ import annotations

from typing import Any, Mapping, Sequence, cast

from database.migrations.runner import CursorLike

VERSION = "20260517_002"
DESCRIPTION = "Garante unicidade operacional em PDVs e formas de pagamento"

def _indexes_da_tabela(cursor: CursorLike, tabela: str) -> set[str]:
    cursor.execute(f"SHOW INDEX FROM {tabela}")
    rows = cast(Sequence[Sequence[Any] | Mapping[str, Any]], cursor.fetchall())
    indexes: set[str] = set()
    for row in rows:
        if isinstance(row, Mapping):
            indexes.add(str(row.get("Key_name") or ""))
        elif row:
            indexes.add(str(row[2]))
    return indexes

def apply(cursor: CursorLike) -> None:
    pdv_indexes = _indexes_da_tabela(cursor, "pdvs")
    if "uniq_pdvs_identificacao" not in pdv_indexes:
        cursor.execute("ALTER TABLE pdvs ADD CONSTRAINT uniq_pdvs_identificacao UNIQUE (identificacao)")

    forma_indexes = _indexes_da_tabela(cursor, "formas_pagamento")
    if "uniq_formas_pagamento_nome" not in forma_indexes:
        cursor.execute("ALTER TABLE formas_pagamento ADD CONSTRAINT uniq_formas_pagamento_nome UNIQUE (nome)")
