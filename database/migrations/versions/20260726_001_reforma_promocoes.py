from __future__ import annotations

from typing import Any, Mapping, Sequence, cast

from database.migrations.runner import CursorLike

VERSION = "20260726_001"
DESCRIPTION = "Reforma promocoes: tabela promocao_regras, novos tipos de desconto e colunas auxiliares"


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
        "promocoes",
        "leve_x",
        "ALTER TABLE `promocoes` ADD COLUMN `leve_x` int DEFAULT NULL AFTER `preco_fixo`",
    )
    _add_column_if_missing(
        cursor,
        "promocoes",
        "pague_y",
        "ALTER TABLE `promocoes` ADD COLUMN `pague_y` int DEFAULT NULL AFTER `leve_x`",
    )
    _add_column_if_missing(
        cursor,
        "promocoes",
        "aplicacao_desconto_xpy",
        "ALTER TABLE `promocoes` ADD COLUMN `aplicacao_desconto_xpy` varchar(20) DEFAULT 'MAIS_BARATO' AFTER `pague_y`",
    )
    _add_column_if_missing(
        cursor,
        "promocoes",
        "regras_progressivas",
        "ALTER TABLE `promocoes` ADD COLUMN `regras_progressivas` json DEFAULT NULL AFTER `aplicacao_desconto_xpy`",
    )
    _add_column_if_missing(
        cursor,
        "promocoes",
        "combo_qtd",
        "ALTER TABLE `promocoes` ADD COLUMN `combo_qtd` int DEFAULT NULL AFTER `regras_progressivas`",
    )
    _add_column_if_missing(
        cursor,
        "promocoes",
        "combo_preco",
        "ALTER TABLE `promocoes` ADD COLUMN `combo_preco` decimal(10,2) DEFAULT NULL AFTER `combo_qtd`",
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS `promocao_regras` (
          `id` int NOT NULL AUTO_INCREMENT,
          `promocao_id` int NOT NULL,
          `tipo_regra` varchar(30) NOT NULL,
          `alvo_id` int DEFAULT NULL,
          `alvo_ids` text DEFAULT NULL,
          `alvo_texto` varchar(255) DEFAULT NULL,
          `faixa_min` decimal(10,2) DEFAULT NULL,
          `faixa_max` decimal(10,2) DEFAULT NULL,
          `ativo` char(1) NOT NULL DEFAULT 'S',
          `createdAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
          `updatedAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`),
          KEY `idx_promocao_regras_promocao` (`promocao_id`),
          KEY `idx_promocao_regras_tipo` (`tipo_regra`),
          KEY `idx_promocao_regras_ativo` (`ativo`),
          CONSTRAINT `fk_promocao_regras_promocao` FOREIGN KEY (`promocao_id`) REFERENCES `promocoes` (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
        """,
    )
