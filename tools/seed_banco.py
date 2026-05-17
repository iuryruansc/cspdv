from database.seeds.runner import run_pending_seeds

def main() -> int:
    applied = run_pending_seeds()
    if applied:
        print("Seeds aplicados:")
        for version in applied:
            print(f"- {version}")
    else:
        print("Nenhum seed pendente.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
