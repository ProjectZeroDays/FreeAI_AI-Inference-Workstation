"""Golden-task evaluation runner.

Loads evals/golden_tasks.json, sends each prompt to the router /route,
scores results with three methods (exact, string, LLM-judge), and writes
a JSON report.

CLI:
    python evals/run_eval.py [--json] [--category coding] [--model gpt-4o]
"""
import argparse
import hashlib
import json
import math
import os
import re
import sys
import time
from pathlib import Path

ROUTER_URL = os.environ.get("ROUTER_URL", "http://localhost:8010/route")
TASKS_PATH = Path(__file__).parent / "golden_tasks.json"
HISTORY_PATH = Path(__file__).parent / "history.jsonl"
REPORT_PATH = Path(__file__).parent / "report.json"


# ── Scoring methods ──────────────────────────────────────────────

def score_exact(expected: str, actual: str) -> tuple[float, str]:
    """Exact string match (case-insensitive, whitespace-normalised)."""
    e = expected.strip().lower()
    a = actual.strip().lower()
    if e == a:
        return 1.0, "exact match"
    # Numeric tolerance for math answers
    try:
        if abs(float(e) - float(a)) < 1e-6:
            return 1.0, "numeric match"
    except (ValueError, TypeError):
        pass
    # Token overlap
    e_tok = set(e.split())
    a_tok = set(a.split())
    if e_tok and a_tok:
        overlap = len(e_tok & a_tok) / max(len(e_tok), len(a_tok))
        return round(overlap, 3), f"token overlap {overlap:.2f}"
    return 0.0, "no match"


def _cosine_similarity(a: str, b: str) -> float:
    """Bag-of-words cosine similarity between two strings."""
    def vec(s: str) -> dict[str, int]:
        from collections import Counter
        return dict(Counter(re.findall(r"\b\w+\b", s.lower())))

    va, vb = vec(a), vec(b)
    if not va or not vb:
        return 0.0
    inter = set(va) & set(vb)
    dot = sum(va[w] * vb[w] for w in inter)
    na = math.sqrt(sum(v * v for v in va.values()))
    nb = math.sqrt(sum(v * v for v in vb.values()))
    if na == 0 or nb == 0:
        return 0.0
    return round(dot / (na * nb), 4)


def score_string(expected: str, actual: str, threshold: float = 0.4) -> tuple[float, str]:
    """String similarity scoring (cosine + substring bonus)."""
    cos = _cosine_similarity(expected, actual)
    # Substring bonus for short expected answers
    if expected and expected.lower() in actual.lower():
        cos = max(cos, 0.9)
    reason = f"cosine={cos:.3f}"
    return round(cos, 4), reason


def score_llm(task: dict, actual: str, router_url: str) -> tuple[float, str]:
    """LLM-judge scoring via /route endpoint."""
    criteria = task.get("llm_criteria", "")
    if not criteria:
        return 0.5, "no criteria — auto-pass"
    judge_prompt = (
        f"Grade this response against the criteria below. "
        f"Return ONLY a JSON object with keys 'score' (0.0-1.0) and 'reason' (one sentence).\n\n"
        f"Criteria: {criteria}\n\n"
        f"Response:\n{actual[:2000]}"
    )
    try:
        import requests
        r = requests.post(
            router_url,
            json={"prompt": judge_prompt, "max_tokens": 128, "temperature": 0.0},
            timeout=60,
        )
        r.raise_for_status()
        j = r.json()
        text = j.get("response", {}).get("content", "") or json.dumps(j.get("response", ""))
        m = re.search(r"\b(\d+\.\d+|\d+)\b", text)
        if m:
            val = float(m.group(1))
            return round(min(1.0, max(0.0, val)), 4), f"llm judge: {val:.2f}"
        return 0.5, f"llm parse fail: {text[:100]}"
    except Exception as exc:
        return 0.5, f"llm judge error: {exc}"


def score_task(task: dict, response: str) -> tuple[float, str]:
    """Route to the correct scoring method."""
    method = task.get("scoring_method", "string")
    expected = task.get("expected_answer", "")
    if method == "exact":
        return score_exact(expected, response)
    elif method == "llm":
        return score_llm(task, response, ROUTER_URL)
    else:
        return score_string(expected, response)


