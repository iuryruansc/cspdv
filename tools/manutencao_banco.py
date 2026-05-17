from __future__ import annotations

import argparse
from typing import Iterable

from database.connection import close_connection
from database.maintenance.validator import ValidationReport, validate_database_baseline
from database.migrations.runner import run_pending_migrations
from database.seeds.runner import run_pending_seeds

def _print_versions(title: str, versions: Iterable[str], empty_message: str) -> None:
    items = list(versions)
    if not items:
        print(empty_message)
        return
    print(title)
    for version in items:
        print(f" - {version}")

def _print_validation(report: ValidationReport) -> None:
    print("Validacao de baseline:")
    print(f" - Tabelas detectadas: {report.total_tables}")
    print(f" - Tabelas ausentes: {len(report.missing_tables)}")
    print(f" - Migrations pendentes: {len(report.pending_migrations)}")
    print(f" - Seeds pendentes: {len(report.pending_seeds)}")
    print(f" - Itens base ausentes: {len(report.missing_seed_items)}")

    for table_name in report.missing_tables:
        print(f"   * tabela ausente: {table_name}")
    for version in report.pending_migrations:
        print(f"   * migration pendente: {version}")
    for version in report.pending_seeds:
        print(f"   * seed pendente: {version}")
    for item in report.missing_seed_items:
        print(f"   * dado base ausente: {item}")

    print("Status final: OK" if report.ok else "Status final: pendencias encontradas")

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Executa manutencao tecnica do banco: migrations, seeds e validacao de baseline."
    )
    parser.add_argument("--migrate", action="store_true", help="Aplica migrations pendentes.")
    parser.add_argument("--seed", action="store_true", help="Aplica seeds pendentes.")
    parser.add_argument("--validate", action="store_true", help="Valida baseline estrutural e dados-base.")
    args = parser.parse_args(argv)

    run_all = not any((args.migrate, args.seed, args.validate))
    should_migrate = args.migrate or run_all
    should_seed = args.seed or run_all
    should_validate = args.validate or run_all

    if should_migrate:
        applied = run_pending_migrations()
        _print_versions("Migrations aplicadas:", applied, "Nenhuma migration pendente.")

    if should_seed:
        applied = run_pending_seeds()
        _print_versions("Seeds aplicados:", applied, "Nenhum seed pendente.")

    if should_validate:
        report = validate_database_baseline()
        _print_validation(report)
        return 0 if report.ok else 1

    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    finally:
        close_connection()
