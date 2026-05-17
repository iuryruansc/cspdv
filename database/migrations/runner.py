from __future__ import annotations

import importlib
import pkgutil
from dataclasses import dataclass
from typing import Any, Callable, List, Mapping, Protocol, Sequence, TypeAlias, cast

from database.connection import get_connection

MigrationParams: TypeAlias = Sequence[Any] | Mapping[str, Any]
MigrationRow: TypeAlias = Sequence[Any] | Mapping[str, Any]

class CursorLike(Protocol):
    def execute(self, operation: str, params: MigrationParams = ...) -> None: ...
    def fetchall(self) -> Sequence[MigrationRow]: ...

@dataclass(frozen=True)
class Migration:
    version: str
    description: str
    apply: Callable[[CursorLike], None]

def _discover_migrations() -> List[Migration]:
    package_name = "database.migrations.versions"
    package = importlib.import_module(package_name)
    migrations: List[Migration] = []

    for module_info in pkgutil.iter_modules(package.__path__):
        if module_info.ispkg:
            continue
        module = importlib.import_module(f"{package_name}.{module_info.name}")
        version = getattr(module, "VERSION", None)
        description = getattr(module, "DESCRIPTION", None)
        apply = getattr(module, "apply", None)
        if not version or not description or not callable(apply):
            continue
        migrations.append(
            Migration(
                version=str(version),
                description=str(description),
                apply=cast(Callable[[CursorLike], None], apply),
            )
        )

    migrations.sort(key=lambda item: item.version)
    return migrations

def _ensure_schema_migrations_table(cursor: CursorLike) -> None:
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version VARCHAR(64) NOT NULL PRIMARY KEY,
            description VARCHAR(255) NOT NULL,
            applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

def _applied_versions(cursor: CursorLike) -> set[str]:
    _ensure_schema_migrations_table(cursor)
    cursor.execute("SELECT version FROM schema_migrations ORDER BY version")
    rows = cursor.fetchall()
    versions: set[str] = set()
    for row in rows:
        if isinstance(row, Sequence) and not isinstance(row, (str, bytes, bytearray)) and row:
            versions.add(str(row[0]))
        elif isinstance(row, Mapping) and "version" in row:
            versions.add(str(row["version"]))
    return versions

def run_pending_migrations() -> list[str]:
    conn = get_connection()
    cursor = conn.cursor()
    applied_now: list[str] = []
    try:
        already_applied = _applied_versions(cast(CursorLike, cursor))
        for migration in _discover_migrations():
            if migration.version in already_applied:
                continue
            migration.apply(cast(CursorLike, cursor))
            cursor.execute(
                """
                INSERT INTO schema_migrations (version, description, applied_at)
                VALUES (%s, %s, NOW())
                """,
                (migration.version, migration.description),
            )
            applied_now.append(migration.version)
        conn.commit()
        return applied_now
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()
