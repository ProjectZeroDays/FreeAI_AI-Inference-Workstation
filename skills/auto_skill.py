"""AutoSkill — Autonomous skill discovery and creation agent.

Monitors user request patterns, identifies recurring multi-step workflows,
and automatically generates SKILL.md files without prompting the user.

Triggers:
  - Same task pattern observed 2+ times across sessions
  - Multi-step workflow with clear input/output contract
  - User correction indicating a better pattern exists

Usage:
    python skills/auto_skill.py           # start monitoring daemon
    python skills/auto_skill.py --scan    # one-shot analysis of recent activity
    python skills/auto_skill.py --list    # list discovered skill candidates
"""
import json
import os
import re
import threading
import time
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).parent.parent
SKILLS_DIR = ROOT / "skills"
ACTIVITY_LOG = ROOT / "config" / "activity_log.jsonl"
PATTERN_STORE = ROOT / "config" / "skill_patterns.json"


def load_patterns():
    if PATTERN_STORE.exists():
        try:
            return json.loads(PATTERN_STORE.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {"patterns": [], "skills_created": []}


def save_patterns(data):
    PATTERN_STORE.parent.mkdir(parents=True, exist_ok=True)
    PATTERN_STORE.write_text(json.dumps(data, indent=2))


def log_activity(session_id, user_input, assistant_output, task_type=None):
    """Log an activity turn for pattern analysis."""
    entry = {
        "ts": int(time.time()),
        "session": session_id,
        "user_input": user_input[:500],
        "assistant_output": assistant_output[:500],
        "task_type": task_type or classify_task(user_input),
    }
    ACTIVITY_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(ACTIVITY_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def classify_task(text):
    """Classify task type from user input."""
    t = text.lower()
    if any(kw in t for kw in ["write", "create", "build", "implement", "code"]):
        return "coding"
    if any(kw in t for kw in ["debug", "fix", "error", "bug"]):
        return "debugging"
    if any(kw in t for kw in ["explain", "what is", "how does", "understand"]):
        return "learning"
    if any(kw in t for kw in ["review", "analyze", "assess", "evaluate"]):
        return "analysis"
    if any(kw in t for kw in ["test", "run tests", "verify"]):
        return "testing"
    if any(kw in t for kw in ["deploy", "run", "start", "build"]):
        return "deployment"
    if any(kw in t for kw in ["refactor", "clean", "improve", "optimize"]):
        return "refactoring"
    return "general"


def extract_keywords(text, min_len=3):
    """Extract meaningful keywords from text."""
    stop = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been",
        "being", "have", "has", "had", "do", "does", "did", "will",
        "would", "could", "should", "may", "might", "can", "shall",
        "to", "of", "in", "for", "on", "with", "at", "by", "from",
        "as", "into", "through", "during", "before", "after", "above",
        "below", "between", "out", "off", "over", "under", "again",
        "further", "then", "once", "here", "there", "when", "where",
        "why", "how", "all", "each", "every", "both", "few", "more",
        "most", "other", "some", "such", "no", "nor", "not", "only",
        "own", "same", "so", "than", "too", "very", "s", "t", "just",
        "don", "now", "i", "me", "my", "we", "our", "you", "your",
        "he", "she", "it", "they", "them", "his", "her", "its", "their",
    }
    words = re.findall(r'\b\w{'+ str(min_len) + r',}\b', text.lower())
    return [w for w in words if w not in stop]


def detect_patterns(min_occurrences=2):
    """Scan activity log for recurring patterns."""
    if not ACTIVITY_LOG.exists():
        return []

    entries = []
    for line in open(ACTIVITY_LOG, encoding="utf-8"):
        try:
            entries.append(json.loads(line.strip()))
        except (json.JSONDecodeError, OSError):
            continue

    # Group by task type
    by_type = defaultdict(list)
    for e in entries:
        by_type[e.get("task_type", "general")].append(e)

    patterns = []
    for task_type, tasks in by_type.items():
        if len(tasks) < min_occurrences:
            continue

        # Extract common keywords
        all_kw = []
        for t in tasks:
            all_kw.extend(extract_keywords(t.get("user_input", "")))
        kw_counts = Counter(all_kw)

        # Find high-frequency keyword combinations
        for kw, count in kw_counts.most_common(20):
            if count >= min_occurrences:
                matching = [t for t in tasks if kw in t.get("user_input", "").lower()]
                patterns.append({
                    "keyword": kw,
                    "task_type": task_type,
                    "occurrences": len(matching),
                    "sample_inputs": [t["user_input"][:100] for t in matching[:3]],
                    "sessions": list(set(t.get("session", "") for t in matching)),
                })

    return sorted(patterns, key=lambda x: -x["occurrences"])


def generate_skill_from_pattern(pattern):
    """Generate a SKILL.md from a detected pattern."""
    name = f"{pattern['task_type']}-{pattern['keyword']}"
    name = re.sub(r'\s+', '-', name).lower()

    sample = pattern.get("sample_inputs", [""])[0]
    trigger_keywords = [pattern["keyword"]]
    for t in pattern.get("sample_inputs", []):
        trigger_keywords.extend(extract_keywords(t))
    trigger_keywords = list(set(trigger_keywords[:8]))

    skill_content = f"""---
name: {name}
description: >
  Automated skill for {pattern['task_type']} tasks involving {pattern['keyword']}.
  Discovered from {pattern['occurrences']} recurring requests.
triggers:
  - {pattern['keyword']}
  - {pattern['task_type']}
metadata:
  auto_generated: true
  source: activity_pattern
  created_at: "{time.strftime('%Y-%m-%d %H:%M:%S')}"
  occurrences: {pattern['occurrences']}
---

# {pattern['keyword'].title()} ({pattern['task_type'].title()})

Auto-generated skill from {pattern['occurrences']} recurring {pattern['task_type']} requests.

## Purpose
Handles {pattern['keyword']} tasks of type {pattern['task_type']}.

## Usage
"""
    for sample in pattern.get("sample_inputs", [])[:5]:
        skill_content += f"\n- `{sample[:80]}...`\n"

    skill_content += f"""
## Pattern Notes
- Task type: {pattern['task_type']}
- Discovered from sessions: {', '.join(pattern.get('sessions', [])[:3])}
- Trigger keywords: {', '.join(trigger_keywords[:5])}

## Generated
{time.strftime('%Y-%m-%d %H:%M:%S')}
"""
    return name, skill_content


def create_skill_from_pattern(pattern):
    """Write a SKILL.md file from a detected pattern."""
    name, content = generate_skill_from_pattern(pattern)
    skill_dir = SKILLS_DIR / name
    base_dir = SKILLS_DIR.resolve()
    skill_dir_resolved = skill_dir.resolve()
    try:
        skill_dir_resolved.relative_to(base_dir)
    except ValueError:
        raise Exception("Invalid file path")
    skill_dir_resolved.mkdir(parents=True, exist_ok=True)
    skill_file = skill_dir_resolved / "SKILL.md"
    skill_file.write_text(content, encoding="utf-8")
    return str(skill_file)


def scan_and_create(min_occurrences=2, max_skills=10):
    """Scan activity, detect patterns, create skills."""
    data = load_patterns()
    existing = set(data.get("skills_created", []))

    patterns = detect_patterns(min_occurrences)
    new_skills = []
    for p in patterns:
        if len(new_skills) >= max_skills:
            break
        pattern_key = f"{p['task_type']}:{p['keyword']}"
        if pattern_key in existing:
            continue
        path = create_skill_from_pattern(p)
        new_skills.append({"pattern": pattern_key, "skill_path": path})
        existing.add(pattern_key)

    data["skills_created"] = list(existing)
    data["last_scan"] = int(time.time())
    save_patterns(data)

    return new_skills


class AutoSkillAgent:
    """Continuous monitoring agent for auto skill creation."""

    def __init__(self, interval_s=300, min_occurrences=2):
        self.interval_s = interval_s
        self.min_occurrences = min_occurrences
        self._running = False
        self._thread = None

    def start(self):
        """Start background monitoring."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def _loop(self):
        while self._running:
            try:
                new = scan_and_create(self.min_occurrences, max_skills=5)
                if new:
                    print(f"[autoskill] Created {len(new)} new skill(s):"
                          f" {', '.join(n['pattern'] for n in new)}")
            except Exception as exc:
                print(f"[autoskill] Error: {exc}")
            time.sleep(self.interval_s)


_agent = None


def get_agent():
    global _agent
    if _agent is None:
        _agent = AutoSkillAgent()
    return _agent


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--scan", action="store_true", help="One-shot scan")
    parser.add_argument("--list", action="store_true", help="List candidates")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    parser.add_argument("--interval", type=int, default=300)
    args = parser.parse_args()

    if args.scan or args.list:
        patterns = detect_patterns()
        if args.list:
            for p in patterns[:10]:
                print(f"  [{p['occurrences']}x] {p['task_type']}: {p['keyword']}")
                for s in p.get("sample_inputs", [])[:2]:
                    print(f"    → {s[:70]}")
        if args.scan:
            new = scan_and_create()
            for n in new:
                print(f"  Created: {n['skill_path']}")
            if not new:
                print("  No new patterns to create.")
    elif args.daemon:
        agent = AutoSkillAgent(interval_s=args.interval)
        agent.start()
        print(f"[autoskill] Daemon running (interval={args.interval}s)")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            agent.stop()
            print("[autoskill] Stopped.")
    else:
        # Default: scan once
        new = scan_and_create()
        print(f"[autoskill] Scan complete. Created {len(new)} skill(s).")
