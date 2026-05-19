from __future__ import annotations

from database.connection import get_connection_diagnostics, get_server_connection

def _quote_identifier(name: str) -> str:
    return f"`{name.replace('`', '``')}`"

def bootstrap_database() -> bool:
    diagnostics = get_connection_diagnostics()
    database_name = str(diagnostics["database"] or "").strip()

    if not database_name:
        raise ConnectionError("DB_NAME nao foi configurado.")

    conn = get_server_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = %s",
            (database_name,),
        )
        if cursor.fetchall():
            return False

        cursor.execute(
            f"CREATE DATABASE {_quote_identifier(database_name)} "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        conn.commit()
        return True
    except Exception as exc:
        conn.rollback()
        raise ConnectionError(f"Nao foi possivel preparar o banco de dados '{database_name}': {exc}")
    finally:
        cursor.close()
        conn.close()
