from typing import Any, Dict, Iterable, List, Optional, cast

from database.connection import get_connection

def listar_registros(
    *,
    table: str,
    id_column: str,
    name_column: str,
    status_column: str = "ativo",
) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            f"""
            SELECT {id_column} AS id, {name_column}, {status_column}
            FROM {table}
            ORDER BY {name_column}
            """
        )
        return cast(List[Dict[str, Any]], cursor.fetchall())
    finally:
        cursor.close()
        conn.close()

def inserir_registro(
    *,
    table: str,
    columns: Iterable[str],
    dados: Dict[str, Any],
) -> Optional[int]:
    colunas = list(columns)
    placeholders = ", ".join(f"%({coluna})s" for coluna in colunas)
    nomes_colunas = ", ".join(colunas)

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            f"INSERT INTO {table} ({nomes_colunas}) VALUES ({placeholders})",
            dados,
        )
        conn.commit()
        return cursor.lastrowid
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

def buscar_registro_por_id(
    *,
    table: str,
    id_column: str,
    columns: Iterable[str],
    record_id: int,
) -> Optional[Dict[str, Any]]:
    colunas = ", ".join(columns)

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            f"""
            SELECT {colunas}
            FROM {table}
            WHERE {id_column} = %s
            LIMIT 1
            """,
            (record_id,),
        )
        return cast(Optional[Dict[str, Any]], cursor.fetchone())
    finally:
        cursor.close()
        conn.close()

def atualizar_registro(
    *,
    table: str,
    id_column: str,
    columns: Iterable[str],
    record_id: int,
    dados: Dict[str, Any],
) -> bool:
    colunas = list(columns)
    set_clause = ", ".join(f"{coluna} = %({coluna})s" for coluna in colunas)

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            f"""
            UPDATE {table}
            SET {set_clause}
            WHERE {id_column} = %({id_column})s
            """,
            {**dados, id_column: record_id},
        )
        conn.commit()
        return cursor.rowcount > 0
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

def atualizar_status_registro(
    *,
    table: str,
    id_column: str,
    status_column: str,
    record_id: int,
    ativo: str,
) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            f"UPDATE {table} SET {status_column} = %s WHERE {id_column} = %s",
            (ativo, record_id),
        )
        conn.commit()
        return cursor.rowcount > 0
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()
