from __future__ import annotations

from typing import Any, Mapping, Sequence, cast

from database.migrations.runner import CursorLike

VERSION = "20261108_001"
DESCRIPTION = "Adiciona indice para consulta de fornecimentos recentes do estoque"


def _indexes(cursor: CursorLike, table_name: str) -> dict[str, tuple[int, tuple[str, ...]]]:
    cursor.execute(f"SHOW INDEX FROM {table_name}")
    rows = cast(Sequence[Sequence[Any] | Mapping[str, Any]], cursor.fetchall())
    agrupados: dict[str, list[tuple[int, str, int]]] = {}

    for row in rows:
        if isinstance(row, Mapping):
            nome = str(row.get("Key_name") or "")
            non_unique = int(row.get("Non_unique") or 0)
            seq = int(row.get("Seq_in_index") or 0)
            coluna = str(row.get("Column_name") or "")
        else:
            nome = str(row[2] or "")
            non_unique = int(row[1] or 0)
            seq = int(row[3] or 0)
            coluna = str(row[4] or "")
        agrupados.setdefault(nome, []).append((seq, coluna, non_unique))

    resultado: dict[str, tuple[int, tuple[str, ...]]] = {}
    for nome, itens in agrupados.items():
        ordenados = sorted(itens, key=lambda item: item[0])
        resultado[nome] = (
            ordenados[0][2] if ordenados else 1,
            tuple(item[1] for item in ordenados),
        )
    return resultado


def apply(cursor: CursorLike) -> None:
    colunas = ("ativo", "tipo", "data_hora", "id", "lote_id")
    if any(indice[1] == colunas for indice in _indexes(cursor, "movimentacao_estoque").values()):
        return

    cursor.execute(
        """
        CREATE INDEX idx_movimentacao_estoque_ativo_tipo_data_id
        ON movimentacao_estoque (ativo, tipo, data_hora, id, lote_id)
        """
    )
