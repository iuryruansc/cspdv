from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import patch

from database.maintenance import validator


@dataclass
class FakeCursor:
    tables: list[str]
    migrations: list[str]
    seeds: list[str]
    present_values: set[tuple[str, str, str]]

    def execute(self, operation: str, params=()) -> None:
        sql = " ".join(operation.strip().split()).upper()
        self._rows = []

        if sql.startswith("SHOW TABLES"):
            self._rows = [(table,) for table in self.tables]
            return
        if sql.startswith("SELECT VERSION FROM SCHEMA_MIGRATIONS"):
            self._rows = [(version,) for version in self.migrations]
            return
        if sql.startswith("SELECT VERSION FROM SCHEMA_SEEDS"):
            self._rows = [(version,) for version in self.seeds]
            return
        if sql.startswith("SELECT 1 FROM "):
            table_name = sql.split("FROM ", 1)[1].split(" ", 1)[0].lower()
            normalized_value = str(params[0]).strip().upper() if params else ""
            if table_name == "clientes":
                key = (table_name, "nome_sistema", normalized_value)
            elif table_name == "cargos":
                key = (table_name, "nome_cargo", normalized_value)
            elif table_name == "perfis":
                key = (table_name, "nome", normalized_value)
            elif table_name == "permissoes":
                key = (table_name, "chave", normalized_value)
            elif table_name == "formas_pagamento":
                key = (table_name, "nome", normalized_value)
            elif table_name == "unidades_medida":
                key = (table_name, "sigla", normalized_value)
            else:
                key = (table_name, "tipo_padrao", normalized_value)
            self._rows = [(1,)] if key in self.present_values else []

    def fetchall(self):
        return list(getattr(self, "_rows", []))

    def close(self) -> None:
        return None


class FakeConnection:
    def __init__(self, cursor: FakeCursor) -> None:
        self._cursor = cursor

    def cursor(self):
        return self._cursor

    def close(self) -> None:
        return None


def test_validate_database_baseline_retorna_ok_quando_base_esta_completa():
    tables = list(validator.REQUIRED_TABLES)
    present_values = {
        ("clientes", "nome_sistema", "CONSUMIDOR FINAL"),
        ("cargos", "nome_cargo", "ADMINISTRADOR"),
        ("perfis", "nome", "ADMIN MASTER"),
        ("permissoes", "chave", "SISTEMA.MASTER"),
        ("permissoes", "chave", "VENDAS.PDV"),
        ("permissoes", "chave", "ESTOQUE.GERENCIAR"),
        ("permissoes", "chave", "FINANCEIRO.TOTAL"),
        ("permissoes", "chave", "RELATORIOS.VER"),
        ("formas_pagamento", "nome", "DINHEIRO"),
        ("formas_pagamento", "nome", "PIX"),
        ("formas_pagamento", "nome", "CARTAO DEBITO"),
        ("formas_pagamento", "nome", "CARTAO CREDITO"),
        ("formas_pagamento", "nome", "VALE REFEICAO"),
        ("formas_pagamento", "nome", "CHEQUE"),
        ("unidades_medida", "sigla", "UN"),
        ("unidades_medida", "sigla", "CX"),
        ("unidades_medida", "sigla", "FD"),
        ("caixa_motivos", "tipo_padrao", "SANGRIA"),
        ("caixa_motivos", "tipo_padrao", "SUPRIMENTO"),
        ("caixa_motivos", "tipo_padrao", "TROCO"),
    }
    cursor = FakeCursor(
        tables=tables,
        migrations=["20260517_001", "20260517_002"],
        seeds=["20260517_001", "20260517_002", "20260517_003"],
        present_values=present_values,
    )

    with patch("database.maintenance.validator.get_connection", return_value=FakeConnection(cursor)), patch(
        "database.maintenance.validator._discover_migrations",
        return_value=[
            type("Migration", (), {"version": "20260517_001"})(),
            type("Migration", (), {"version": "20260517_002"})(),
        ],
    ), patch(
        "database.maintenance.validator._discover_seeds",
        return_value=[
            type("Seed", (), {"version": "20260517_001"})(),
            type("Seed", (), {"version": "20260517_002"})(),
            type("Seed", (), {"version": "20260517_003"})(),
        ],
    ):
        report = validator.validate_database_baseline()

    assert report.ok is True
    assert report.missing_tables == []
    assert report.pending_migrations == []
    assert report.pending_seeds == []
    assert report.missing_seed_items == []


def test_validate_database_baseline_aponta_pendencias():
    cursor = FakeCursor(
        tables=["schema_migrations", "config_empresa", "clientes"],
        migrations=["20260517_001"],
        seeds=[],
        present_values=set(),
    )

    with patch("database.maintenance.validator.get_connection", return_value=FakeConnection(cursor)), patch(
        "database.maintenance.validator._discover_migrations",
        return_value=[
            type("Migration", (), {"version": "20260517_001"})(),
            type("Migration", (), {"version": "20260517_002"})(),
        ],
    ), patch(
        "database.maintenance.validator._discover_seeds",
        return_value=[
            type("Seed", (), {"version": "20260517_001"})(),
        ],
    ):
        report = validator.validate_database_baseline()

    assert report.ok is False
    assert "schema_seeds" in report.missing_tables
    assert "20260517_002" in report.pending_migrations
    assert "20260517_001" in report.pending_seeds
    assert "cliente sistema: Consumidor Final" in report.missing_seed_items

