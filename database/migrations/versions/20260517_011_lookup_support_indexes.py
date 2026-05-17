from __future__ import annotations

from typing import Any, Mapping, Sequence, cast

from database.migrations.runner import CursorLike

VERSION = "20260517_011"
DESCRIPTION = "Adiciona indices de apoio para lookup e ordenacao operacional"

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
    # Apoio para combos/listagens ordenadas por nome.
    _create_index_if_missing(cursor, "categorias", "idx_categorias_ativo_nome", ("ativo", "nome"))
    _create_index_if_missing(cursor, "marcas", "idx_marcas_ativo_nome_marca", ("ativo", "nome_marca"))
    _create_index_if_missing(cursor, "fornecedores", "idx_fornecedores_ativo_nome_fantasia", ("ativo", "nome_fantasia"))
    _create_index_if_missing(cursor, "formas_pagamento", "idx_formas_pagamento_ativo_nome", ("ativo", "nome"))
    _create_index_if_missing(cursor, "unidades_medida", "idx_unidades_medida_ativo_sigla", ("ativo", "sigla"))
    _create_index_if_missing(cursor, "pdvs", "idx_pdvs_ativo_status_identificacao", ("ativo", "status", "identificacao"))

    # Lookup/ordenacao em clientes.
    _create_index_if_missing(cursor, "clientes", "idx_clientes_ativo_sistema_nome", ("ativo", "cliente_sistema", "nome"))
    _create_index_if_missing(cursor, "clientes", "idx_clientes_ativo_sistema_cpf", ("ativo", "cliente_sistema", "cpf"))

    # Listagem geral e painéis operacionais de produtos.
    _create_index_if_missing(cursor, "produtos", "idx_produtos_ativo_nome", ("ativo", "nome"))
    _create_index_if_missing(cursor, "produtos", "idx_produtos_ativo_categoria_fornecedor_nome", ("ativo", "categoria_id", "fornecedor_id", "nome"))
