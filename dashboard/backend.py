"""Dashboard backend — serves the unified FreeAI dashboard and skills manager.

Provides REST API endpoints and serves static HTML pages.
"""
import json
import os
import random
import threading
import time
import uuid
from pathlib import Path

try:
    from flask import Flask, render_template, request, jsonify, send_from_directory
except ImportError:
    Flask = None

ROOT = Path(__file__).parent
DASHBOARD_DIR = ROOT
STATIC_DIR = DASHBOARD_DIR / "static"
TEMPLATES_DIR = DASHBOARD_DIR / "templates"
CONFIG_DIR = ROOT.parent / "config"
SKILLS_DIR = ROOT.parent / "skills"
ACTIVITY_LOG = CONFIG_DIR / "activity_log.jsonl"

app = Flask(__name__,
            static_folder=str(STATIC_DIR),
            template_folder=str(TEMPLATES_DIR))

# ── In-memory state ──────────────────────────────────────────────
_services = {}
_requests_log = []
_LOCK = threading.Lock()


def _load_json(path, default=None):
    if path.exists():
        try:
            return json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return default or {}


def _save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


# ── Pages ────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("index.html")


@app.route("/skills")
def skills_page():
    return render_template("skills.html")


@app.route("/sdlc")
def sdlc_page():
    return render_template("sdlc.html")


@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(str(STATIC_DIR), filename)


# ── API: Services health ─────────────────────────────────────────
@app.route("/api/services")
def api_services():
    services = {}
    ports = {
        "proxy": 8100, "memory": 8110, "agents": 8120,
        "registry": 8130, "rag": 8140, "brain": 8150, "skills": 8160,
    }
    import urllib.request
    for name, port in ports.items():
        try:
            r = urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=2)
            services[name] = {"status": "running", "port": port, "health": r.status == 200}
        except Exception:
            services[name] = {"status": "stopped", "port": port, "health": False}
    return jsonify(services)


# ── API: Skills ──────────────────────────────────────────────────
@app.route("/api/skills")
def api_skills():
    skills = []
    if SKILLS_DIR.exists():
        for d in sorted(SKILLS_DIR.iterdir()):
            if not d.is_dir():
                continue
            skill_md = d / "SKILL.md"
            if not skill_md.exists():
                continue
            content = skill_md.read_text(encoding="utf-8", errors="ignore")
            name = d.name
            desc = ""
            triggers = []
            category = "general"
            auto = False
            enabled = True
            import re
            fm = re.match(r"^---\n([\s\S]*?)\n---", content)
            if fm:
                fm_text = fm.group(1)
                for line in fm_text.split("\n"):
                    if line.startswith("name:"):
                        name = line.split(":", 1)[1].strip().strip('"').strip("'")
                    elif line.startswith("description:"):
                        desc = line.split(":", 1)[1].strip().strip('"')
                    elif line.startswith("category:"):
                        category = line.split(":", 1)[1].strip()
                    elif line.startswith("auto_generated:"):
                        auto = line.split(":", 1)[1].strip().lower() == "true"
                    elif line.startswith("enabled:"):
                        enabled = line.split(":", 1)[1].strip().lower() == "true"
                # Extract triggers from frontmatter
                trig_section = False
                for line in fm_text.split("\n"):
                    if line.strip() == "triggers:":
                        trig_section = True
                        continue
                    if trig_section:
                        if line.strip().startswith("- "):
                            triggers.append(line[2:].strip().strip('"'))
                        else:
                            trig_section = False
            skills.append({
                "name": name,
                "path": str(skill_md),
                "description": desc,
                "triggers": triggers,
                "category": category,
                "auto_generated": auto,
                "enabled": enabled,
                "content": content,
            })
    return jsonify(skills)


@app.route("/api/skills/save", methods=["POST"])
def api_save_skill():
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"ok": False, "error": "Name required"}), 400
    safe_name = re.sub(r'[^\w\-]', '-', name).lower()
    skill_dir = SKILLS_DIR / safe_name
    skill_dir.mkdir(parents=True, exist_ok=True)
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
    return jsonify({"ok": True, "name": name})


