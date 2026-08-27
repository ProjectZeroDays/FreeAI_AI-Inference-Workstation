"""Skill monitoring daemon — watches requests and auto-creates skills.

This runs as a background process that:
  1. Listens for request activity via the proxy/memory APIs
  2. Detects recurring patterns across sessions
  3. Auto-generates SKILL.md files without prompting
  4. Notifies the dashboard of new skills

Usage:
    python skills/monitor.py              # start daemon
    python skills/monitor.py --once       # single pass
    python skills/monitor.py --watch      # watch mode (non-daemon)
"""
import json
import os
import signal
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).parent.parent
ACTIVITY_LOG = ROOT / "config" / "activity_log.jsonl"
PATTERN_STORE = ROOT / "config" / "skill_patterns.json"
SKILLS_DIR = ROOT / "skills"


def log_request(session_id, user_input, assistant_output="", task_type=None):
    """Log a request for pattern analysis."""
    entry = {
        "ts": int(time.time()),
        "session": session_id or "unknown",
        "user_input": user_input[:500],
        "assistant_output": assistant_output[:500],
        "task_type": task_type or detect_type(user_input),
    }
    ACTIVITY_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(ACTIVITY_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def detect_type(text):
    t = text.lower()
    if any(k in t for k in ["write", "create", "build", "implement", "code", "function"]):
        return "coding"
    if any(k in t for k in ["debug", "fix", "error", "bug", "traceback"]):
        return "debugging"
    if any(k in t for k in ["explain", "what is", "how does", "understand"]):
        return "learning"
    if any(k in t for k in ["review", "analyze", "assess", "evaluate"]):
        return "analysis"
    if any(k in t for k in ["test", "run tests", "verify", "check"]):
        return "testing"
    if any(k in t for k in ["deploy", "run server", "start", "build project"]):
        return "deployment"
    if any(k in t for k in ["refactor", "clean up", "improve", "optimize"]):
        return "refactoring"
    if any(k in t for k in ["doc", "readme", "document", "comment"]):
        return "documentation"
    return "general"


def analyze_and_create(min_occurrences=2, max_new=5):
    """One-shot: scan activity log, create skills for recurring patterns."""
    if not ACTIVITY_LOG.exists():
        return []

    entries = []
    for line in open(ACTIVITY_LOG, encoding="utf-8"):
        try:
            entries.append(json.loads(line.strip()))
        except (json.JSONDecodeError, OSError):
            continue

    # Group by type
    from collections import Counter, defaultdict
    by_type = defaultdict(list)
    for e in entries:
        by_type[e.get("task_type", "general")].append(e)

    created = []
    pattern_store = load_pattern_store()
    existing = set(pattern_store.get("created_skills", []))

    for task_type, tasks in by_type.items():
        if len(tasks) < min_occurrences:
            continue
        kw_counts = Counter()
        for t in tasks:
            for w in __import__('re').findall(r'\b\w{3,}\b', t.get("user_input", "").lower()):
                if w not in {"there", "their", "through", "another", "where", "about", "after"}:
                    kw_counts[w] += 1
        for kw, count in kw_counts.most_common(10):
            if count < min_occurrences:
                continue
            pattern_key = f"{task_type}:{kw}"
            if pattern_key in existing:
                continue
            if len(created) >= max_new:
                return created
            matching = [t for t in tasks if kw in t.get("user_input", "").lower()]
            skill_name = f"{task_type}-{kw}"
            skill_name = __import__('re').sub(r'\s+', '-', skill_name).lower()
            sample = matching[0].get("user_input", "")[:100] if matching else ""
            content = f"""---
name: {skill_name}
description: >
  Handles {task_type} tasks involving {kw}.
  Auto-discovered from {len(matching)} recurring requests.
triggers:
  - {kw}
  - {task_type}
metadata:
  auto_generated: true
  source: activity_monitor
  created_at: "{time.strftime('%Y-%m-%d %H:%M:%S')}"
  occurrences: {len(matching)}
---

# {kw.title()} ({task_type.title()})

Auto-generated skill for {len(matching)} observed {task_type} tasks containing "{kw}".

## Purpose
Automates {kw}-related {task_type} workflows.

## Sample Inputs
"""
            for m in matching[:5]:
                content += f"- `{m.get('user_input', '')[:70]}...`\n"
            content += f"\n## Discovered\n- Sessions: {', '.join(set(t.get('session','') for t in matching[:3]))}\n"
            content += f"- First seen: {min(t.get('ts',0) for t in matching) if matching else 0}\n"

            skill_dir = SKILLS_DIR / skill_name
            skill_dir.mkdir(parents=True, exist_ok=True)
            (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")
            existing.add(pattern_key)
            created.append({"name": skill_name, "path": str(skill_dir / "SKILL.md"),
                           "pattern": pattern_key})

    pattern_store["created_skills"] = list(existing)
    pattern_store["last_scan"] = int(time.time())
    save_pattern_store(pattern_store)
    return created


def load_pattern_store():
    if PATTERN_STORE.exists():
        try:
            return json.loads(PATTERN_STORE.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {"created_skills": [], "last_scan": 0}


def save_pattern_store(data):
    PATTERN_STORE.parent.mkdir(parents=True, exist_ok=True)
    PATTERN_STORE.write_text(json.dumps(data, indent=2))


def daemon_loop(interval_s=300, min_occ=2):
    """Background loop: periodically scan and create skills."""
    print(f"[monitor] Starting auto-skill daemon (interval={interval_s}s, min_occ={min_occ})")
    while True:
        try:
            new = analyze_and_create(min_occ, max_new=3)
            if new:
                print(f"[monitor] Created {len(new)} skill(s): {', '.join(n['name'] for n in new)}")
            else:
                print(f"[monitor] No new patterns (checked {ACTIVITY_LOG.exists() and sum(1 for _ in open(ACTIVITY_LOG))} activity entries)")
        except Exception as exc:
            print(f"[monitor] Error: {exc}")
        time.sleep(interval_s)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Auto-Skill Monitor")
    parser.add_argument("--once", action="store_true", help="Single scan, then exit")
    parser.add_argument("--daemon", action="store_true", help="Run as background daemon")
    parser.add_argument("--interval", type=int, default=300, help="Scan interval in seconds")
    parser.add_argument("--min-occ", type=int, default=2, help="Min occurrences to trigger")
    parser.add_argument("--log", type=str, help="Log a specific request")
    parser.add_argument("--input", type=str, help="User input for --log")
    parser.add_argument("--session", type=str, default="cli")
    args = parser.parse_args()

    if args.log and args.input:
        log_request(args.session, args.input)
        print(f"[monitor] Logged request to activity log.")
        return

    if args.daemon:
        def handle_sig(sig, frame):
            print("\n[monitor] Stopping...")
            sys.exit(0)
        signal.signal(signal.SIGINT, handle_sig)
        signal.signal(signal.SIGTERM, handle_sig)
        daemon_loop(args.interval, args.min_occ)
    else:
        new = analyze_and_create(args.min_occ)
        if new:
            print(f"[monitor] Created {len(new)} skill(s):")
            for s in new:
                print(f"  ✓ {s['name']} → {s['path']}")
        else:
            print("[monitor] No new patterns detected.")
        print(f"[monitor] Activity log: {ACTIVITY_LOG.exists() and sum(1 for _ in open(ACTIVITY_LOG))} entries")


if __name__ == "__main__":
    main()
