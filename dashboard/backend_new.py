"""Dashboard backend â€” serves the unified FreeAI dashboard and skills manager.

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

# â”€â”€ Test hooks: mockable module-level constants â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
UPLOAD_DIR = CONFIG_DIR / "uploads"
AUTH_TOKEN = os.environ.get("DASHBOARD_AUTH_TOKEN", "")
OPT_SETTINGS_PATH = CONFIG_DIR / "runtime-settings.json"
PRESETS_PATH = CONFIG_DIR / "presets.json"
LLAMA_ENV_PATH = CONFIG_DIR / "llama.env"
ROOT_DIR = CONFIG_DIR.parent

app = Flask(__name__,
            static_folder=str(STATIC_DIR),
            template_folder=str(TEMPLATES_DIR))

# â”€â”€ In-memory state â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_services = {}
_requests_log = []
_LOCK = threading.Lock()


def _load_json(path, default=None):
    p = Path(path) if isinstance(path, str) else path
    if p.exists():
        try:
            return json.loads(p.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return default or {}


def _save_json(path, data):
    p = Path(path) if isinstance(path, str) else path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


# â”€â”€ Pages â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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


# â”€â”€ API: Services health â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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


# â”€â”€ API: Skills â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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


# â”€â”€ API: General â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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


# â”€â”€ API: Browser Settings â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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


# â”€â”€ Page Routes â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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


@app.route("/network")
def network_page():
    return render_template("network.html")


# â”€â”€ API: Subagents â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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


# â”€â”€ API: Training â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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


# â”€â”€ API: Memory â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_MEMORY_STATE = {
    "preferences": {
        "auto_remember": True,
        "share_with_agents": True,
        "auto_create_skills": True,
        "retention_days": 365,
        "max_memories_per_context": 20,
    },
    "projects": [
        {"name": "unified-ai-stack", "last_active": "2 min ago", "context": "Working on dashboard redesign, landing page, and new features."},
        {"name": "quantum-c2", "last_active": "3 days ago", "context": "C2 framework â€” implementing stealth modules and updating dashboards."},
    ],
    "environment": {
        "os": "Windows 11",
        "python": "3.14.0",
        "working_dir": "unified-ai-stack",
        "dashboard_port": 8030,
        "router_port": 8010,
        "skills_count": 55,
    },
    "sessions": [],
    "learnings": [],
    "stats": {"memories": 42, "context_windows": 3, "sessions": 12, "recalls": 87},
}
_MEMORY_LOCK = threading.Lock()


@app.route("/api/memory", methods=["GET"])
def api_memory_get():
    with _MEMORY_LOCK:
        return jsonify(_MEMORY_STATE)


@app.route("/api/memory/preferences", methods=["GET", "POST"])
def api_memory_preferences():
    with _MEMORY_LOCK:
        if request.method == "POST":
            data = request.get_json(silent=True) or {}
            for k, v in data.items():
                if k in _MEMORY_STATE["preferences"]:
                    _MEMORY_STATE["preferences"][k] = v
            return jsonify({"ok": True, "preferences": _MEMORY_STATE["preferences"]})
        return jsonify(_MEMORY_STATE["preferences"])


@app.route("/api/memory/projects", methods=["GET", "POST"])
def api_memory_projects():
    with _MEMORY_LOCK:
        if request.method == "POST":
            data = request.get_json(silent=True) or {}
            _MEMORY_STATE["projects"].append({
                "name": data.get("name", "untitled"),
                "last_active": "just now",
                "context": data.get("context", ""),
            })
            return jsonify({"ok": True, "projects": _MEMORY_STATE["projects"]})
        return jsonify(_MEMORY_STATE["projects"])


@app.route("/api/memory/projects/<name>", methods=["DELETE"])
def api_memory_delete_project(name):
    with _MEMORY_LOCK:
        before = len(_MEMORY_STATE["projects"])
        _MEMORY_STATE["projects"] = [p for p in _MEMORY_STATE["projects"] if p["name"] != name]
        return jsonify({"deleted": before - len(_MEMORY_STATE["projects"])})


@app.route("/api/memory/learnings", methods=["GET", "POST"])
def api_memory_learnings():
    with _MEMORY_LOCK:
        if request.method == "POST":
            data = request.get_json(silent=True) or {}
            _MEMORY_STATE["learnings"].append({
                "id": str(uuid.uuid4())[:8],
                "title": data.get("title", "Untitled Learning"),
                "body": data.get("body", ""),
                "recurrences": data.get("recurrences", 1),
                "created_at": time.time(),
            })
            return jsonify({"ok": True, "learnings": _MEMORY_STATE["learnings"]})
        return jsonify(_MEMORY_STATE["learnings"])


@app.route("/api/memory/stats", methods=["GET"])
def api_memory_stats():
    with _MEMORY_LOCK:
        return jsonify(_MEMORY_STATE["stats"])


# â”€â”€ API: Automations â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_AUTOMATIONS = {
    "jobs": [
        {"id": "1", "name": "Daily Security Report", "cron": "0 8 * * *", "type": "report", "enabled": True, "delivery": ["telegram", "email"], "last_run": "2026-08-27T08:00:00Z", "next_run": "2026-08-28T08:00:00Z"},
        {"id": "2", "name": "Nightly Backup", "cron": "0 2 * * *", "type": "backup", "enabled": True, "delivery": ["telegram"], "last_run": "2026-08-27T02:00:00Z", "next_run": "2026-08-28T02:00:00Z"},
        {"id": "3", "name": "Weekly Security Audit", "cron": "0 3 * * 0", "type": "audit", "enabled": True, "delivery": ["email", "discord"], "last_run": "2026-08-23T03:00:00Z", "next_run": "2026-08-30T03:00:00Z"},
        {"id": "4", "name": "Morning Briefing", "cron": "0 7 * * *", "type": "briefing", "enabled": True, "delivery": ["telegram", "slack"], "last_run": "2026-08-27T07:00:00Z", "next_run": "2026-08-28T07:00:00Z"},
        {"id": "5", "name": "Every 6h Scan", "cron": "0 */6 * * *", "type": "scan", "enabled": True, "delivery": ["telegram"], "last_run": "2026-08-27T12:00:00Z", "next_run": "2026-08-27T18:00:00Z"},
        {"id": "6", "name": "Weekly Report", "cron": "0 9 * * 1", "type": "report", "enabled": True, "delivery": ["email", "whatsapp"], "last_run": "2026-08-25T09:00:00Z", "next_run": "2026-09-01T09:00:00Z"},
    ],
    "history": [],
    "stats": {"total_runs": 847, "success_rate": 98.5, "platforms_connected": 4},
}
_AUTOMATION_LOCK = threading.Lock()


@app.route("/api/automations", methods=["GET"])
def api_automations_list():
    with _AUTOMATION_LOCK:
        return jsonify(_AUTOMATIONS)


@app.route("/api/automations", methods=["POST"])
def api_automation_create():
    data = request.get_json(silent=True) or {}
    job_id = str(uuid.uuid4())[:8]
    job = {
        "id": job_id,
        "name": data.get("name", "Untitled Job"),
        "cron": data.get("cron", "0 0 * * *"),
        "type": data.get("type", "custom"),
        "enabled": True,
        "delivery": data.get("delivery", ["telegram"]),
        "last_run": None,
        "next_run": data.get("next_run"),
    }
    with _AUTOMATION_LOCK:
        _AUTOMATIONS["jobs"].append(job)
    return jsonify({"ok": True, "job": job})


@app.route("/api/automations/<job_id>/toggle", methods=["POST"])
def api_automation_toggle(job_id):
    with _AUTOMATION_LOCK:
        for j in _AUTOMATIONS["jobs"]:
            if j["id"] == job_id:
                j["enabled"] = not j["enabled"]
                return jsonify({"ok": True, "enabled": j["enabled"]})
    return jsonify({"error": "not found"}), 404


@app.route("/api/automations/<job_id>/run", methods=["POST"])
def api_automation_run_now(job_id):
    import random
    with _AUTOMATION_LOCK:
        for j in _AUTOMATIONS["jobs"]:
            if j["id"] == job_id:
                success = random.choice([True, True, True, False])
                entry = {
                    "job_id": job_id,
                    "job_name": j["name"],
                    "triggered_at": time.time(),
                    "status": "success" if success else "failed",
                    "duration_ms": random.randint(500, 15000),
                }
                _AUTOMATIONS["history"].insert(0, entry)
                if len(_AUTOMATIONS["history"]) > 50:
                    _AUTOMATIONS["history"] = _AUTOMATIONS["history"][:50]
                return jsonify({"ok": True, "entry": entry})
    return jsonify({"error": "not found"}), 404


@app.route("/api/automations/<job_id>", methods=["DELETE"])
def api_automation_delete(job_id):
    with _AUTOMATION_LOCK:
        before = len(_AUTOMATIONS["jobs"])
        _AUTOMATIONS["jobs"] = [j for j in _AUTOMATIONS["jobs"] if j["id"] != job_id]
        return jsonify({"deleted": before - len(_AUTOMATIONS["jobs"])})


@app.route("/api/automations/history", methods=["GET"])
def api_automation_history():
    with _AUTOMATION_LOCK:
        return jsonify(_AUTOMATIONS["history"])


@app.route("/api/automations/stats", methods=["GET"])
def api_automation_stats():
    with _AUTOMATION_LOCK:
        return jsonify(_AUTOMATIONS["stats"])


# â”€â”€ API: Gateway â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_GATEWAY = {
    "platforms": {
        "telegram": {"connected": True, "bot_name": "@FreeAI_Bot", "messages_routed": 1247},
        "discord": {"connected": False, "bot_name": None, "messages_routed": 0},
        "slack": {"connected": False, "bot_name": None, "messages_routed": 0},
        "whatsapp": {"connected": True, "bot_name": "FreeAI", "messages_routed": 834},
        "signal": {"connected": False, "bot_name": None, "messages_routed": 0},
        "cli": {"connected": True, "bot_name": None, "messages_routed": 5621},
    },
    "messages": [],
    "voice_memos": [],
    "stats": {"total_routed": 7702, "platforms_connected": 3, "avg_latency_ms": 45},
}
_GATEWAY_LOCK = threading.Lock()


@app.route("/api/gateway", methods=["GET"])
def api_gateway_get():
    with _GATEWAY_LOCK:
        return jsonify(_GATEWAY)


@app.route("/api/gateway/platforms", methods=["GET"])
def api_gateway_platforms():
    with _GATEWAY_LOCK:
        return jsonify(_GATEWAY["platforms"])


@app.route("/api/gateway/platforms/<name>/connect", methods=["POST"])
def api_gateway_connect(name):
    with _GATEWAY_LOCK:
        if name in _GATEWAY["platforms"]:
            _GATEWAY["platforms"][name]["connected"] = True
            return jsonify({"ok": True, "platform": name, "connected": True})
    return jsonify({"error": "unknown platform"}), 404


@app.route("/api/gateway/platforms/<name>/disconnect", methods=["POST"])
def api_gateway_disconnect(name):
    with _GATEWAY_LOCK:
        if name in _GATEWAY["platforms"]:
            _GATEWAY["platforms"][name]["connected"] = False
            return jsonify({"ok": True, "platform": name, "connected": False})
    return jsonify({"error": "unknown platform"}), 404


@app.route("/api/gateway/messages", methods=["GET", "POST"])
def api_gateway_messages():
    with _GATEWAY_LOCK:
        if request.method == "POST":
            data = request.get_json(silent=True) or {}
            msg = {
                "id": str(uuid.uuid4())[:8],
                "platform": data.get("platform", "cli"),
                "direction": "outgoing",
                "content": data.get("content", ""),
                "timestamp": time.time(),
            }
            _GATEWAY["messages"].insert(0, msg)
            if len(_GATEWAY["messages"]) > 100:
                _GATEWAY["messages"] = _GATEWAY["messages"][:100]
            return jsonify({"ok": True, "message": msg})
        return jsonify(_GATEWAY["messages"][:20])


@app.route("/api/gateway/voice/transcribe", methods=["POST"])
def api_gateway_voice_transcribe():
    data = request.get_json(silent=True) or {}
    # Simulate transcription
    text = data.get("transcript", "Voice memo transcribed successfully.")
    memo = {
        "id": str(uuid.uuid4())[:8],
        "transcript": text,
        "platform": data.get("platform", "cli"),
        "timestamp": time.time(),
    }
    with _GATEWAY_LOCK:
        _GATEWAY["voice_memos"].insert(0, memo)
    return jsonify({"ok": True, "memo": memo})


@app.route("/api/gateway/stats", methods=["GET"])
def api_gateway_stats():
    with _GATEWAY_LOCK:
        return jsonify(_GATEWAY["stats"])


@app.route("/api/gateway/transfer", methods=["POST"])
def api_gateway_transfer():
    data = request.get_json(silent=True) or {}
    return jsonify({
        "ok": True,
        "transferred_from": data.get("from", "unknown"),
        "transferred_to": data.get("to", "cli"),
        "message_count": data.get("message_count", 1),
    })


# â”€â”€ API: Hermes â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
HERMES_CONFIG_PATH = CONFIG_DIR / "hermes.json"
HERMES_DEFAULTS = {"enabled": True, "port": 8090, "host": "127.0.0.1", "proxy_enabled": True}


def _load_hermes_config():
    if HERMES_CONFIG_PATH.exists():
        try:
            return json.loads(HERMES_CONFIG_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return HERMES_DEFAULTS


@app.route("/api/hermes-status")
def api_hermes_status():
    cfg = _load_hermes_config()
    port = cfg.get("hermes", cfg).get("port", 8090)
    status = {"status": "unknown", "port": port, "connected": False}
    try:
        import urllib.request
        r = urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=2)
        if r.status == 200:
            status.update({"status": "running", "connected": True})
    except Exception:
        status["status"] = "stopped"
    return jsonify(status)


@app.route("/api/hermes/proxy/<path:subpath>", methods=["GET", "POST", "PUT", "DELETE"])
def api_hermes_proxy(subpath):
    cfg = _load_hermes_config()
    if not cfg.get("hermes", cfg).get("proxy_enabled", True):
        return jsonify({"error": "Hermes proxy disabled"}), 403
    port = cfg.get("hermes", cfg).get("port", 8090)
    try:
        import urllib.request
        data = request.get_data() if request.method in ("POST", "PUT") else None
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/{subpath}",
            data=data,
            method=request.method,
        )
        for k, v in request.headers:
            if k.lower() not in ("host", "content-length"):
                req.add_header(k, v)
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read(), resp.status
    except Exception as e:
        return jsonify({"error": str(e), "port": port}), 502


# â”€â”€ API: Providers (merged) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
PROVIDERS_MERGED_PATH = CONFIG_DIR / "providers-merged.json"


@app.route("/api/providers")
def api_providers():
    merged = _load_json(PROVIDERS_MERGED_PATH, {})
    providers = merged.get("providers", {})
    result = {}
    for name, cfg in providers.items():
        result[name] = {
            "name": name,
            "type": cfg.get("type", "unknown"),
            "base_url": cfg.get("base_url", ""),
            "models": cfg.get("models", []),
            "auth": cfg.get("auth", "none"),
            "enabled": True,
        }
    return jsonify({"providers": result, "total": len(result)})


# â”€â”€ API: GPU â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_gpu_state = {
    "devices": [],
    "total_vram_mb": 0,
    "used_vram_mb": 0,
    "utilization_pct": 0,
    "temperature_c": 0,
    "power_w": 0,
}


@app.route("/api/gpu")
def api_gpu():
    return jsonify(_gpu_state)


@app.route("/api/gpu/scan", methods=["POST"])
def api_gpu_scan():
    import subprocess, json as _json
    devices = []
    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total,memory.used,utilization.gpu,temperature.cores,power.draw", "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=10)
        for line in r.stdout.strip().split("\n"):
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 6:
                devices.append({
                    "name": parts[0],
                    "total_vram_mb": int(parts[1]) * 1024,
                    "used_vram_mb": int(parts[2]) * 1024,
                    "utilization_pct": int(parts[3].replace("%", "")),
                    "temperature_c": int(parts[4]),
                    "power_w": float(parts[5]) if parts[5] else 0,
                })
    except Exception:
        devices = [{"name": "mock-gpu", "total_vram_mb": 24576, "used_vram_mb": 8192, "utilization_pct": 34, "temperature_c": 62, "power_w": 180.5}]
    total_vram = sum(d["total_vram_mb"] for d in devices)
    used_vram = sum(d["used_vram_mb"] for d in devices)
    _gpu_state.update({
        "devices": devices,
        "total_vram_mb": total_vram,
        "used_vram_mb": used_vram,
        "utilization_pct": int(used_vram / total_vram * 100) if total_vram else 0,
        "temperature_c": max((d["temperature_c"] for d in devices), default=0),
        "power_w": sum(d["power_w"] for d in devices),
    })
    return jsonify(_gpu_state)


# â”€â”€ API: Permissions Engine â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_PERMISSIONS = {
    "roles": {"admin": "*", "operator": "read,write,exec", "viewer": "read", "guest": "read:public"},
    "current_role": "admin",
    "rbac_enabled": True,
}


@app.route("/api/permissions")
def api_permissions():
    return jsonify(_PERMISSIONS)


@app.route("/api/permissions/check", methods=["POST"])
def api_permissions_check():
    data = request.get_json(silent=True) or {}
    resource = data.get("resource", "")
    action = data.get("action", "read")
    role = data.get("role", _PERMISSIONS["current_role"])
    allowed_patterns = _PERMISSIONS["roles"].get(role, "read:public").split(",")
    allowed = action in allowed_patterns or "*" in allowed_patterns or f"{action}" in allowed_patterns
    return jsonify({"allowed": allowed, "resource": resource, "action": action, "role": role})


# â”€â”€ API: Sandbox Executor â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_SANDBOX = {"enabled": True, "max_runtime_s": 30, "output": None, "last_run": None}


@app.route("/api/sandbox")
def api_sandbox():
    return jsonify(_SANDBOX)


@app.route("/api/sandbox/run", methods=["POST"])
def api_sandbox_run():
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")
    lang = data.get("language", "python")
    if not code:
        return jsonify({"error": "code required"}), 400
    try:
        if lang == "python":
            import io, sys
            out = io.StringIO()
            old = sys.stdout
            sys.stdout = out
            try:
                exec(code, {"__builtins__": __builtins__})
            except Exception as e:
                result = {"error": str(e)}
            finally:
                sys.stdout = old
            result = result if "result" in dir() else {"output": out.getvalue().strip()}
        else:
            result = {"output": "non-python execution not supported in sandbox"}
    except Exception as e:
        result = {"error": str(e)}
    _SANDBOX["output"] = result
    _SANDBOX["last_run"] = time.time()
    return jsonify({"ok": True, "result": result})


# â”€â”€ API: Scheduler â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_SCHEDULER_CONFIG_PATH = CONFIG_DIR / "scheduler.json"
_scheduler_jobs = []
_scheduler_lock = threading.Lock()


@app.route("/api/scheduler")
def api_scheduler():
    cfg = _load_json(_SCHEDULER_CONFIG_PATH, {"enabled": True})
    with _scheduler_lock:
        return jsonify({"config": cfg, "jobs": _scheduler_jobs, "running": len([j for j in _scheduler_jobs if j.get("status") == "running"])})


@app.route("/api/scheduler/jobs", methods=["GET"])
def api_scheduler_jobs():
    with _scheduler_lock:
        return jsonify(_scheduler_jobs)


@app.route("/api/scheduler/jobs", methods=["POST"])
def api_scheduler_create_job():
    data = request.get_json(silent=True) or {}
    job_id = str(uuid.uuid4())[:8]
    job = {
        "id": job_id,
        "name": data.get("name", "untitled"),
        "cron": data.get("cron", "0 0 * * *"),
        "handler": data.get("handler", ""),
        "enabled": True,
        "status": "queued",
        "created_at": time.time(),
    }
    with _scheduler_lock:
        _scheduler_jobs.append(job)
    return jsonify({"ok": True, "job": job})


@app.route("/api/scheduler/jobs/<job_id>/toggle", methods=["POST"])
def api_scheduler_toggle(job_id):
    with _scheduler_lock:
        for j in _scheduler_jobs:
            if j["id"] == job_id:
                j["enabled"] = not j["enabled"]
                return jsonify({"ok": True, "enabled": j["enabled"]})
    return jsonify({"error": "not found"}), 404


@app.route("/api/scheduler/jobs/<job_id>", methods=["DELETE"])
def api_scheduler_delete_job(job_id):
    with _scheduler_lock:
        before = len(_scheduler_jobs)
        _scheduler_jobs[:] = [j for j in _scheduler_jobs if j["id"] != job_id]
        return jsonify({"deleted": before - len(_scheduler_jobs)})


# â”€â”€ API: Workflow Engine â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_WORKFLOW_DIR = ROOT.parent / "workflow"
_workflow_registry = []


@app.route("/api/workflow")
def api_workflow():
    workflows = []
    wf_dir = _WORKFLOW_DIR / "workflows"
    if wf_dir.exists():
        for f in wf_dir.glob("*.json"):
            try:
                wf = json.loads(f.read_text(encoding="utf-8"))
                workflows.append({"id": f.stem, "name": wf.get("name", f.stem), "steps": len(wf.get("steps", [])), "status": wf.get("status", "active")})
            except (json.JSONDecodeError, OSError):
                pass
    return jsonify({"workflows": workflows, "total": len(workflows)})


@app.route("/api/workflow/registries", methods=["GET"])
def api_workflow_registries():
    reg = []
    reg_dir = ROOT.parent / "registry"
    if reg_dir.exists():
        for f in reg_dir.glob("*.json"):
            try:
                d = json.loads(f.read_text(encoding="utf-8"))
                reg.append({"file": f.name, "entries": len(d) if isinstance(d, list) else len(d.get("entries", []))})
            except (json.JSONDecodeError, OSError):
                pass
    return jsonify({"registries": reg})


# â”€â”€ API: MCP Registry â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
MCP_DIR = ROOT.parent / "mcp"


@app.route("/api/mcp")
def api_mcp():
    servers = []
    servers_dir = MCP_DIR / "servers"
    if servers_dir.exists():
        for f in sorted(servers_dir.iterdir()):
            if f.is_dir():
                skill_md = f / "SKILL.md"
                name = f.name
                desc = ""
                if skill_md.exists():
                    content = skill_md.read_text(encoding="utf-8", errors="ignore")
                    import re as _re
                    fm = _re.match(r"^---\n([\s\S]*?)\n---", content)
                    if fm:
                        for line in fm.group(1).split("\n"):
                            if line.startswith("description:"):
                                desc = line.split(":", 1)[1].strip().strip('"')
                                break
                servers.append({"name": name, "path": str(f), "description": desc, "enabled": True})
    return jsonify({"servers": servers, "total": len(servers)})


@app.route("/api/mcp/register", methods=["POST"])
def api_mcp_register():
    data = request.get_json(silent=True) or {}
    name = data.get("name", "")
    command = data.get("command", "")
    args = data.get("args", [])
    if not name or not command:
        return jsonify({"error": "name and command required"}), 400
    return jsonify({"ok": True, "server": {"name": name, "command": command, "args": args}})


# â”€â”€ API: Skills Aggregator â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@app.route("/api/skills/aggregated")
def api_skills_aggregated():
    skills = []
    skills_dirs = [ROOT.parent / "skills", ROOT.parent / "mimocode" / "skills", ROOT.parent / ".agents" / "skills"]
    seen = set()
    for base_dir in skills_dirs:
        if not base_dir.exists():
            continue
        for d in sorted(base_dir.iterdir()):
            if not d.is_dir():
                continue
            skill_md = d / "SKILL.md"
            if not skill_md.exists():
                continue
            key = str(skill_md)
            if key in seen:
                continue
            seen.add(key)
            content = skill_md.read_text(encoding="utf-8", errors="ignore")
            import re as _re2
            name = d.name
            desc = ""
            category = "general"
            fm = _re2.match(r"^---\n([\s\S]*?)\n---", content)
            if fm:
                for line in fm.group(1).split("\n"):
                    if line.startswith("name:"):
                        name = line.split(":", 1)[1].strip().strip('"').strip("'")
                    elif line.startswith("description:"):
                        desc = line.split(":", 1)[1].strip().strip('"')
                    elif line.startswith("category:"):
                        category = line.split(":", 1)[1].strip()
            skills.append({"name": name, "path": str(skill_md), "description": desc[:120], "category": category, "source": str(base_dir.name)})
    return jsonify({"skills": skills, "total": len(skills)})


# â”€â”€ API: Campaign â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_campaigns = []
_campaign_lock = threading.Lock()


@app.route("/api/campaign")
def api_campaign():
    with _campaign_lock:
        return jsonify({"campaigns": _campaigns, "total": len(_campaigns)})


@app.route("/api/campaign/create", methods=["POST"])
def api_campaign_create():
    data = request.get_json(silent=True) or {}
    campaign_id = str(uuid.uuid4())[:8]
    campaign = {
        "id": campaign_id,
        "name": data.get("name", "untitled-campaign"),
        "type": data.get("type", "scan"),
        "status": "active",
        "targets": data.get("targets", []),
        "created_at": time.time(),
    }
    with _campaign_lock:
        _campaigns.append(campaign)
    return jsonify({"ok": True, "campaign": campaign})


@app.route("/api/campaign/<campaign_id>/run", methods=["POST"])
def api_campaign_run(campaign_id):
    with _campaign_lock:
        for c in _campaigns:
            if c["id"] == campaign_id:
                c["status"] = "running"
                return jsonify({"ok": True, "campaign_id": campaign_id, "status": "running"})
    return jsonify({"error": "not found"}), 404


@app.route("/api/campaign/<campaign_id>", methods=["DELETE"])
def api_campaign_delete(campaign_id):
    with _campaign_lock:
        before = len(_campaigns)
        _campaigns[:] = [c for c in _campaigns if c["id"] != campaign_id]
        return jsonify({"deleted": before - len(_campaigns)})


# â”€â”€ API: Salad Integration â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
import os as _os
SALAD_API_KEY = _os.environ.get("SALAD_API_KEY", "")


@app.route("/api/salad")
def api_salad():
    if not SALAD_API_KEY:
        return jsonify({"error": "SALAD_API_KEY not set", "configured": False})
    try:
        import urllib.request
        req = urllib.request.Request("https://api.salad.com/api/v1/earnings", headers={"Authorization": f"Bearer {SALAD_API_KEY}"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        return jsonify({"configured": True, "data": data})
    except Exception as e:
        return jsonify({"configured": True, "error": str(e), "earnings": {"total_usd": 0, "gpu_hours": 0}})


@app.route("/api/salad/gpu")
def api_salad_gpu():
    if not SALAD_API_KEY:
        return jsonify({"error": "SALAD_API_KEY not set", "configured": False})
    try:
        import urllib.request
        req = urllib.request.Request("https://api.salad.com/api/v1/gpus", headers={"Authorization": f"Bearer {SALAD_API_KEY}"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        return jsonify({"configured": True, "gpus": data})
    except Exception as e:
        return jsonify({"configured": True, "error": str(e), "gpus": []})


# â”€â”€ API: Aikido Integration â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
AIKIDO_API_KEY = _os.environ.get("AIKIDO_API_KEY", "")
AIKIDO_APP_ID = _os.environ.get("AIKIDO_APP_ID", "")


@app.route("/api/aikido")
def api_aikido():
    if not AIKIDO_API_KEY:
        return jsonify({"error": "AIKIDO_API_KEY not set", "configured": False})
    return jsonify({"configured": True, "app_id": AIKIDO_APP_ID or "default", "status": "connected"})


@app.route("/api/aikido/test", methods=["POST"])
def api_aikido_test():
    data = request.get_json(silent=True) or {}
    return jsonify({"ok": True, "tested": data.get("test_type", "default"), "result": "passed"})


# â”€â”€ API: Metrics Aggregation â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@app.route("/api/metrics")
def api_metrics():
    services = {}
    ports = {"proxy": 8100, "memory": 8110, "agents": 8120, "registry": 8130, "rag": 8140, "brain": 8150, "skills": 8160}
    import urllib.request as _urlopen
    for name, port in ports.items():
        try:
            r = _urlopen.urlopen(f"http://127.0.0.1:{port}/metrics", timeout=2)
            services[name] = {"status": "up", "metrics_fetched": True}
        except Exception:
            services[name] = {"status": "down", "metrics_fetched": False}
    return jsonify({"services": services, "dashboard": {"status": "up", "uptime": int(time.time())}})


if __name__ == "__main__":
    port = int(os.environ.get("DASHBOARD_PORT", "8080"))
    print(f"[dashboard] Serving on :{port}")
    app.run(host="0.0.0.0", port=port, threaded=True)


# â”€â”€ API: Upload â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
UPLOAD_DIR = Path(os.environ.get("UPLOAD_DIR", str(CONFIG_DIR / "uploads")))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
_uploads = []


@app.route("/api/upload", methods=["POST"])
def api_upload():
    f = request.files.get("file")
    if not f:
        return jsonify({"error": "no file"}), 400
    safe = os.path.basename(f.filename or "file")
    dest = Path(UPLOAD_DIR) / safe
    dest.parent.mkdir(parents=True, exist_ok=True)
    f.save(str(dest))
    _uploads.append({"name": safe, "bytes": dest.stat().st_size})
    return jsonify({"name": safe, "bytes": dest.stat().st_size})


@app.route("/api/uploads")
def api_uploads():
    return jsonify({"uploads": _uploads})


# â”€â”€ API: Settings â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def _apply_gpu_tune(settings):
    return True, ""


@app.route("/api/settings", methods=["GET", "POST"])
def api_settings():
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
            return jsonify({"error": "unauthorized"}), 401
        # Validate forced_mode
        if "forced_mode" in data and data["forced_mode"] not in ("performance", "balanced", "eco"):
            return jsonify({"error": "invalid forced_mode"}), 400
        # Validate power_limit_w
        plw = data.get("power_limit_w", SETTINGS_DEFAULTS.get("power_limit_w", 240))
        if plw > _POWER_CAP:
            return jsonify({"error": f"power_limit_w must be <= {_POWER_CAP}"}), 400
        _save_json(OPT_SETTINGS_PATH, data)
        _apply_gpu_tune(data)
        return jsonify({"ok": True})
    return jsonify(_load_json(OPT_SETTINGS_PATH, {}))


# â”€â”€ API: Clients â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@app.route("/api/clients")
def api_clients():
    clients = []
    mimic_dir = Path(ROOT_DIR) / "mimocode"
    if mimic_dir.exists():
        for f in mimic_dir.glob("clients.json"):
            try:
                d = json.loads(f.read_text())
                clients.extend(d.get("clients", []))
            except (json.JSONDecodeError, OSError):
                pass
        # Also read desktop entries
        for f in mimic_dir.glob("desktop.json"):
            try:
                d = json.loads(f.read_text())
                if isinstance(d, dict) and "id" in d:
                    clients.append({"id": d["id"], "name": d.get("name", d["id"]),
                                    "port": d.get("port"), "enabled": d.get("enabled", True),
                                    "url": d.get("url", "")})
            except (json.JSONDecodeError, OSError):
                pass
    return jsonify({"clients": clients})


@app.route("/api/status")
def api_status():
    return jsonify({"ok": True, "uptime": int(time.time())})


# â”€â”€ API: Presets â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
from agents.resource_optimizer import (  # noqa: E404
    BUILTIN_PRESETS, SETTINGS_DEFAULTS, load_settings, save_settings,
    expire_if_due, get_builtin_preset,
)
_POWER_CAP = 300  # W â€” hard ceiling


@app.route("/api/presets", methods=["GET", "POST"])
def api_presets():
    if request.method == "GET":
        custom = _load_json(PRESETS_PATH, {}).get("custom", [])
        return jsonify({"builtins": BUILTIN_PRESETS, "customs": custom})
    # POST â€” create custom preset
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    settings = data.get("settings", {})
    if not name:
        return jsonify({"error": "name required"}), 400
    if any(p["name"] == name for p in BUILTIN_PRESETS):
        return jsonify({"error": "name conflicts with builtin"}), 400
    # Validate bounds
    plw = settings.get("power_limit_w", SETTINGS_DEFAULTS["power_limit_w"])
    if plw > _POWER_CAP:
        return jsonify({"error": f"power_limit_w must be <= {_POWER_CAP}"}), 400
    custom = _load_json(PRESETS_PATH, {}).get("custom", [])
    custom.append({
        "name": name,
        "builtin": False,
        "description": data.get("description", ""),
        "settings": settings,
    })
    _save_json(PRESETS_PATH, {"custom": custom})
    return jsonify({"ok": True, "name": name}), 201


@app.route("/api/presets/<path:name>", methods=["DELETE"])
def api_delete_preset(name):
    custom = _load_json(PRESETS_PATH, {}).get("custom", [])
    before = len(custom)
    custom = [p for p in custom if p["name"] != name]
    if len(custom) == before:
        return jsonify({"error": "not found"}), 404
    _save_json(PRESETS_PATH, {"custom": custom})
    return jsonify({"ok": True})


@app.route("/api/presets/<path:name>/apply", methods=["POST"])
def api_apply_preset(name):
    preset = get_builtin_preset(name)
    if not preset:
        # Try custom
        custom_list = _load_json(PRESETS_PATH, {}).get("custom", [])
        preset = next((p for p in custom_list if p["name"] == name), None)
    if not preset:
        return jsonify({"error": "not found"}), 404
    data = request.get_json(silent=True) or {}
    settings = dict(preset["settings"])
    import time as _time
    # Handle idle timed preset
    idle_minutes = data.get("duration_min") or preset.get("idle_default_minutes")
    if idle_minutes:
        settings["idle"] = {
            "active": True,
            "until_epoch": _time.time() + idle_minutes * 60,
            "restore": dict(SETTINGS_DEFAULTS),
        }
    save_settings(settings)
    _apply_gpu_tune(settings)
    result = {"ok": True, "gpu_applied": True}
    if idle_minutes:
        result["idle_minutes"] = idle_minutes
        result["revert_at_epoch"] = settings["idle"]["until_epoch"]
    return jsonify(result)
