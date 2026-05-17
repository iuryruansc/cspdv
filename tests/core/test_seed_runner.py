from __future__ import annotations

import importlib
from unittest.mock import patch

from database.seeds import runner


class FakeCursor:
    def __init__(self) -> None:
        self.schema_seeds: set[str] = set()
        self._rows = []
        self.cargos: dict[str, int] = {}
        self.clientes: dict[str, int] = {}
        self.perfis: dict[str, int] = {}
        self.permissoes: dict[str, int] = {}
        self.perfil_permissoes: set[tuple[int, int]] = set()
        self._auto_id = 1

    def execute(self, operation: str, params=()) -> None:
        sql = " ".join(operation.strip().split()).upper()
        if sql.startswith("CREATE TABLE IF NOT EXISTS SCHEMA_SEEDS"):
            self._rows = []
            return
        if sql.startswith("SELECT VERSION FROM SCHEMA_SEEDS"):
            self._rows = [(version,) for version in sorted(self.schema_seeds)]
            return
        if sql.startswith("INSERT INTO SCHEMA_SEEDS"):
            self.schema_seeds.add(str(params[0]))
            self._rows = []
            return
        if "SELECT 1 FROM CLIENTES" in sql:
            cliente_nome = str(params[0]).strip().upper()
            self._rows = [(1,)] if cliente_nome in self.clientes else []
            return
        if sql.startswith("INSERT INTO CLIENTES"):
            self.clientes[str(params["nome"]).strip().upper()] = self._auto_id
            self._auto_id += 1
            self._rows = []
            return
        if "SELECT ID FROM CARGOS" in sql:
            cargo_id = self.cargos.get(str(params[0]).strip().upper())
            self._rows = [(cargo_id,)] if cargo_id else []
            return
        if sql.startswith("INSERT INTO CARGOS"):
            self.cargos[str(params[0]).strip().upper()] = self._auto_id
            self._auto_id += 1
            self._rows = []
            return
        if "SELECT ID FROM PERFIS" in sql:
            perfil_id = self.perfis.get(str(params[0]).strip().upper())
            self._rows = [(perfil_id,)] if perfil_id else []
            return
        if sql.startswith("INSERT INTO PERFIS"):
            self.perfis[str(params[0]).strip().upper()] = self._auto_id
            self._auto_id += 1
            self._rows = []
            return
        if "SELECT ID FROM PERMISSOES" in sql:
            permissao_id = self.permissoes.get(str(params[0]).strip().upper())
            self._rows = [(permissao_id,)] if permissao_id else []
            return
        if sql.startswith("INSERT INTO PERMISSOES"):
            self.permissoes[str(params[0]).strip().upper()] = self._auto_id
            self._auto_id += 1
            self._rows = []
            return
        if sql.startswith("SELECT 1 FROM PERFIL_PERMISSOES"):
            perfil_id, permissao_id = int(params[0]), int(params[1])
            self._rows = [(1,)] if (perfil_id, permissao_id) in self.perfil_permissoes else []
            return
        if sql.startswith("INSERT INTO PERFIL_PERMISSOES"):
            self.perfil_permissoes.add((int(params[0]), int(params[1])))
            self._rows = []
            return
        self._rows = []

    def fetchall(self):
        return list(self._rows)

    def close(self) -> None:
        return None


class FakeConnection:
    def __init__(self, cursor: FakeCursor) -> None:
        self._cursor = cursor
        self.committed = False
        self.rolled_back = False

    def cursor(self):
        return self._cursor

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True

    def close(self) -> None:
        return None


def test_run_pending_seeds_aplica_somente_pendentes():
    applied_calls: list[str] = []

    def apply_seed_1(_cursor) -> None:
        applied_calls.append("20260517_001")

    def apply_seed_2(_cursor) -> None:
        applied_calls.append("20260517_002")

    seeds = [
        runner.Seed("20260517_001", "Seed base", apply_seed_1),
        runner.Seed("20260517_002", "Seed extra", apply_seed_2),
    ]

    cursor = FakeCursor()
    cursor.schema_seeds.add("20260517_001")
    conn = FakeConnection(cursor)

    with patch("database.seeds.runner.get_connection", return_value=conn), patch(
        "database.seeds.runner._discover_seeds",
        return_value=seeds,
    ):
        applied = runner.run_pending_seeds()

    assert applied == ["20260517_002"]
    assert applied_calls == ["20260517_002"]
    assert conn.committed is True
    assert conn.rolled_back is False


def test_seed_access_master_data_eh_idempotente():
    module = importlib.import_module("database.seeds.versions.20260517_002_access_master_data")
    cursor = FakeCursor()

    module.apply(cursor)
    cargos_count = len(cursor.cargos)
    perfis_count = len(cursor.perfis)
    permissoes_count = len(cursor.permissoes)
    vinculos_count = len(cursor.perfil_permissoes)

    module.apply(cursor)

    assert len(cursor.cargos) == cargos_count == 1
    assert len(cursor.perfis) == perfis_count == 1
    assert len(cursor.permissoes) == permissoes_count == 5
    assert len(cursor.perfil_permissoes) == vinculos_count == 5


def test_seed_consumidor_final_eh_idempotente():
    module = importlib.import_module("database.seeds.versions.20260517_003_consumidor_final_client")
    cursor = FakeCursor()

    module.apply(cursor)
    clientes_count = len(cursor.clientes)

    module.apply(cursor)

    assert len(cursor.clientes) == clientes_count == 1
    assert "CONSUMIDOR FINAL" in cursor.clientes
