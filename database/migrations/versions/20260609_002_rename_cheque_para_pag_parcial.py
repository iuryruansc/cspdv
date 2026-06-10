from __future__ import annotations

from typing import Any, Mapping, Sequence, cast

from database.migrations.runner import CursorLike

VERSION = "20260609_002"
DESCRIPTION = "Renomeia forma de pagamento Cheque para Pag. Parcial"


def _rows(cursor: CursorLike) -> Sequence[Sequence[Any] | Mapping[str, Any]]:
    return cast(Sequence[Sequence[Any] | Mapping[str, Any]], cursor.fetchall())


def apply(cursor: CursorLike) -> None:
    cursor.execute(
        "SELECT id FROM formas_pagamento WHERE UPPER(TRIM(nome)) = 'CHEQUE' LIMIT 1"
    )
    if _rows(cursor):
        cursor.execute(
            "UPDATE formas_pagamento SET nome = 'Pag. Parcial', updatedAt = NOW() WHERE UPPER(TRIM(nome)) = 'CHEQUE'"
        )
