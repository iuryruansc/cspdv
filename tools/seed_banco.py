from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from database.connection import close_connection
from database.bootstrap import bootstrap_database
from database.seeds.runner import run_pending_seeds

def main() -> int:
    if bootstrap_database():
        print("Banco de dados criado automaticamente.")
    applied = run_pending_seeds()
    if applied:
        print("Seeds aplicados:")
        for version in applied:
            print(f"- {version}")
    else:
        print("Nenhum seed pendente.")
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    finally:
        close_connection()
