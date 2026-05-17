from __future__ import annotations

from typing import Any, Mapping, Sequence, cast

from database.migrations.runner import CursorLike

VERSION = "20260517_009"
DESCRIPTION = "Adiciona indices para consultas operacionais e dashboard"

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
    # Dashboard e consultas recentes de vendas.
    _create_index_if_missing(
        cursor,
        "vendas",
        "idx_vendas_status_data_hora",
        ("status", "data_hora"),
    )

    # Recebimentos por periodo, forma e venda.
    _create_index_if_missing(
        cursor,
        "pagamento_parcial",
        "idx_pagamento_parcial_data_forma_venda",
        ("data_pagamento", "forma_pagamento", "venda_id"),
    )

    # Contas a receber por vencimento/status/PDV.
    _create_index_if_missing(
        cursor,
        "contas_receber",
        "idx_contas_receber_ativo_status_vencimento_caixa",
        ("ativo", "status", "data_vencimento", "caixa_id"),
    )

    # Recebimentos posteriores e comprovantes.
    _create_index_if_missing(
        cursor,
        "contas_receber_recebimentos",
        "idx_crr_ativo_data_conta",
        ("ativo", "data_recebimento", "conta_receber_id"),
    )

    # Reembolsos por periodo/status.
    _create_index_if_missing(
        cursor,
        "venda_reembolsos",
        "idx_venda_reembolsos_ativo_status_data_venda",
        ("ativo", "status", "data_hora", "venda_id"),
    )

    # Busca da promocao vigente por produto.
    _create_index_if_missing(
        cursor,
        "promocao_produtos",
        "idx_promocao_produtos_produto_ativo_promocao",
        ("produto_id", "ativo", "promocao_id"),
    )

    # Alertas e listagem de promocoes.
    _create_index_if_missing(
        cursor,
        "promocoes",
        "idx_promocoes_ativo_status_data_fim",
        ("ativo", "status", "data_fim"),
    )
