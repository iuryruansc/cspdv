from __future__ import annotations

from database.migrations.runner import CursorLike

VERSION = "20261109_001"
DESCRIPTION = "Cria o registro relacional de fornecimentos e vincula suas movimentações"


def _coluna_existe(cursor: CursorLike, tabela: str, coluna: str) -> bool:
    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND COLUMN_NAME = %s
        """,
        (tabela, coluna),
    )
    row = cursor.fetchone() or {}
    return int(row.get("total", 0) if isinstance(row, dict) else row[0]) > 0


def _indice_existe(cursor: CursorLike, tabela: str, indice: str) -> bool:
    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM information_schema.STATISTICS
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND INDEX_NAME = %s
        """,
        (tabela, indice),
    )
    row = cursor.fetchone() or {}
    return int(row.get("total", 0) if isinstance(row, dict) else row[0]) > 0


def apply(cursor: CursorLike) -> None:
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS estoque_fornecimentos (
            id INT NOT NULL AUTO_INCREMENT,
            cliente_id INT NOT NULL,
            usuario_id INT NOT NULL,
            data_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            observacao TEXT NULL,
            ativo CHAR(1) NOT NULL DEFAULT 'S',
            createdAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            KEY idx_estoque_fornecimentos_cliente_data (cliente_id, data_hora, id),
            KEY idx_estoque_fornecimentos_usuario_data (usuario_id, data_hora, id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS estoque_fornecimentos_itens (
            id INT NOT NULL AUTO_INCREMENT,
            fornecimento_id INT NOT NULL,
            produto_id INT NOT NULL,
            quantidade INT NOT NULL,
            createdAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            KEY idx_estoque_fornecimentos_itens_fornecimento (fornecimento_id, id),
            KEY idx_estoque_fornecimentos_itens_produto (produto_id, id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
    )

    if not _coluna_existe(cursor, "movimentacao_estoque", "fornecimento_id"):
        cursor.execute(
            "ALTER TABLE movimentacao_estoque ADD COLUMN fornecimento_id INT NULL AFTER venda_id"
        )
    if not _indice_existe(cursor, "movimentacao_estoque", "idx_movimentacao_estoque_fornecimento"):
        cursor.execute(
            "CREATE INDEX idx_movimentacao_estoque_fornecimento ON movimentacao_estoque (fornecimento_id, data_hora, id)"
        )
