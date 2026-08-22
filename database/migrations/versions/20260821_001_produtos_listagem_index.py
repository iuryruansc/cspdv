from __future__ import annotations

from database.migrations.runner import CursorLike

VERSION = "20260821_001"
DESCRIPTION = "Produtos: otimizar ordenacao da listagem administrativa"


def apply(cursor: CursorLike) -> None:
    cursor.execute(
        """
        CREATE INDEX `idx_produtos_ativo_nome_id`
        ON `produtos` (`ativo`, `nome`, `id`)
        """
    )
