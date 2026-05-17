from __future__ import annotations

import importlib
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Protocol, Sequence, TypeAlias, cast

from database.connection import get_connection
from database.migrations.runner import _discover_migrations
from database.seeds.runner import _discover_seeds

_seed_operational = importlib.import_module("database.seeds.versions.20260517_001_operational_master_data")
_seed_access = importlib.import_module("database.seeds.versions.20260517_002_access_master_data")
_seed_consumidor = importlib.import_module("database.seeds.versions.20260517_003_consumidor_final_client")

FORMAS_PAGAMENTO = cast(list[dict[str, Any]], _seed_operational.FORMAS_PAGAMENTO)
UNIDADES = cast(list[dict[str, Any]], _seed_operational.UNIDADES)
CAIXA_MOTIVOS = cast(list[dict[str, Any]], _seed_operational.CAIXA_MOTIVOS)
CARGO_ADMIN = cast(str, _seed_access.CARGO_ADMIN)
PERFIL_MASTER = cast(dict[str, Any], _seed_access.PERFIL_MASTER)
PERMISSOES_BASE = cast(list[dict[str, Any]], _seed_access.PERMISSOES_BASE)
CONSUMIDOR_FINAL = cast(dict[str, Any], _seed_consumidor.CONSUMIDOR_FINAL)

ValidationParams: TypeAlias = Sequence[Any] | Mapping[str, Any]
ValidationRow: TypeAlias = Sequence[Any] | Mapping[str, Any]

REQUIRED_TABLES = (
    "schema_migrations",
    "schema_seeds",
    "config_empresa",
    "clientes",
    "formas_pagamento",
    "unidades_medida",
    "caixa_motivos",
    "cargos",
    "perfis",
    "permissoes",
    "perfil_permissoes",
)

class ValidationCursorLike(Protocol):
    def execute(self, operation: str, params: ValidationParams = ...) -> None: ...
    def fetchall(self) -> Sequence[ValidationRow]: ...

@dataclass(frozen=True)
class ValidationReport:
    missing_tables: list[str]
    pending_migrations: list[str]
    pending_seeds: list[str]
    missing_seed_items: list[str]
    total_tables: int

    @property
    def ok(self) -> bool:
        return not (
            self.missing_tables
            or self.pending_migrations
            or self.pending_seeds
            or self.missing_seed_items
        )

def _rows(cursor: ValidationCursorLike) -> Sequence[ValidationRow]:
    return cast(Sequence[ValidationRow], cursor.fetchall())

def _first_value(row: ValidationRow | None) -> Any | None:
    if row is None:
        return None
    if isinstance(row, Mapping):
        return next(iter(row.values()), None)
    if isinstance(row, Sequence) and not isinstance(row, (str, bytes, bytearray)) and row:
        return row[0]
    return None

def _table_names(cursor: ValidationCursorLike) -> set[str]:
    cursor.execute("SHOW TABLES")
    tables: set[str] = set()
    for row in _rows(cursor):
        value = _first_value(row)
        if value is not None:
            tables.add(str(value))
    return tables

def _applied_versions(cursor: ValidationCursorLike, registry_table: str) -> set[str]:
    cursor.execute(f"SELECT version FROM {registry_table} ORDER BY version")
    versions: set[str] = set()
    for row in _rows(cursor):
        value = _first_value(row)
        if value is not None:
            versions.add(str(value))
    return versions

def _row_exists(
    cursor: ValidationCursorLike,
    table_name: str,
    column_name: str,
    value: str,
    *,
    extra_where: str = "",
    extra_params: Iterable[Any] = (),
) -> bool:
    sql = (
        f"SELECT 1 FROM {table_name} "
        f"WHERE UPPER(TRIM({column_name})) = UPPER(TRIM(%s))"
    )
    if extra_where:
        sql += f" AND {extra_where}"
    sql += " LIMIT 1"
    params = (value, *tuple(extra_params))
    cursor.execute(sql, params)
    return bool(_rows(cursor))

def validate_database_baseline() -> ValidationReport:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        tables = _table_names(cast(ValidationCursorLike, cursor))
        missing_tables = [table for table in REQUIRED_TABLES if table not in tables]

        pending_migrations: list[str] = []
        if "schema_migrations" in tables:
            applied_migrations = _applied_versions(cast(ValidationCursorLike, cursor), "schema_migrations")
            pending_migrations = [
                migration.version
                for migration in _discover_migrations()
                if migration.version not in applied_migrations
            ]
        else:
            pending_migrations = [migration.version for migration in _discover_migrations()]

        pending_seeds: list[str] = []
        if "schema_seeds" in tables:
            applied_seeds = _applied_versions(cast(ValidationCursorLike, cursor), "schema_seeds")
            pending_seeds = [seed.version for seed in _discover_seeds() if seed.version not in applied_seeds]
        else:
            pending_seeds = [seed.version for seed in _discover_seeds()]

        missing_seed_items: list[str] = []
        if "clientes" in tables and not _row_exists(
            cast(ValidationCursorLike, cursor),
            "clientes",
            "nome",
            str(CONSUMIDOR_FINAL["nome"]),
            extra_where="cliente_sistema = 'S'",
        ):
            missing_seed_items.append("cliente sistema: Consumidor Final")

        if "cargos" in tables and not _row_exists(
            cast(ValidationCursorLike, cursor), "cargos", "nome_cargo", CARGO_ADMIN
        ):
            missing_seed_items.append(f"cargo base: {CARGO_ADMIN}")

        if "perfis" in tables and not _row_exists(
            cast(ValidationCursorLike, cursor), "perfis", "nome", str(PERFIL_MASTER["nome"])
        ):
            missing_seed_items.append(f"perfil base: {PERFIL_MASTER['nome']}")

        if "permissoes" in tables:
            for permissao in PERMISSOES_BASE:
                if not _row_exists(
                    cast(ValidationCursorLike, cursor),
                    "permissoes",
                    "chave",
                    str(permissao["chave"]),
                ):
                    missing_seed_items.append(f"permissao base: {permissao['chave']}")

        if "formas_pagamento" in tables:
            for forma in FORMAS_PAGAMENTO:
                if not _row_exists(
                    cast(ValidationCursorLike, cursor),
                    "formas_pagamento",
                    "nome",
                    str(forma["nome"]),
                ):
                    missing_seed_items.append(f"forma de pagamento base: {forma['nome']}")

        if "unidades_medida" in tables:
            for unidade in UNIDADES:
                if not _row_exists(
                    cast(ValidationCursorLike, cursor),
                    "unidades_medida",
                    "sigla",
                    str(unidade["sigla"]),
                ):
                    missing_seed_items.append(f"unidade base: {unidade['sigla']}")

        if "caixa_motivos" in tables:
            for motivo in CAIXA_MOTIVOS:
                if not _row_exists(
                    cast(ValidationCursorLike, cursor),
                    "caixa_motivos",
                    "tipo_padrao",
                    str(motivo["tipo_padrao"]),
                ):
                    missing_seed_items.append(f"motivo de caixa base: {motivo['tipo_padrao']}")

        return ValidationReport(
            missing_tables=missing_tables,
            pending_migrations=pending_migrations,
            pending_seeds=pending_seeds,
            missing_seed_items=missing_seed_items,
            total_tables=len(tables),
        )
    finally:
        cursor.close()
        conn.close()
