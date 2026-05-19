from __future__ import annotations

from unittest.mock import Mock, patch

from database.bootstrap import bootstrap_database


def test_bootstrap_database_nao_cria_quando_schema_ja_existe():
    cursor = Mock()
    cursor.fetchall.return_value = [("cspdv",)]
    conn = Mock()
    conn.cursor.return_value = cursor

    with patch("database.bootstrap.get_connection_diagnostics", return_value={"database": "cspdv"}), patch(
        "database.bootstrap.get_server_connection",
        return_value=conn,
    ):
        created = bootstrap_database()

    assert created is False
    cursor.execute.assert_called_once_with(
        "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = %s",
        ("cspdv",),
    )
    conn.commit.assert_not_called()


def test_bootstrap_database_cria_schema_quando_ausente():
    cursor = Mock()
    cursor.fetchall.return_value = []
    conn = Mock()
    conn.cursor.return_value = cursor

    with patch("database.bootstrap.get_connection_diagnostics", return_value={"database": "cspdv"}), patch(
        "database.bootstrap.get_server_connection",
        return_value=conn,
    ):
        created = bootstrap_database()

    assert created is True
    assert cursor.execute.call_count == 2
    cursor.execute.assert_any_call(
        "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = %s",
        ("cspdv",),
    )
    cursor.execute.assert_any_call(
        "CREATE DATABASE `cspdv` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    )
    conn.commit.assert_called_once()


def test_bootstrap_database_exige_db_name():
    with patch("database.bootstrap.get_connection_diagnostics", return_value={"database": ""}):
        try:
            bootstrap_database()
        except ConnectionError as exc:
            assert "DB_NAME" in str(exc)
        else:
            raise AssertionError("Era esperado ConnectionError quando DB_NAME esta vazio.")
