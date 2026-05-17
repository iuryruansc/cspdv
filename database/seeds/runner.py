from __future__ import annotations

import importlib
import pkgutil
from dataclasses import dataclass
from typing import Any, Callable, List, Mapping, Protocol, Sequence, TypeAlias, cast

from database.connection import get_connection

SeedParams: TypeAlias = Sequence[Any] | Mapping[str, Any]
SeedRow: TypeAlias = Sequence[Any] | Mapping[str, Any]

class SeedCursorLike(Protocol):
    def execute(self, operation: str, params: SeedParams = ...) -> None: ...
    def fetchall(self) -> Sequence[SeedRow]: ...

@dataclass(frozen=True)
class Seed:
    version: str
    description: str
    apply: Callable[[SeedCursorLike], None]

def _discover_seeds() -> List[Seed]:
    package_name = "database.seeds.versions"
    package = importlib.import_module(package_name)
    seeds: List[Seed] = []

    for module_info in pkgutil.iter_modules(package.__path__):
        if module_info.ispkg:
            continue
        module = importlib.import_module(f"{package_name}.{module_info.name}")
        version = getattr(module, "VERSION", None)
        description = getattr(module, "DESCRIPTION", None)
        apply = getattr(module, "apply", None)
        if not version or not description or not callable(apply):
            continue
        seeds.append(
            Seed(
                version=str(version),
                description=str(description),
                apply=cast(Callable[[SeedCursorLike], None], apply),
            )
        )

    seeds.sort(key=lambda item: item.version)
    return seeds

def _ensure_schema_seeds_table(cursor: SeedCursorLike) -> None:
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_seeds (
            version VARCHAR(64) NOT NULL PRIMARY KEY,
            description VARCHAR(255) NOT NULL,
            applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

def _applied_versions(cursor: SeedCursorLike) -> set[str]:
    _ensure_schema_seeds_table(cursor)
    cursor.execute("SELECT version FROM schema_seeds ORDER BY version")
    rows = cursor.fetchall()
    versions: set[str] = set()
    for row in rows:
        if isinstance(row, Sequence) and not isinstance(row, (str, bytes, bytearray)) and row:
            versions.add(str(row[0]))
        elif isinstance(row, Mapping) and "version" in row:
            versions.add(str(row["version"]))
    return versions

def run_pending_seeds() -> list[str]:
    conn = get_connection()
    cursor = conn.cursor()
    applied_now: list[str] = []
    try:
        already_applied = _applied_versions(cast(SeedCursorLike, cursor))
        for seed in _discover_seeds():
            if seed.version in already_applied:
                continue
            seed.apply(cast(SeedCursorLike, cursor))
            cursor.execute(
                """
                INSERT INTO schema_seeds (version, description, applied_at)
                VALUES (%s, %s, NOW())
                """,
                (seed.version, seed.description),
            )
            applied_now.append(seed.version)
        conn.commit()
        return applied_now
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()
