from __future__ import annotations

from database.migrations.runner import CursorLike

VERSION = "20261113_001"
DESCRIPTION = "Permite configurar a regra de desconto individual dos produtos de uma promoção"


def _coluna_existe(cursor: CursorLike, coluna: str) -> bool:
    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'promocao_produtos'
          AND COLUMN_NAME = %s
        """,
        (coluna,),
    )
    row = cursor.fetchone() or {}
    return int(row.get("total", 0) if isinstance(row, dict) else row[0]) > 0


def apply(cursor: CursorLike) -> None:
    colunas = (
        ("tipo_desconto_item", "VARCHAR(30) NULL AFTER produto_id"),
        ("desconto_percentual_item", "DECIMAL(10,2) NULL AFTER tipo_desconto_item"),
        ("desconto_valor_item", "DECIMAL(10,2) NULL AFTER desconto_percentual_item"),
        ("preco_fixo_item", "DECIMAL(10,2) NULL AFTER desconto_valor_item"),
    )
    for nome, definicao in colunas:
        if not _coluna_existe(cursor, nome):
            cursor.execute(f"ALTER TABLE promocao_produtos ADD COLUMN {nome} {definicao}")