@app.route("/api/skills/delete/<name>", methods=["DELETE"])
def api_delete_skill(name):
    import shutil
    safe_name = re.sub(r'[^\w\-]', '-', name).lower()
    skill_dir = SKILLS_DIR / safe_name
    if skill_dir.exists():
        shutil.rmtree(skill_dir)
    return jsonify({"ok": True})


@app.route("/api/skills/scan", methods=["POST"])
def api_scan_skills():
    """Scan activity log and auto-create skills."""
    if not ACTIVITY_LOG.exists():
        return jsonify({"created": [], "message": "No activity log found"})
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
    created = []
    pattern_store = _load_json(CONFIG_DIR / "skill_patterns.json", {})
    existing = set(pattern_store.get("created_skills", []))
    import re as _re
    for task_type, tasks in by_type.items():
        if len(tasks) < 2:
            continue
        kw_counts = Counter()
        for t in tasks:
            for w in _re.findall(r'\b\w{3,}\b', t.get("user_input", "").lower()):
                if w not in {"there", "their", "through", "another", "where", "about"}:
                    kw_counts[w] += 1
        for kw, count in kw_counts.most_common(10):
            if count < 2:
                continue
            pattern_key = f"{task_type}:{kw}"
            if pattern_key in existing:
                continue
            matching = [t for t in tasks if kw in t.get("user_input", "").lower()]
            skill_name = f"{task_type}-{kw}"
            skill_name = _re.sub(r'\s+', '-', skill_name).lower()
            sample = matching[0].get("user_input", "")[:100] if matching else ""
            content = f"""---
name: {skill_name}
description: >
  Auto-generated for {task_type} with keyword {kw}.
  Discovered from {len(matching)} recurring requests.
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

Auto-generated skill from {len(matching)} observed {task_type} tasks.

## Purpose
Handles {kw}-related {task_type} workflows automatically.

## Sample Inputs
"""
            for m in matching[:5]:
                content += f"- `{m.get('user_input', '')[:70]}...`\n"
            content += f"\n## Discovered\n- Sessions: {', '.join(set(t.get('session','') for t in matching[:3]))}\n"
            skill_dir = SKILLS_DIR / skill_name
            skill_dir.mkdir(parents=True, exist_ok=True)
            (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")
            existing.add(pattern_key)
            created.append(skill_name)
    pattern_store["created_skills"] = list(existing)
    pattern_store["last_scan"] = int(time.time())
    _save_json(CONFIG_DIR / "skill_patterns.json", pattern_store)
    return jsonify({"created": created, "count": len(created)})


@app.route("/api/skills/activity")
def api_activity():
    if not ACTIVITY_LOG.exists():
        return jsonify({"entries": [], "total": 0})
    entries = []
    for line in open(ACTIVITY_LOG, encoding="utf-8"):
        try:
            entries.append(json.loads(line.strip()))
        except (json.JSONDecodeError, OSError):
            continue
    return jsonify({"entries": entries[-100:], "total": len(entries)})


@app.route("/api/skills/log", methods=["POST"])
def api_log_activity():
    data = request.get_json(silent=True) or {}
    entry = {
        "ts": int(time.time()),
        "session": data.get("session_id", "unknown"),
        "user_input": data.get("user_input", "")[:500],
        "assistant_output": data.get("assistant_output", "")[:500],
        "task_type": data.get("task_type", "general"),
    }
    ACTIVITY_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(ACTIVITY_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return jsonify({"ok": True})


# ── API: General ─────────────────────────────────────────────────
@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "service": "dashboard"})


@app.route("/api/config")
def get_config():
    config = _load_json(CONFIG_DIR / "services.json", {})
    return jsonify(config)


@app.route("/api/stats")
def stats():
    skills_count = len(list(SKILLS_DIR.iterdir())) if SKILLS_DIR.exists() else 0
    activity_count = 0
    if ACTIVITY_LOG.exists():
        activity_count = sum(1 for _ in open(ACTIVITY_LOG))
    return jsonify({
        "skills_total": skills_count,
        "activity_entries": activity_count,
        "uptime": int(time.time()),
    })


