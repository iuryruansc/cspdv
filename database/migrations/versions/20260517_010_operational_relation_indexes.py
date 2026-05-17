from __future__ import annotations

from typing import Any, Mapping, Sequence, cast

from database.migrations.runner import CursorLike

VERSION = "20260517_010"
DESCRIPTION = "Adiciona indices relacionais para estoque, lotes e consultas auxiliares"

def _indexes(cursor: CursorLike, table_name: str) -> dict[str, tuple[int, tuple[str, ...]]]:
    cursor.execute(f"SHOW INDEX FROM {table_name}")
    rows = cast(Sequence[Sequence[Any] | Mapping[str, Any]], cursor.fetchall())
    agrupados: dict[str, list[tuple[int, str, int]]] = {}

    for row in rows:
        if not row:
            continue
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
        non_unique = ordenados[0][2] if ordenados else 1
        colunas = tuple(item[1] for item in ordenados)
        resultado[nome] = (non_unique, colunas)
    return resultado


def _has_index(cursor: CursorLike, table_name: str, expected_columns: Sequence[str]) -> bool:
    esperado = tuple(expected_columns)
    for _non_unique, colunas in _indexes(cursor, table_name).values():
        if colunas == esperado:
            return True
    return False

def _create_index_if_missing(
    cursor: CursorLike,
    table_name: str,
    index_name: str,
    columns: Sequence[str],
) -> None:
    if _has_index(cursor, table_name, columns):
        return
    cursor.execute(
        f"CREATE INDEX {index_name} ON {table_name} ({', '.join(columns)})"
    )

def apply(cursor: CursorLike) -> None:
    # Estoque / lotes.
    _create_index_if_missing(
        cursor,
        "lotes",
        "idx_lotes_produto_ativo_validade_numero",
        ("produto_id", "ativo", "data_validade", "numero_lote"),
    )
    _create_index_if_missing(
        cursor,
        "movimentacao_estoque",
        "idx_movimentacao_estoque_ativo_data_lote",
        ("ativo", "data_hora", "lote_id"),
    )

    # Consultas auxiliares do financeiro e venda.
    _create_index_if_missing(
        cursor,
        "venda_reembolso_itens",
        "idx_venda_reembolso_itens_item_venda",
        ("item_venda_id",),
    )
    _create_index_if_missing(
        cursor,
        "pagamento_parcial",
        "idx_pagamento_parcial_venda_id",
        ("venda_id",),
    )

    # Fluxos de promocoes por promocao e produto.
    _create_index_if_missing(
        cursor,
        "promocao_produtos",
        "idx_promocao_produtos_promocao_ativo_produto",
        ("promocao_id", "ativo", "produto_id"),
    )
