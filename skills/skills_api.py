"""Skills API — REST endpoints for the Skills Manager dashboard.

Endpoints:
  GET  /api/skills          - List all skills
  GET  /api/skills/files    - List skills from filesystem
  POST /api/skills/save     - Create or update a skill
  DELETE /api/skills/delete/<name> - Delete a skill
  POST /api/skills/scan     - Scan for auto-generated skill opportunities
  GET  /api/skills/activity - Recent activity log for pattern analysis
"""
import json
import os
import re
import threading
import time
from pathlib import Path

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

ROOT = Path(__file__).parent.parent
SKILLS_DIR = ROOT / "skills"
ACTIVITY_LOG = ROOT / "config" / "activity_log.jsonl"
PATTERN_STORE = ROOT / "config" / "skill_patterns.json"


def _ensure_dirs():
    SKILLS_DIR.mkdir(parents=True, exist_ok=True)
    (ROOT / "config").mkdir(parents=True, exist_ok=True)


_ensure_dirs()


def _load_skill_files():
    """Scan skills directory for SKILL.md files."""
    skills = []
    if not SKILLS_DIR.exists():
        return skills
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        content = skill_md.read_text(encoding="utf-8", errors="ignore")
        name = skill_dir.name
        desc = ""
        triggers = []
        category = "general"
        auto_generated = False
        enabled = True

        # Parse frontmatter
        fm_match = re.match(r"^---\n([\s\S]*?)\n---", content)
        if fm_match:
            fm = fm_match.group(1)
            for line in fm.split("\n"):
                if line.startswith("name:"):
                    name = line.split(":", 1)[1].strip().strip('"').strip("'")
                elif line.startswith("description:"):
                    desc = line.split(":", 1)[1].strip().strip('"')
                elif line.startswith("triggers:"):
                    pass  # next lines are list items
                elif line.strip().startswith("- ") and "triggers" in fm[:fm.find(line) if line in fm else 0]:
                    triggers.append(line[2:].strip())
                elif line.startswith("category:"):
                    category = line.split(":", 1)[1].strip()
                elif line.startswith("auto_generated:"):
                    auto_generated = line.split(":", 1)[1].strip().lower() == "true"
                elif line.startswith("enabled:"):
                    enabled = line.split(":", 1)[1].strip().lower() == "true"

        # Fallback: extract triggers from content if not in frontmatter
        if not triggers:
            trigger_matches = re.findall(r"^\s*-\s+(\S.+)$", content, re.MULTILINE)
            triggers = [t.strip().strip('"').strip("'") for t in trigger_matches[:5]]

        skills.append({
            "name": name,
            "path": str(skill_md),
            "description": desc,
            "triggers": triggers,
            "category": category,
            "auto_generated": auto_generated,
            "enabled": enabled,
            "content": content,
        })
    return skills


