import os
from typing import Any, Sequence, cast

import mysql.connector
from mysql.connector import Error, pooling

from utils.runtime_paths import load_project_dotenv

load_project_dotenv()

_connection_pool = None

def _db_config(*, include_database: bool = True):
    host = os.getenv("DB_HOST", "127.0.0.1").strip()

    if host.lower() == "localhost":
        host = "127.0.0.1"

    config = {
        "host": host,
        "port": int(os.getenv("DB_PORT", 3306)),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "charset": "utf8mb4",
        "autocommit": False,
        "connection_timeout": int(os.getenv("DB_CONNECTION_TIMEOUT", 5)),
        "use_pure": True,
    }
    if include_database:
        config["database"] = os.getenv("DB_NAME")
    return config

def _usar_pool():
    return os.getenv("DB_USE_POOL", "").strip().lower() in {"1", "true", "yes", "on"}

def get_connection_mode():
    return "pool" if _usar_pool() else "direta"

def get_connection_diagnostics():
    config = _db_config()
    diagnostics = {
        "mode": get_connection_mode(),
        "host": config["host"],
        "port": config["port"],
        "database": config["database"],
        "use_pure": config["use_pure"],
        "connection_timeout": config["connection_timeout"],
        "pool_enabled": _usar_pool(),
        "pool_initialized": _connection_pool is not None,
    }

    if _usar_pool():
        diagnostics["pool_name"] = os.getenv("DB_POOL_NAME", "cspdv_pool")
        diagnostics["pool_size"] = int(os.getenv("DB_POOL_SIZE", 5))

    return diagnostics

def get_connection_pool():
    global _connection_pool

    if _connection_pool is None:
        config = _db_config()

        try:
            _connection_pool = pooling.MySQLConnectionPool(
                pool_name=os.getenv("DB_POOL_NAME", "cspdv_pool"),
                pool_size=int(os.getenv("DB_POOL_SIZE", 5)),
                pool_reset_session=True,
                **config,
            )
        except Exception as exc:
            raise ConnectionError(f"Nao foi possivel criar o pool de conexoes: {exc}")

    return _connection_pool

def get_connection():
    try:
        if _usar_pool():
            return get_connection_pool().get_connection()
        return mysql.connector.connect(**_db_config())
    except Exception as exc:
        raise ConnectionError(f"Nao foi possivel conectar ao banco de dados: {exc}")

def get_server_connection():
    try:
        return mysql.connector.connect(**_db_config(include_database=False))
    except Exception as exc:
        raise ConnectionError(f"Nao foi possivel conectar ao servidor MySQL: {exc}")


def close_connection():
    global _connection_pool
    _connection_pool = None


class _CursorContext:
    """Context manager that yields a dictionary cursor and closes both cursor and connection on exit."""

    def __init__(self, *, dictionary: bool = True):
        self._dictionary = dictionary
        self._conn = None
        self._cursor = None

    def __enter__(self):
        self._conn = get_connection()
        self._cursor = self._conn.cursor(dictionary=self._dictionary)
        return self._cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self._cursor.close()
        finally:
            self._conn.close()
        return False


def db_cursor(*, dictionary: bool = True):
    """Return a context manager that provides a cursor and auto-closes on exit.

    Usage:
        with db_cursor() as cur:
            cur.execute("SELECT ...")
            rows = cur.fetchall()
    """
    return _CursorContext(dictionary=dictionary)


class _TransactionContext:
    """Context manager that yields a cursor, commits on success, rolls back on error, and always closes."""

    def __init__(self, *, dictionary: bool = True):
        self._dictionary = dictionary
        self._conn = None
        self._cursor = None

    def __enter__(self):
        self._conn = get_connection()
        self._cursor = self._conn.cursor(dictionary=self._dictionary)
        return self._cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is None:
                self._conn.commit()
            else:
                self._conn.rollback()
        finally:
            try:
                self._cursor.close()
            finally:
                self._conn.close()
        return False


def db_transaction(*, dictionary: bool = True):
    """Context manager for write operations with auto-commit/rollback.

    Usage:
        with db_transaction() as cur:
            cur.execute("INSERT INTO ...")
            cur.execute("UPDATE ...")
    # auto-commits if no exception, rolls back on exception, always closes
    """
    return _TransactionContext(dictionary=dictionary)

if __name__ == "__main__":
    from utils.app_logger import log_error, log_info

    try:
        diagnostics = get_connection_diagnostics()
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SHOW TABLES;")
            tabelas = cast(list[Sequence[Any]], cursor.fetchall())

        log_info(
            "Modo de conexao: "
            f"{diagnostics['mode'], diagnostics['pool_enabled'], diagnostics['pool_initialized'], diagnostics.get('pool_name', '-'), diagnostics.get('pool_size', '-')}"
        )
        log_info(f"Conectado ao banco '{os.getenv('DB_NAME')}' em {os.getenv('DB_HOST')}")
        log_info(f"Tabelas encontradas ({len(tabelas)}):")
        for (nome,) in tabelas:
            log_info(f"  - {nome}")

        conn.close()
    except ConnectionError as exc:
        log_error("Erro de conexao.", exc)
    except Error as exc:
        log_error("Erro no banco de dados.", exc)
    finally:
        close_connection()
