import os
from typing import Any, Sequence, cast

import mysql.connector
from dotenv import load_dotenv
from mysql.connector import Error, pooling

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

_connection_pool = None

def _db_config():
    host = os.getenv("DB_HOST", "127.0.0.1").strip()

    if host.lower() == "localhost":
        host = "127.0.0.1"

    return {
        "host": host,
        "port": int(os.getenv("DB_PORT", 3306)),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_NAME"),
        "charset": "utf8mb4",
        "autocommit": False,
        "connection_timeout": int(os.getenv("DB_CONNECTION_TIMEOUT", 5)),
        "use_pure": True,
    }

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
        except Error as exc:
            raise ConnectionError(f"Não foi possível criar o pool de conexões: {exc}")

    return _connection_pool

def get_connection():
    try:
        if _usar_pool():
            return get_connection_pool().get_connection()
        return mysql.connector.connect(**_db_config())
    except Error as exc:
        raise ConnectionError(f"Não foi possível conectar ao banco de dados: {exc}")

def close_connection():
    global _connection_pool
    _connection_pool = None

if __name__ == "__main__":
    from utils.app_logger import log_error, log_info

    try:
        diagnostics = get_connection_diagnostics()
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SHOW TABLES;")
            tabelas = cast(list[Sequence[Any]], cursor.fetchall())

        log_info(
            "Modo de conexão: "
            f"{diagnostics['mode'], diagnostics['pool_enabled'], diagnostics['pool_initialized'], diagnostics.get('pool_name', '-'), diagnostics.get('pool_size', '-')}"
        )
        log_info(f"Conectado ao banco '{os.getenv('DB_NAME')}' em {os.getenv('DB_HOST')}")
        log_info(f"Tabelas encontradas ({len(tabelas)}):")
        for (nome,) in tabelas:
            log_info(f"  - {nome}")

        conn.close()
    except ConnectionError as exc:
        log_error("Erro de conexão.", exc)
    except Error as exc:
        log_error("Erro no banco de dados.", exc)
    finally:
        close_connection()
