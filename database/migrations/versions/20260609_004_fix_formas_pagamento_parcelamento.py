from __future__ import annotations

from typing import Any, Mapping, Sequence, cast

from database.migrations.runner import CursorLike

VERSION = "20260609_004"
DESCRIPTION = "Corrige permite_parcelamento e taxa_administrativa em formas_pagamento existentes"


def apply(cursor: CursorLike) -> None:
    correct_values = [
        ("Dinheiro", "N", 0.00),
        ("PIX", "N", 0.00),
        ("Cartao Debito", "N", 0.00),
        ("Cartao Credito", "S", 0.00),
        ("Vale Refeicao", "N", 0.00),
        ("Pag. Parcial", "N", 0.00),
    ]

    for nome, permite, taxa in correct_values:
        cursor.execute(
            """
            UPDATE formas_pagamento
            SET permite_parcelamento = %s,
                taxa_administrativa = %s,
                updatedAt = NOW()
            WHERE UPPER(TRIM(nome)) = UPPER(TRIM(%s))
              AND (
                  permite_parcelamento IS NULL
                  OR permite_parcelamento != %s
                  OR taxa_administrativa IS NULL
                  OR taxa_administrativa != %s
              )
            """,
            (permite, taxa, nome, permite, taxa),
        )
