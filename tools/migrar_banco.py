from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from database.connection import close_connection
from database.migrations.runner import run_pending_migrations

def main() -> int:
    applied = run_pending_migrations()
    if applied:
        print("Migrations aplicadas:")
        for version in applied:
            print(f" - {version}")
    else:
        print("Nenhuma migration pendente.")
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    finally:
        close_connection()