# ── API: Browser Settings ────────────────────────────────────────
BROWSER_CONFIG_PATH = CONFIG_DIR / "browser.json"

BROWSER_DEFAULTS = {
    "stealth": {
        "enable": True,
        "randomize_fingerprint": True,
        "mask_webdriver": True,
        "fake_headers": True,
        "override_navigator": True,
        "canvas_noise": True,
        "webgl_noise": True,
        "audio_noise": True,
    },
    "anonymity": {"mode": "none", "tor_socks_port": 9150},
    "healing": {
        "max_retries": 5,
        "retry_backoff": 1.5,
        "adaptive_selectors": True,
        "screenshot_on_fail": True,
        "scroll_into_view": True,
    },
    "manifestx": {"enabled": True, "god_mode": True},
    "cdp": {"enabled": True},
    "observability": {"dom_mirror": False},
    "viewport": {"width": 1920, "height": 1080},
    "headless": True,
    "api_port": 8180,
}


def _load_browser_config():
    if BROWSER_CONFIG_PATH.exists():
        try:
            with open(BROWSER_CONFIG_PATH, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return dict(BROWSER_DEFAULTS)


def _save_browser_config(cfg):
    BROWSER_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(BROWSER_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)


@app.route("/api/browser/settings", methods=["GET"])
def get_browser_settings():
    cfg = _load_browser_config()
    return jsonify(cfg)


@app.route("/api/browser/settings", methods=["POST"])
def save_browser_settings():
    data = request.get_json(silent=True) or {}
    cfg = _load_browser_config()
    # Merge incoming settings
    for section in ("stealth", "anonymity", "healing", "manifestx",
                    "cdp", "observability", "viewport"):
        if section in data:
            if section in cfg and isinstance(cfg[section], dict):
                cfg[section].update(data[section])
            else:
                cfg[section] = data[section]
    for key in ("headless", "api_port"):
        if key in data:
            cfg[key] = data[key]
    _save_browser_config(cfg)
    return jsonify({"ok": True, "settings": cfg})


@app.route("/api/browser/reset")
def reset_browser_settings():
    _save_browser_config(dict(BROWSER_DEFAULTS))
    return jsonify({"ok": True, "settings": BROWSER_DEFAULTS})


# ── Page Routes ──────────────────────────────────────────────────
@app.route("/subagents")
def subagents_page():
    return render_template("subagents.html")


@app.route("/training")
def training_page():
    return render_template("training.html")


@app.route("/memory")
def memory_page():
    return render_template("memory.html")


@app.route("/gateway")
def gateway_page():
    return render_template("gateway.html")


@app.route("/automations")
def automations_page():
    return render_template("automations.html")


@app.route("/wiki-dashboard")
def wiki_dashboard_page():
    return render_template("wiki-dashboard.html")


@app.route("/blog")
def blog_page():
    return render_template("blog.html")


@app.route("/forum")
def forum_page():
    return render_template("forum.html")


@app.route("/logs")
def logs_page():
    return render_template("logs.html")


# ── API: Subagents ────────────────────────────────────────────────
_SUBAGENTS = []
_SUBAGENT_LOCK = threading.Lock()
_TRAINING_DATA = {
    "datasets": [],
    "jobs": {"sft": [], "dpo": [], "abr": []},
    "models": [],
}
_TRAINING_LOCK = threading.Lock()


@app.route("/api/subagents", methods=["GET"])
def api_subagents():
    with _SUBAGENT_LOCK:
        return jsonify(_SUBAGENTS)


@app.route("/api/subagents", methods=["POST"])
def api_create_subagent():
    data = request.get_json(silent=True) or {}
    desc = data.get("description", "untitled task")
    roles = data.get("roles", "all")
    parallel = min(int(data.get("parallel", 3)), 8)
    model = data.get("model", "auto")
    pipeline = data.get("pipeline", "scaffold")
    timeout = int(data.get("timeout", 30))
    steps = data.get("steps", [])

    role_map = {
        "all": ["explorer", "coder", "reviewer", "researcher", "architect"],
        "coder": ["coder"],
        "explorer": ["explorer"],
        "researcher": ["researcher"],
        "reviewer": ["reviewer"],
        "architect": ["architect"],
    }
    selected_roles = role_map.get(roles, ["explorer", "coder"])
    count = min(parallel, len(selected_roles))
    task_id = str(uuid.uuid4())[:8]
    spawned = []

    for i in range(count):
        sa_id = f"{task_id}-{i:02d}"
        role = selected_roles[i % len(selected_roles)]
        sa = {
            "id": sa_id,
            "task_id": task_id,
            "name": f"{role.capitalize()} #{i+1}",
            "role": role,
            "pipeline": pipeline,
            "model": model,
            "status": "running",
            "progress": 0,
            "created_at": time.time(),
            "description": desc[:80],
        }
        spawned.append(sa)

    with _SUBAGENT_LOCK:
        _SUBAGENTS.extend(spawned)

    def _simulate(sa):
        for p in range(0, 101, random.randint(5, 15)):
            time.sleep(random.uniform(0.5, 2))
            with _SUBAGENT_LOCK:
                for s in _SUBAGENTS:
                    if s["id"] == sa["id"]:
                        s["progress"] = min(p, 100)
                        if p >= 100:
                            s["status"] = random.choice(["done", "done", "done", "failed"])
                        break

    threading.Thread(target=_simulate, args=(spawned[0],), daemon=True).start()
    if len(spawned) > 1:
        threading.Thread(target=_simulate, args=(spawned[1],), daemon=True).start()

    return jsonify({"task_id": task_id, "subagents_launched": len(spawned), "subagents": spawned})


@app.route("/api/subagents/<sa_id>", methods=["DELETE"])
def api_delete_subagent(sa_id):
    with _SUBAGENT_LOCK:
        before = len(_SUBAGENTS)
        _SUBAGENTS[:] = [s for s in _SUBAGENTS if s["id"] != sa_id]
    return jsonify({"removed": before - len(_SUBAGENTS)})


@app.route("/api/subagents/<sa_id>/pause", methods=["POST"])
def api_pause_subagent(sa_id):
    with _SUBAGENT_LOCK:
        for s in _SUBAGENTS:
            if s["id"] == sa_id:
                s["status"] = "paused"
                return jsonify({"ok": True})
    return jsonify({"error": "not found"}), 404


@app.route("/api/subagents/<sa_id>/resume", methods=["POST"])
def api_resume_subagent(sa_id):
    with _SUBAGENT_LOCK:
        for s in _SUBAGENTS:
            if s["id"] == sa_id:
                s["status"] = "running"
                return jsonify({"ok": True})
    return jsonify({"error": "not found"}), 404


@app.route("/api/subagents/<sa_id>/log")
def api_subagent_log(sa_id):
    return jsonify({
        "id": sa_id,
        "logs": [
            {"time": "14:32:01", "level": "info", "msg": "Subagent initialized"},
            {"time": "14:32:02", "level": "info", "msg": "Loading context from persistent memory"},
            {"time": "14:32:03", "level": "ok", "msg": "Context loaded: 3 memories recalled"},
            {"time": "14:32:05", "level": "info", "msg": "Starting task execution"},
        ]
    })


# ── API: Training ─────────────────────────────────────────────────
@app.route("/api/training", methods=["GET"])
def api_training_status():
    with _TRAINING_LOCK:
        return jsonify(_TRAINING_DATA)


@app.route("/api/training/datasets", methods=["GET"])
def api_datasets():
    with _TRAINING_LOCK:
        return jsonify(_TRAINING_DATA["datasets"])


@app.route("/api/training/datasets", methods=["POST"])
def api_upload_dataset():
    name = request.form.get("name", "untitled")
    fmt = request.form.get("format", "jsonl")
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    ds_id = str(uuid.uuid4())[:8]
    with _TRAINING_LOCK:
        _TRAINING_DATA["datasets"].append({
            "id": ds_id,
            "name": name,
            "format": fmt,
            "samples": random.randint(100, 10000),
            "created_at": time.time(),
        })
    return jsonify({"id": ds_id, "name": name, "format": fmt, "samples": 1234})


@app.route("/api/training/datasets/<ds_id>", methods=["DELETE"])
def api_delete_dataset(ds_id):
    with _TRAINING_LOCK:
        _TRAINING_DATA["datasets"] = [d for d in _TRAINING_DATA["datasets"] if d["id"] != ds_id]
    return jsonify({"deleted": True})


@app.route("/api/training/jobs", methods=["POST"])
def api_create_job():
    data = request.get_json(silent=True) or {}
    jtype = data.get("type", "sft")
    job_id = str(uuid.uuid4())[:8]
    job = {
        "id": job_id,
        "type": jtype,
        "model": data.get("base_model", "unknown"),
        "dataset": data.get("dataset_id", ""),
        "name": data.get("name", jtype + "-" + job_id),
        "status": "queued",
        "progress": 0,
        "created_at": time.time(),
    }
    with _TRAINING_LOCK:
        _TRAINING_DATA["jobs"][jtype].append(job)

    def _run():
        for p in range(0, 101, random.randint(3, 10)):
            time.sleep(random.uniform(0.3, 1.5))
            with _TRAINING_LOCK:
                job["progress"] = min(p, 100)
                if p >= 100:
                    job["status"] = random.choice(["done", "failed"])
                    if job["status"] == "done" and jtype == "sft":
                        _TRAINING_DATA["models"].append({
                            "id": str(uuid.uuid4())[:8],
                            "name": job["name"],
                            "base_model": job["model"],
                            "method": "sft",
                            "samples": 1234,
                            "created_at": time.time(),
                        })

    threading.Thread(target=_run, daemon=True).start()
    return jsonify({"job_id": job_id, "status": "queued"})


@app.route("/api/training/abliterate", methods=["POST"])
def api_abliterate():
    data = request.get_json(silent=True) or {}
    job_id = str(uuid.uuid4())[:8]
    job = {
        "id": job_id,
        "model": data.get("model", "unknown"),
        "strategy": data.get("strategy", "boundary_inversion"),
        "status": "running",
        "progress": 0,
        "created_at": time.time(),
    }
    with _TRAINING_LOCK:
        _TRAINING_DATA["jobs"]["abr"].append(job)

    def _run():
        for p in range(0, 101, random.randint(5, 15)):
            time.sleep(random.uniform(0.3, 1))
            with _TRAINING_LOCK:
                job["progress"] = min(p, 100)
                if p >= 100:
                    job["status"] = "done"

    threading.Thread(target=_run, daemon=True).start()
    return jsonify({"job_id": job_id, "status": "running"})


@app.route("/api/training/models", methods=["GET"])
def api_models():
    with _TRAINING_LOCK:
        return jsonify(_TRAINING_DATA["models"])


@app.route("/api/training/models/<mid>", methods=["DELETE"])
def api_delete_model(mid):
    with _TRAINING_LOCK:
        _TRAINING_DATA["models"] = [m for m in _TRAINING_DATA["models"] if m["id"] != mid]
    return jsonify({"deleted": True})


@app.route("/api/training/models/<mid>/deploy", methods=["POST"])
def api_deploy_model(mid):
    with _TRAINING_LOCK:
        for m in _TRAINING_DATA["models"]:
            if m["id"] == mid:
                return jsonify({"ok": True, "endpoint": "http://localhost:9001/v1/completions", "model": m["name"]})
    return jsonify({"error": "not found"}), 404


if __name__ == "__main__":
    port = int(os.environ.get("DASHBOARD_PORT", "8080"))
    print(f"[dashboard] Serving on :{port}")
    app.run(host="0.0.0.0", port=port, threaded=True)
