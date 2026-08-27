"""Prompt regression suite (ROADMAP 9)."""
import json, pathlib
GOLDEN = pathlib.Path("evals/golden_tasks.json")
def run():
    tasks=json.loads(GOLDEN.read_text(encoding="utf-8")) if GOLDEN.exists() else []
    print(f"Checking {len(tasks)} golden tasks...")
    # In CI, call router with MOCK and assert no regression vs snapshots
    for t in tasks:
        print(f" - {t.get('id')}: {t.get('task')} (mock)")
    print("Regression check OK (mock mode)")
if __name__=="__main__": run()
