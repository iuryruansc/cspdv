from __future__ import annotations

from typing import Any, Mapping, Sequence, cast

from database.migrations.runner import CursorLike

VERSION = "20260517_006"
DESCRIPTION = "Garante unicidade operacional em PDVs, unidades, formas e codigos de produto"

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

def _has_unique_index(cursor: CursorLike, table_name: str, expected_columns: Sequence[str]) -> bool:
    esperado = tuple(expected_columns)
    for non_unique, colunas in _indexes(cursor, table_name).values():
        if non_unique == 0 and colunas == esperado:
            return True
    return False

def _create_unique_if_missing(cursor: CursorLike, table_name: str, index_name: str, column_name: str) -> None:
    if not _has_unique_index(cursor, table_name, (column_name,)):
        cursor.execute(
            f"CREATE UNIQUE INDEX {index_name} ON {table_name} ({column_name})"
        )

def apply(cursor: CursorLike) -> None:
    _create_unique_if_missing(cursor, "pdvs", "uniq_pdvs_identificacao", "identificacao")
    _create_unique_if_missing(cursor, "unidades_medida", "uniq_unidades_sigla", "sigla")
    _create_unique_if_missing(cursor, "formas_pagamento", "uniq_formas_pagamento_nome", "nome")
    _create_unique_if_missing(cursor, "produtos", "uniq_produtos_cod_produto", "cod_produto")
    _create_unique_if_missing(cursor, "produtos", "uniq_produtos_codigo_barras", "codigo_barras")