def _log_activity(session_id, user_input, assistant_output, task_type=None):
    entry = {
        "ts": int(time.time()),
        "session": session_id or "unknown",
        "user_input": user_input[:500],
        "assistant_output": assistant_output[:500],
        "task_type": task_type or "general",
    }
    with open(ACTIVITY_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _detect_patterns(min_occ=2):
    if not ACTIVITY_LOG.exists():
        return []
    entries = []
    for line in open(ACTIVITY_LOG, encoding="utf-8"):
        try:
            entries.append(json.loads(line.strip()))
        except (json.JSONDecodeError, OSError):
            continue
    from collections import Counter, defaultdict
    by_type = defaultdict(list)
    for e in entries:
        by_type[e.get("task_type", "general")].append(e)
    patterns = []
    for task_type, tasks in by_type.items():
        if len(tasks) < min_occ:
            continue
        kw_counts = Counter()
        for t in tasks:
            for w in re.findall(r'\b\w{3,}\b', t.get("user_input", "").lower()):
                if w not in {"there", "their", "through", "another", "where"}:
                    kw_counts[w] += 1
        for kw, count in kw_counts.most_common(10):
            if count >= min_occ:
                matching = [t for t in tasks if kw in t.get("user_input", "").lower()]
                patterns.append({
                    "keyword": kw,
                    "task_type": task_type,
                    "occurrences": len(matching),
                    "sample_inputs": [t["user_input"][:80] for t in matching[:3]],
                    "sessions": list(set(t.get("session", "") for t in matching)),
                })
    return sorted(patterns, key=lambda x: -x["occurrences"])


def _generate_skill_from_pattern(pattern):
    name = f"{pattern['task_type']}-{pattern['keyword']}"
    name = re.sub(r'\s+', '-', name).lower()
    sample = pattern.get("sample_inputs", [""])[0]
    content = f"""---
name: {name}
description: >
  Auto-generated skill for {pattern['task_type']} tasks involving {pattern['keyword']}.
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
    for s in pattern.get("sample_inputs", [])[:5]:
        content += f"- `{s[:70]}...`\n"
    content += f"\n## Pattern Notes\n- Task type: {pattern['task_type']}\n"
    content += f"- Discovered: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
    return name, content


# ── In-memory store (supplements filesystem) ─────────────────────
_skills = None
_lock = threading.Lock()


def get_skills():
    global _skills
    if _skills is None:
        _skills = _load_skill_files()
    return _skills


def save_skill_data(data):
    """Save a skill to the filesystem."""
    name = data.get("name", "").strip()
    if not name:
        raise ValueError("Skill name is required")
    # Sanitize name for directory
    safe_name = re.sub(r'[^\w\-]', '-', name).lower()
    skill_dir = SKILLS_DIR / safe_name
    skill_dir.mkdir(parents=True, exist_ok=True)

    # Build frontmatter
    fm = f"""---
name: {name}
description: >
  {data.get('description', '')}
triggers:
{chr(10).join('  - ' + t for t in data.get('triggers', []))}
category: {data.get('category', 'general')}
auto_generated: {str(data.get('auto_generated', False)).lower()}
enabled: {str(data.get('enabled', True)).lower()}
metadata:
  updated_at: "{time.strftime('%Y-%m-%d %H:%M:%S')}"
---

"""
    content = fm + (data.get("content", "") or "")
    (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")

    # Update in-memory
    global _skills
    _skills = _load_skill_files()
    return True


def delete_skill(name):
    safe_name = re.sub(r'[^\w\-]', '-', name).lower()
    skill_dir = SKILLS_DIR / safe_name
    if skill_dir.exists():
        import shutil
        shutil.rmtree(skill_dir)
    global _skills
    _skills = _load_skill_files()
    return True


# ── FastAPI app ────────────────────────────────────────────────────
if HAS_FASTAPI:
    app = FastAPI(title="Skills API", version="1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    class SaveSkillRequest(BaseModel):
        name: str
        description: str = ""
        triggers: list[str] = []
        tags: list[str] = []
        category: str = "general"
        content: str = ""
        enabled: bool = True
        auto_generated: bool = False

    @app.get("/api/skills")
    def list_skills():
        return get_skills()

    @app.get("/api/skills/files")
    def list_skills_files():
        return _load_skill_files()

    @app.post("/api/skills/save")
    def save_skill(req: SaveSkillRequest):
        try:
            save_skill_data(req.model_dump())
            return {"ok": True, "name": req.name}
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    @app.delete("/api/skills/delete/{name}")
    def delete_skill_endpoint(name: str):
        try:
            delete_skill(name)
            return {"ok": True}
        except Exception as exc:
            raise HTTPException(status_code=404, detail=str(exc))

    @app.post("/api/skills/scan")
    def scan_for_skills():
        patterns = _detect_patterns(min_occ=2)
        created = []
        for p in patterns[:5]:
            sname, content = _generate_skill_from_pattern(p)
            try:
                existing = [s for s in get_skills() if s["name"] == sname]
                if existing:
                    continue
                save_skill_data({
                    "name": sname,
                    "description": f"Auto-generated for {p['task_type']}: {p['keyword']}",
                    "triggers": [p["keyword"], p["task_type"]],
                    "category": p["task_type"],
                    "content": content,
                    "auto_generated": True,
                })
                created.append(sname)
            except Exception:
                pass
        return {"created": created, "patterns_found": len(patterns)}

    @app.get("/health")
    def health():
        return {"status": "ok", "skills_count": len(get_skills())}

    @app.get("/api/skills/activity")
    def get_activity(limit=50):
        if not ACTIVITY_LOG.exists():
            return {"entries": [], "total": 0}
        entries = []
        for line in open(ACTIVITY_LOG, encoding="utf-8"):
            try:
                entries.append(json.loads(line.strip()))
            except (json.JSONDecodeError, OSError):
                continue
        return {"entries": entries[-limit:], "total": len(entries)}

    @app.post("/api/skills/log-activity")
    def log_activity_endpoint(req: dict):
        _log_activity(
            req.get("session_id", "unknown"),
            req.get("user_input", ""),
            req.get("assistant_output", ""),
            req.get("task_type"),
        )
        return {"ok": True}

    @app.get("/api/skills/stats")
    def stats():
        skills = get_skills()
        cats = {}
        auto_count = 0
        enabled_count = 0
        for s in skills:
            c = s.get("category", "general")
            cats[c] = cats.get(c, 0) + 1
            if s.get("auto_generated"):
                auto_count += 1
            if s.get("enabled", True):
                enabled_count += 1
        return {
            "total": len(skills),
            "categories": cats,
            "auto_generated": auto_count,
            "enabled": enabled_count,
        }


if __name__ == "__main__":
    if HAS_FASTAPI:
        import uvicorn
        port = int(os.environ.get("SKILLS_PORT", "8160"))
        print(f"[skills] Starting skills API on :{port}")
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        print("[skills] FastAPI not available. Use the dashboard API endpoint.")
