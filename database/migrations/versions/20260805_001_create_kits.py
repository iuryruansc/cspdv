from __future__ import annotations

from typing import Any, Mapping, Sequence, cast

from database.migrations.runner import CursorLike

VERSION = "20260805_001"
DESCRIPTION = "Kits de produtos: tabelas kits e kit_itens"


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
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS `kits` (
            `id` int NOT NULL AUTO_INCREMENT,
            `produto_id` int NOT NULL COMMENT 'Produto que representa o kit',
            `nome` varchar(250) NOT NULL,
            `descricao` text,
            `preco_kit` decimal(10,2) NOT NULL DEFAULT 0.00,
            `ativo` char(1) NOT NULL DEFAULT 'S',
            `createdAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
            `updatedAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (`id`),
            KEY `idx_kits_produto` (`produto_id`),
            KEY `idx_kits_ativo` (`ativo`),
            CONSTRAINT `fk_kits_produto` FOREIGN KEY (`produto_id`) REFERENCES `produtos` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS `kit_itens` (
            `id` int NOT NULL AUTO_INCREMENT,
            `kit_id` int NOT NULL,
            `produto_id` int NOT NULL COMMENT 'Componente do kit',
            `quantidade` int NOT NULL DEFAULT 1,
            `createdAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
            `updatedAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (`id`),
            KEY `idx_kit_itens_kit` (`kit_id`),
            KEY `idx_kit_itens_produto` (`produto_id`),
            CONSTRAINT `fk_kit_itens_kit` FOREIGN KEY (`kit_id`) REFERENCES `kits` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT `fk_kit_itens_produto` FOREIGN KEY (`produto_id`) REFERENCES `produtos` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    )