# ── Router client ────────────────────────────────────────────────

def call_router(prompt: str, model: str | None = None, max_tokens: int = 512) -> dict:
    """Send prompt to the router and return the response dict."""
    import requests
    payload: dict = {"prompt": prompt, "max_tokens": max_tokens, "temperature": 0.2}
    if model:
        payload["model"] = model
    started = time.monotonic()
    r = requests.post(ROUTER_URL, json=payload, timeout=120)
    elapsed_ms = int((time.monotonic() - started) * 1000)
    r.raise_for_status()
    j = r.json()
    txt = j.get("response", {}).get("content") or json.dumps(j.get("response", ""))
    return {
        "model": j.get("model_used", "unknown"),
        "latency_ms": elapsed_ms,
        "content": txt[:3000],
    }


# ── Main evaluation loop ─────────────────────────────────────────

def run_eval(tasks_path: str, category: str | None, model: str | None, json_output: bool) -> dict:
    data = json.loads(Path(tasks_path).read_text(encoding="utf-8"))
    tasks = data["tasks"]
    if category:
        tasks = [t for t in tasks if t.get("category") == category]

    run_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
    results = []
    for task in tasks:
        print(f"  [{task['id']}] {task['category']}/{task['difficulty']} ... ", end="", flush=True)
        resp = call_router(task["prompt"], model=model, max_tokens=task.get("max_tokens", 512))
        score, reason = score_task(task, resp["content"])
        entry = {
            "id": task["id"],
            "category": task["category"],
            "difficulty": task["difficulty"],
            "prompt": task["prompt"],
            "expected": task.get("expected_answer", "")[:200],
            "response": resp["content"][:500],
            "score": round(score, 4),
            "reason": reason,
            "model_used": resp["model"],
            "latency_ms": resp["latency_ms"],
        }
        results.append(entry)
        label = "PASS" if score >= 0.7 else "FAIL"
        print(f"{score:.2f} [{label}] {reason}")

    # Aggregate
    cat_avg: dict[str, list[float]] = {}
    diff_avg: dict[str, list[float]] = {}
    for e in results:
        cat_avg.setdefault(e["category"], []).append(e["score"])
        diff_avg.setdefault(e["difficulty"], []).append(e["score"])
    category_avg = {k: round(sum(v) / len(v), 4) for k, v in cat_avg.items()}
    difficulty_avg = {k: round(sum(v) / len(v), 4) for k, v in diff_avg.items()}
    overall = round(sum(e["score"] for e in results) / len(results), 4) if results else 0.0

    report = {
        "run_id": run_id,
        "timestamp": time.time(),
        "total_tasks": len(results),
        "overall_score": overall,
        "category_avg": category_avg,
        "difficulty_avg": difficulty_avg,
        "results": results,
    }

    # Write JSON report
    out_path = REPORT_PATH if json_output else Path(__file__).parent / "report.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    # Append to history JSONL
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "run_id": run_id,
            "timestamp": report["timestamp"],
            "overall_score": overall,
            "total_tasks": len(results),
            "category_avg": category_avg,
            "difficulty_avg": difficulty_avg,
        }, ensure_ascii=False) + "\n")

    print(f"\nOverall: {overall:.3f}  |  Categories: {category_avg}  |  Difficulty: {difficulty_avg}")
    print(f"Report written to {out_path}")
    return report


# ── CLI ──────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Golden-task evaluation harness")
    ap.add_argument("--tasks", default=str(TASKS_PATH), help="Path to golden_tasks.json")
    ap.add_argument("--category", default=None, help="Filter by category (coding|reasoning|knowledge|creativity)")
    ap.add_argument("--model", default=None, help="Override model via router")
    ap.add_argument("--json", action="store_true", help="Pretty-print report to stdout")
    args = ap.parse_args()

    report = run_eval(args.tasks, args.category, args.model, args.json)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    sys.exit(0 if report["overall_score"] >= 0.6 else 1)


if __name__ == "__main__":
    main()
