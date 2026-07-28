from __future__ import annotations
from typing import Any, Iterable, cast

from database.connection import db_cursor, db_transaction

def listar_registros(
    *,
    table: str,
    id_column: str,
    name_column: str,
    status_column: str = "ativo",
) -> list[dict[str, Any]]:
    with db_cursor() as cur:
        cur.execute(
            f"""
            SELECT {id_column} AS id, {name_column}, {status_column}
            FROM {table}
            ORDER BY {name_column}
            """
        )
        return cast(list[dict[str, Any]], cur.fetchall())
def inserir_registro(
    *,
    table: str,
    columns: Iterable[str],
    dados: dict[str, Any],
) -> int | None:
    colunas = list(columns)
    placeholders = ", ".join(f"%({coluna})s" for coluna in colunas)
    nomes_colunas = ", ".join(colunas)

    with db_transaction(dictionary=False) as cur:
        cur.execute(
            f"INSERT INTO {table} ({nomes_colunas}) VALUES ({placeholders})",
            dados,
        )
        return cur.lastrowid
def buscar_registro_por_id(
    *,
    table: str,
    id_column: str,
    columns: Iterable[str],
    record_id: int,
) -> dict[str, Any] | None:
    colunas = ", ".join(columns)

    with db_cursor() as cur:
        cur.execute(
            f"""
            SELECT {colunas}
            FROM {table}
            WHERE {id_column} = %s
            LIMIT 1
            """,
            (record_id,),
        )
        return cast(dict[str, Any] | None, cur.fetchone())
def atualizar_registro(
    *,
    table: str,
    id_column: str,
    columns: Iterable[str],
    record_id: int,
    dados: dict[str, Any],
) -> bool:
    colunas = list(columns)
    set_clause = ", ".join(f"{coluna} = %({coluna})s" for coluna in colunas)

    with db_transaction(dictionary=False) as cur:
        cur.execute(
            f"""
            UPDATE {table}
            SET {set_clause}
            WHERE {id_column} = %({id_column})s
            """,
            {**dados, id_column: record_id},
        )
        return cur.rowcount > 0
def atualizar_status_registro(
    *,
    table: str,
    id_column: str,
    status_column: str,
    record_id: int,
    ativo: str,
) -> bool:
    with db_transaction(dictionary=False) as cur:
        cur.execute(
            f"UPDATE {table} SET {status_column} = %s WHERE {id_column} = %s",
            (ativo, record_id),
        )
        return cur.rowcount > 0
