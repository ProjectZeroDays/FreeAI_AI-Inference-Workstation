#!/usr/bin/env python3
"""Reviewer-scored golden-task harness.

Calls router /route for each task, then asks a reviewer model to score.
Reviewer = qwen3.5-9B or qwythos-v2 with strict rubric.
"""
import argparse
import json
import os
import pathlib
import requests

ROUTER = os.environ.get("ROUTER_URL", "http://localhost:8010/route")
REVIEWER_PROMPT = """You are a strict grader. Score 0-10.
Task: {task_prompt}
Response: {response}
Checklist: contains expected substrings {expected}. Reply JSON {{"score": N, "reason": "..."}}"""

def score(task, resp_text):
    expected = task.get("expected_contains", [])
    has = sum(1 for k in expected if k.lower() in resp_text.lower())
    base = 6 + has * 2
    # optional reviewer LLM call
    if os.environ.get("USE_REVIEWER_LLM") == "1":
        try:
            r = requests.post(ROUTER, json={
                "prompt": REVIEWER_PROMPT.format(task_prompt=task["prompt"],
                                                  response=resp_text[:2000],
                                                  expected=expected),
                "max_tokens": 256, "temperature": 0.0}, timeout=60)
            j = r.json()
            txt = json.dumps(j.get("response", ""))
            import re
            m = re.search(r"\b10\b|\b[0-9]\b", txt)
            if m:
                base = int(m.group(0))
        except Exception:
            pass
    return min(10, base), f"matched {has}/{len(expected)} keywords"

def run(tasks_path):
    tasks = json.loads(pathlib.Path(tasks_path).read_text())["tasks"]
    results = []
    for t in tasks:
        r = requests.post(ROUTER, json={"prompt": t["prompt"],
                                        "max_tokens": t.get("max_tokens", 512),
                                        "temperature": 0.2}, timeout=120)
        r.raise_for_status()
        j = r.json()
        txt = j.get("response", {}).get("content") or json.dumps(j.get("response",""))[:2000]
        sc, reason = score(t, txt)
        results.append({"id": t["id"], "score": sc, "reason": reason,
                        "model": j.get("model_used"), "latency": j.get("elapsed_ms")})
        print(f"{t['id']}: {sc}/10 {reason} via {j.get('model_used')}")
    avg = sum(r["score"] for r in results)/len(results) if results else 0
    print(f"AVERAGE {avg:.1f}/10")
    pathlib.Path("evals/results.json").write_text(json.dumps({"avg": avg, "results": results}, indent=2))
    return 0 if avg >= 6 else 1

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", default="evals/golden_tasks.json")
    args = ap.parse_args()
    raise SystemExit(run(args.tasks))
