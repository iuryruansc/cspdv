from dataclasses import dataclass
from unittest.mock import patch

from database.migrations import runner


@dataclass
class _FakeCursor:
    versions: list[tuple[str]]

    def __post_init__(self):
        self.commands: list[tuple[str, tuple | None]] = []

    def execute(self, sql, params=None):
        self.commands.append((sql, params))

    def fetchall(self):
        return list(self.versions)

    def close(self):
        return None


class _FakeConnection:
    def __init__(self, cursor):
        self._cursor = cursor
        self.committed = False
        self.rolled_back = False

    def cursor(self):
        return self._cursor

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def close(self):
        return None


class TestMigrationRunner:
    def test_nao_aplica_quando_nao_ha_pendencias(self):
        cursor = _FakeCursor([("20260517_001",)])
        conn = _FakeConnection(cursor)
        migration = runner.Migration(
            version="20260517_001",
            description="teste",
            apply=lambda _cursor: None,
        )

        with patch("database.migrations.runner.get_connection", return_value=conn), patch(
            "database.migrations.runner._discover_migrations",
            return_value=[migration],
        ):
            applied = runner.run_pending_migrations()

        assert applied == []
        assert conn.committed is True

    def test_aplica_e_registra_migration_pendente(self):
        cursor = _FakeCursor([])
        conn = _FakeConnection(cursor)
        applied_by_migration: list[str] = []

        def _apply(_cursor):
            applied_by_migration.append("ok")

        migration = runner.Migration(
            version="20260517_999",
            description="migration de teste",
            apply=_apply,
        )

        with patch("database.migrations.runner.get_connection", return_value=conn), patch(
            "database.migrations.runner._discover_migrations",
            return_value=[migration],
        ):
            applied = runner.run_pending_migrations()

        assert applied == ["20260517_999"]
        assert applied_by_migration == ["ok"]
        assert any("INSERT INTO schema_migrations" in command[0] for command in cursor.commands)
        assert conn.committed is True
