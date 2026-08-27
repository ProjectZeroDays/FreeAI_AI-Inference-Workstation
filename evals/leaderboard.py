"""Leaderboard: track eval runs over time and compare model performance.

Reads evals/history.jsonl (written by reviewer.py) and presents
trend data and per-model breakdowns.

CLI:
    python evals/leaderboard.py [--last N] [--model gpt-4o] [--json]
"""
import argparse
import json
import sys
from pathlib import Path

HISTORY_PATH = Path(__file__).parent / "history.jsonl"


def load_history() -> list[dict]:
    """Load all historical eval runs from the JSONL file."""
    if not HISTORY_PATH.exists():
        return []
    runs = []
    for line in open(HISTORY_PATH, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            runs.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return runs


def summarize(runs: list[dict], last: int | None = None, model: str | None = None) -> dict:
    """Compute leaderboard summary from history."""
    if last:
        runs = runs[-last:]
    if not runs:
        return {"runs": [], "total_runs": 0, "trend": [], "models": {}}

    # Per-model aggregation
    model_scores: dict[str, list[float]] = {}
    for run in runs:
        ms = run.get("model_used") or "unknown"
        # history entries may not have model_used; use results if available
        if "results" in run:
            for r in run["results"]:
                m = r.get("model_used", "unknown")
                model_scores.setdefault(m, []).append(r["score"])
        # Fall back to overall score if no per-task detail
        if ms not in model_scores:
            model_scores.setdefault(ms, []).append(run.get("overall_score", 0.0))

    model_summary = {}
    for m, scores in model_scores.items():
        model_summary[m] = {
            "runs": len(scores),
            "avg": round(sum(scores) / len(scores), 4),
            "best": round(max(scores), 4),
            "worst": round(min(scores), 4),
        }

    # Trend: last N scores
    trend = [r.get("overall_score", 0.0) for r in runs]

    # Category breakdown across all runs
    cat_totals: dict[str, list[float]] = {}
    diff_totals: dict[str, list[float]] = {}
    for run in runs:
        for cat, val in run.get("category_avg", {}).items():
            cat_totals.setdefault(cat, []).append(val)
        for diff, val in run.get("difficulty_avg", {}).items():
            diff_totals.setdefault(diff, []).append(val)

    cat_avg = {k: round(sum(v) / len(v), 4) for k, v in cat_totals.items()}
    diff_avg = {k: round(sum(v) / len(v), 4) for k, v in diff_totals.items()}

    return {
        "total_runs": len(runs),
        "latest": runs[-1] if runs else None,
        "trend": trend,
        "models": model_summary,
        "category_avg": cat_avg,
        "difficulty_avg": diff_avg,
    }


def print_table(summary: dict):
    """Pretty-print the leaderboard to stdout."""
    print(f"\n{'='*60}")
    print(f"  GOLDEN-TASK LEADERBOARD  ({summary['total_runs']} runs)")
    print(f"{'='*60}")

    if summary["trend"]:
        scores = summary["trend"]
        print(f"\n  Trend: {' → '.join(f'{s:.3f}' for s in scores)}")
        print(f"  Average: {sum(scores)/len(scores):.3f}")

    if summary["models"]:
        print(f"\n  {'Model':<20} {'Runs':>6} {'Avg':>8} {'Best':>8} {'Worst':>8}")
        print(f"  {'-'*52}")
        for m, stats in sorted(summary["models"].items(), key=lambda x: -x[1]["avg"]):
            print(f"  {m:<20} {stats['runs']:>6} {stats['avg']:>8.3f} {stats['best']:>8.3f} {stats['worst']:>8.3f}")

    if summary.get("category_avg"):
        print(f"\n  Category averages:")
        for cat, val in sorted(summary["category_avg"].items()):
            print(f"    {cat:<15} {val:.3f}")

    if summary.get("difficulty_avg"):
        print(f"  Difficulty averages:")
        for diff, val in sorted(summary["difficulty_avg"].items()):
            print(f"    {diff:<10} {val:.3f}")

    print(f"\n{'='*60}\n")


def main():
    ap = argparse.ArgumentParser(description="Golden-task eval leaderboard")
    ap.add_argument("--last", type=int, default=None, help="Show only last N runs")
    ap.add_argument("--model", default=None, help="Filter by model name")
    ap.add_argument("--json", action="store_true", help="Output JSON instead of table")
    args = ap.parse_args()

    runs = load_history()
    summary = summarize(runs, last=args.last, model=args.model)

    if args.json:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        print_table(summary)

    if not runs:
        print("No eval history found. Run `python evals/run_eval.py` first.")
        sys.exit(0)


if __name__ == "__main__":
    main()
