"""Dashboard backend ΓÇö serves the unified FreeAI dashboard and skills manager.

Provides REST API endpoints and serves static HTML pages.
"""
import json
import os
import subprocess
import threading
import time
from pathlib import Path

try:
    from flask import Flask, render_template, request, jsonify, send_from_directory
except ImportError:
    Flask = None

try:
    from flask_socketio import SocketIO, emit
    _SOCKETIO_AVAILABLE = True
except ImportError:
    _SOCKETIO_AVAILABLE = False
    SocketIO = None
    emit = None

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

# ΓöÇΓöÇ WebSocket (optional, requires flask-socketio) ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
socketio = None
if _SOCKETIO_AVAILABLE:
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

    @socketio.on('connect')
    def ws_connect():
        emit('connected', {'service': 'freeai-mobile', 'ts': int(time.time())})

    @socketio.on('subscribe')
    def ws_subscribe(data):
        from flask_socketio import join_room
        room = data.get('room', 'mobile') if data else 'mobile'
        join_room(room)
        emit('subscribed', {'room': room})

    @socketio.on('unsubscribe')
    def ws_unsubscribe(data):
        from flask_socketio import leave_room
        room = data.get('room', 'mobile') if data else 'mobile'
        leave_room(room)


def _push_mobile(event_name, data):
    """Push an event to all connected mobile clients (non-blocking)."""
    if socketio is None:
        return
    try:
        socketio.emit(event_name, data, namespace='/')
    except Exception:
        pass


# ΓöÇΓöÇ In-memory state ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
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


# ΓöÇΓöÇ Pages ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("index.html")


@app.route("/skills")
def skills_page():
    return render_template("skills.html")


@app.route("/mobile")
def mobile_page():
    return render_template("mobile.html")


@app.route("/sdlc")
def sdlc_page():
    return render_template("sdlc.html")


@app.route("/campaigns")
def campaigns_page():
    return send_from_directory(str(TEMPLATES_DIR), "campaigns.html")


@app.route("/plugins")
def plugins_page():
    return send_from_directory(str(TEMPLATES_DIR), "plugins.html")


@app.route("/permissions")
def permissions_page():
    return send_from_directory(str(TEMPLATES_DIR), "permissions.html")


@app.route("/gpu")
def gpu_page():
    return send_from_directory(str(TEMPLATES_DIR), "gpu.html")


@app.route("/health")
def health_page():
    return send_from_directory(str(TEMPLATES_DIR), "health.html")


@app.route("/providers")
def providers_page():
    return send_from_directory(str(TEMPLATES_DIR), "providers.html")


@app.route("/hermes")
def hermes_page():
    return send_from_directory(str(TEMPLATES_DIR), "hermes.html")


@app.route("/orchestration")
def orchestration_page():
    return send_from_directory(str(TEMPLATES_DIR), "orchestration.html")


@app.route("/loot")
def loot_page():
    return send_from_directory(str(TEMPLATES_DIR), "loot.html")


@app.route("/c2")
def c2_page():
    return send_from_directory(str(TEMPLATES_DIR), "c2.html")


@app.route("/workflows")
def workflows_page():
    return send_from_directory(str(TEMPLATES_DIR), "workflows.html")


@app.route("/scheduler")
def scheduler_page():
    return send_from_directory(str(TEMPLATES_DIR), "scheduler.html")


@app.route("/mcp")
def mcp_page():
    return send_from_directory(str(TEMPLATES_DIR), "mcp.html")


@app.route("/browser-v2")
def browser_v2_page():
    return send_from_directory(str(TEMPLATES_DIR), "browser-v2.html")


@app.route("/downloads")
def downloads_page():
    return send_from_directory(str(TEMPLATES_DIR), "downloads.html")


@app.route("/jobs")
def jobs_page():
    return send_from_directory(str(TEMPLATES_DIR), "jobs.html")


@app.route("/clients")
def clients_page():
    return send_from_directory(str(TEMPLATES_DIR), "clients.html")

@app.route("/desktop")
def desktop_page():
    return send_from_directory(str(TEMPLATES_DIR), "desktop.html")



@app.route("/reports")
def reports_page():
    return send_from_directory(str(TEMPLATES_DIR), "reports.html")

@app.route("/sandbox")
def sandbox_page():
    return send_from_directory(str(TEMPLATES_DIR), "sandbox.html")

@app.route("/vast-ai")
def vastai_page():
    return send_from_directory(str(TEMPLATES_DIR), "vast-ai.html")

@app.route("/do")
def do_page():
    return send_from_directory(str(TEMPLATES_DIR), "do.html")

@app.route("/runpod")
def runpod_page():
    return send_from_directory(str(TEMPLATES_DIR), "runpod.html")

@app.route("/hostinger")
def hostinger_page():
    return send_from_directory(str(TEMPLATES_DIR), "hostinger.html")

@app.route("/update")
def update_page():
    return send_from_directory(str(TEMPLATES_DIR), "update.html")



@app.route("/wiki-dashboard")
def wiki_dashboard_page():
    return send_from_directory(str(TEMPLATES_DIR), "wiki-dashboard.html")

@app.route("/network")
def network_page():
    return send_from_directory(str(TEMPLATES_DIR), "network.html")

@app.route("/logs")
def logs_page():
    return send_from_directory(str(TEMPLATES_DIR), "logs.html")

@app.route("/salad")
def salad_page():
    return send_from_directory(str(TEMPLATES_DIR), "salad.html")

@app.route("/custom-agents")
def custom_agents_page():
    return send_from_directory(str(TEMPLATES_DIR), "custom-agents.html")

@app.route("/acp-agents")
def acp_agents_page():
    return send_from_directory(str(TEMPLATES_DIR), "acp-agents.html")

@app.route("/multiplexer")
def multiplexer_page():
    return send_from_directory(str(TEMPLATES_DIR), "multiplexer.html")

@app.route("/codemap")
def codemap_page():
    return send_from_directory(str(TEMPLATES_DIR), "codemap.html")

@app.route("/clonedeps")
def clonedeps_page():
    return send_from_directory(str(TEMPLATES_DIR), "clonedeps.html")

@app.route("/worktrees")
def worktrees_page():
    return send_from_directory(str(TEMPLATES_DIR), "worktrees.html")

@app.route("/presets")
def presets_page():
    return send_from_directory(str(TEMPLATES_DIR), "presets.html")

@app.route("/interview")
def interview_page():
    return send_from_directory(str(TEMPLATES_DIR), "interview.html")

@app.route("/teams")
def teams_page():
    return send_from_directory(str(TEMPLATES_DIR), "teams.html")

@app.route("/forum-admin")
def forum_admin_page():
    return send_from_directory(str(TEMPLATES_DIR), "forum-admin.html")

@app.route("/blog-admin")
def blog_admin_page():
    return send_from_directory(str(TEMPLATES_DIR), "blog-admin.html")


@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(str(STATIC_DIR), filename)


# ΓöÇΓöÇ API: Services health ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
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


# ΓöÇΓöÇ API: Skills ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
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


# ΓöÇΓöÇ API: General ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
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


# ΓöÇΓöÇ API: Browser Settings ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
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


# ΓöÇΓöÇ Permissions API ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
try:
    from permissions.engine import get_permissions
    _perm = get_permissions()
except Exception:
    _perm = None


@app.route("/api/permissions/roles")
def api_permissions_roles():
    if _perm is None:
        return jsonify({"error": "permissions module not available"})
    roles = _perm.roles.get_all_roles()
    return jsonify(list(roles.values()))


@app.route("/api/permissions/audit")
def api_permissions_audit():
    if _perm is None:
        return jsonify({"error": "permissions module not available"})
    limit = request.args.get("limit", 50, type=int)
    action = request.args.get("action", "")
    entries = _perm.get_audit_log(limit=limit, action=action)
    return jsonify(entries)


@app.route("/api/permissions/audit/clear", methods=["DELETE"])
def api_permissions_clear_audit():
    from permissions.engine import AUDIT_FILE
    if AUDIT_FILE.exists():
        AUDIT_FILE.unlink()
    return jsonify({"status": "cleared"})


# ΓöÇΓöÇ Sandbox API ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
_SANDBOX_SETTINGS = {
    "timeout": 60, "memory_mb": 512, "max_output": 50000,
    "network": False, "write": False, "subprocess": True,
}


@app.route("/api/sandbox/settings", methods=["GET"])
def sandbox_settings_get():
    return jsonify(_SANDBOX_SETTINGS)


@app.route("/api/sandbox/settings", methods=["PUT"])
def sandbox_settings_put():
    global _SANDBOX_SETTINGS
    data = request.get_json(silent=True) or {}
    _SANDBOX_SETTINGS.update(data)
    return jsonify({"status": "saved", "settings": _SANDBOX_SETTINGS})


@app.route("/api/sandbox/run", methods=["POST"])
def sandbox_run():
    try:
        from sandbox.sandbox import SandboxRunner
        runner = SandboxRunner()
        data = request.get_json(silent=True) or {}
        code = data.get("code", "")
        timeout = data.get("timeout", 30)
        result = runner.run(code, timeout=timeout, network=data.get("network", False))
        return jsonify(result.to_dict())
    except Exception as e:
        return jsonify({"exit_code": -1, "error": str(e), "stdout": "", "stderr": str(e)})


# ΓöÇΓöÇ Health API (integrated into dashboard) ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
try:
    from health.api import get_monitor
    _health_monitor = get_monitor()
except Exception:
    _health_monitor = None


@app.route("/api/health/status")
def api_health_status():
    if _health_monitor:
        return jsonify(_health_monitor.get_status())
    return jsonify({"services": {}, "summary": {"total": 0, "healthy": 0, "unhealthy": 0}})


@app.route("/api/health/restart/<name>", methods=["POST"])
def api_health_restart(name):
    if _health_monitor:
        return jsonify(_health_monitor.manual_restart(name))
    return jsonify({"error": "Health monitor not available"})


@app.route("/api/health/model/recommend")
def api_model_recommend():
    if _health_monitor:
        return jsonify(_health_monitor.get_model_recommendation(request.args.get("task", "general")))
    return jsonify({"id": "qwen2.5-7b-instruct", "name": "Qwen2.5 7B", "context": 32768, "cost": 0, "tier": "free"})


@app.route("/api/health/logs")
def api_health_logs():
    from pathlib import Path as _P
    log_file = ROOT / "data" / "health" / "health_log.jsonl"
    limit = request.args.get("limit", 50, type=int)
    if not log_file.exists():
        return jsonify({"logs": []})
    lines = log_file.read_text().strip().split("\n")
    entries = []
    for l in lines:
        if l.strip():
            try:
                entries.append(json.loads(l))
            except Exception:
                pass
    return jsonify(entries[-limit:])


@app.route("/api/health/logs/clear", methods=["DELETE"])
def api_clear_health_logs():
    log_file = ROOT / "data" / "health" / "health_log.jsonl"
    if log_file.exists():
        log_file.unlink()
    return jsonify({"status": "cleared"})


# ΓöÇΓöÇ API: Salad GPU Rental ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
@app.route("/api/salad/status")
def api_salad_status():
    import sys
    salad_path = ROOT.parent / "salad" / "client.py"
    if not salad_path.exists():
        return jsonify({"connected": False, "error": "salad module not found"})
    sys.path.insert(0, str(ROOT.parent))
    from salad.client import get_status
    return jsonify(get_status())


@app.route("/api/salad/configure", methods=["POST"])
def api_salad_configure():
    import sys
    body = request.get_json() or {}
    api_key = body.get("api_key", "")
    chef_id = body.get("chef_id", "")
    enabled = body.get("enabled", True)
    if not api_key or not chef_id:
        return jsonify({"error": "api_key and chef_id required"}), 400
    sys.path.insert(0, str(ROOT.parent))
    from salad.client import configure
    return jsonify(configure(api_key, chef_id, enabled))


@app.route("/api/salad/portal")
def api_salad_portal():
    import sys
    sys.path.insert(0, str(ROOT.parent))
    from salad.client import open_portal
    return jsonify({"portal_url": open_portal()})


@app.route("/api/salad/history")
def api_salad_history():
    from pathlib import Path as _P
    from datetime import datetime, timedelta
    history_file = CONFIG_DIR / "salad_history.json"
    if not history_file.exists():
        return jsonify({"history": [], "total_7d": 0, "last_updated": ""})
    try:
        history = json.loads(history_file.read_text())
    except Exception:
        return jsonify({"history": [], "total_7d": 0, "last_updated": ""})
    seven_days = datetime.utcnow() - timedelta(days=7)
    recent = []
    for h in history:
        try:
            dt = datetime.fromisoformat(h.get("date", "").replace("Z", "+00:00"))
            if dt > seven_days:
                recent.append(h)
        except Exception:
            pass
    total = sum(h.get("earnings", 0) for h in recent)
    return jsonify({
        "history": recent[-30:],
        "total_7d": round(total, 4),
        "last_updated": datetime.utcnow().isoformat() + "Z",
    })


if __name__ == "__main__":
    port = int(os.environ.get("DASHBOARD_PORT", "8080"))
    print(f"[dashboard] Serving on :{port}")
    app.run(host="0.0.0.0", port=port, threaded=True)


# ΓöÇΓöÇ API: Cloud Provider Validation (connect-test only, no side effects) ΓöÇΓöÇ
@app.route("/api/cloud/vastai/validate", methods=["POST"])
def api_vastai_validate():
    import urllib.request, urllib.error, json as _json
    body = request.get_json() or {}
    api_key = body.get("api_key", "").strip()
    if not api_key:
        return jsonify({"valid": False, "error": "api_key required"})
    try:
        req = urllib.request.Request(
            "https://api.vast.ai/v0/key/",
            headers={"Authorization": f"Token {api_key}"},
        )
        with urllib.request.urlopen(req, timeout=8) as r:
            data = _json.loads(r.read())
        return jsonify({"valid": True, "account": data.get("email", "unknown")})
    except urllib.error.HTTPError as e:
        return jsonify({"valid": False, "error": f"HTTP {e.code}: {e.reason}"})
    except Exception as e:
        return jsonify({"valid": False, "error": str(e)})


@app.route("/api/cloud/do/validate", methods=["POST"])
def api_do_validate():
    import urllib.request, urllib.error, json as _json
    body = request.get_json() or {}
    api_key = body.get("api_key", "").strip()
    if not api_key:
        return jsonify({"valid": False, "error": "api_key required"})
    try:
        req = urllib.request.Request(
            "https://api.digitalocean.com/v2/account",
            headers={"Authorization": f"Bearer {api_key}"},
        )
        with urllib.request.urlopen(req, timeout=8) as r:
            data = _json.loads(r.read())
        return jsonify({"valid": True, "account": data.get("account", {}).get("email", "unknown")})
    except urllib.error.HTTPError as e:
        return jsonify({"valid": False, "error": f"HTTP {e.code}: {e.reason}"})
    except Exception as e:
        return jsonify({"valid": False, "error": str(e)})


@app.route("/api/cloud/runpod/validate", methods=["POST"])
def api_runpod_validate():
    import urllib.request, urllib.error, json as _json
    body = request.get_json() or {}
    api_key = body.get("api_key", "").strip()
    if not api_key:
        return jsonify({"valid": False, "error": "api_key required"})
    try:
        req = urllib.request.Request(
            "https://api.runpod.io/graphql",
            data=_json.dumps({"query": "{ viewer { id email } }"}).encode(),
            headers={"Authorization": api_key, "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=8) as r:
            data = _json.loads(r.read())
        viewer = data.get("data", {}).get("viewer", {})
        return jsonify({"valid": True, "account": viewer.get("email", "unknown")})
    except urllib.error.HTTPError as e:
        return jsonify({"valid": False, "error": f"HTTP {e.code}: {e.reason}"})
    except Exception as e:
        return jsonify({"valid": False, "error": str(e)})


@app.route("/api/cloud/hostinger/validate", methods=["POST"])
def api_hostinger_validate():
    import urllib.request, urllib.error, json as _json
    body = request.get_json() or {}
    api_key = body.get("api_key", "").strip()
    if not api_key:
        return jsonify({"valid": False, "error": "api_key required"})
    try:
        req = urllib.request.Request(
            "https://api.hostinger.com/v1/account",
            headers={"Authorization": f"Bearer {api_key}"},
        )
        with urllib.request.urlopen(req, timeout=8) as r:
            data = _json.loads(r.read())
        return jsonify({"valid": True, "account": data.get("email", "unknown")})
    except urllib.error.HTTPError as e:
        return jsonify({"valid": False, "error": f"HTTP {e.code}: {e.reason}"})
    except Exception as e:
        return jsonify({"valid": False, "error": str(e)})



# ---- Vast.ai Status & Deploy ----
@app.route("/api/vast/status")
def api_vast_status():
    import urllib.request, urllib.error, json as _json
    key = request.args.get("key", "")
    if not key:
        return jsonify({"error": "api_key required"})
    try:
        req = urllib.request.Request(
            "https://api.vast.ai/v0/instance/",
            headers={"Authorization": "Token " + key},
        )
        with urllib.request.urlopen(req, timeout=8) as r:
            data = _json.loads(r.read())
        instances = data if isinstance(data, list) else []
        gpus = sum(1 for i in instances if i.get("state") == "running")
        return jsonify({"instances": len(instances), "active_gpus": gpus, "credits": 0, "spent_today": 0})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/api/vast/deploy", methods=["POST"])
def api_vast_deploy():
    import urllib.request, urllib.error, json as _json
    body = request.get_json() or {}
    key = body.get("api_key", "")
    if not key:
        return jsonify({"error": "api_key required"})
    try:
        req = urllib.request.Request(
            "https://api.vast.ai/v0/instance/filtered/?state=Mapped",
            headers={"Authorization": "Token " + key},
        )
        with urllib.request.urlopen(req, timeout=8) as r:
            instances = _json.loads(r.read())
        return jsonify({"instance_id": instances[0].get("id") if instances else None, "status": "ready"})
    except Exception as e:
        return jsonify({"error": str(e)})

# ---- DigitalOcean Status & Operations ----
@app.route("/api/do/status")
def api_do_status():
    import urllib.request, urllib.error, json as _json
    key = request.args.get("key", "")
    if not key:
        return jsonify({"error": "api_key required"})
    try:
        req = urllib.request.Request(
            "https://api.digitalocean.com/v2/droplets?per_page=100",
            headers={"Authorization": "Bearer " + key},
        )
        with urllib.request.urlopen(req, timeout=8) as r:
            data = _json.loads(r.read())
        droplets = data.get("droplets", [])
        active = sum(1 for d in droplets if d.get("status") == "active")
        return jsonify({"droplets": active, "k8s": 0, "spent": 0, "projects": 1, "all_droplets": droplets})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/api/do/create", methods=["POST"])
def api_do_create():
    import urllib.request, urllib.error, json as _json
    body = request.get_json() or {}
    key = body.get("api_key", "")
    name = body.get("name", "freeai-" + str(int(time.time())))
    region = body.get("region", "nyc3")
    plan = body.get("plan", "s-1vcpu-1gb")
    image = body.get("image", "ubuntu-24-04-x64")
    if not key:
        return jsonify({"error": "api_key required"})
    try:
        payload = _json.dumps({"name": name, "region": region, "size": plan, "image": image, "ssh_keys": []}).encode()
        req = urllib.request.Request(
            "https://api.digitalocean.com/v2/droplets",
            data=payload,
            headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            data = _json.loads(r.read())
        d = data.get("droplet", {})
        nets = d.get("networks", {}) or {}
        addrs = nets.get("v4", []) or []
        ip = addrs[0].get("ip_address", "") if addrs else ""
        return jsonify({"id": d.get("id"), "name": d.get("name"), "ip": ip})
    except urllib.error.HTTPError as e:
        return jsonify({"error": "HTTP " + str(e.code) + ": " + str(e.reason)})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/api/do/action", methods=["POST"])
def api_do_action():
    import urllib.request, urllib.error, json as _json
    body = request.get_json() or {}
    key = body.get("api_key", "")
    name = body.get("name", "")
    action = body.get("action", "")
    if not key or not name or not action:
        return jsonify({"error": "api_key, name, and action required"})
    try:
        req = urllib.request.Request(
            "https://api.digitalocean.com/v2/droplets?per_page=100",
            headers={"Authorization": "Bearer " + key},
        )
        with urllib.request.urlopen(req, timeout=8) as r:
            data = _json.loads(r.read())
        droplets = data.get("droplets", [])
        droplet = next((d for d in droplets if d.get("name") == name), None)
        if not droplet:
            return jsonify({"error": "Droplet not found: " + name})
        did = droplet["id"]
        payload = _json.dumps({"type": action}).encode()
        act = urllib.request.Request(
            "https://api.digitalocean.com/v2/droplets/" + str(did) + "/actions",
            data=payload,
            headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(act, timeout=10) as r:
            result = _json.loads(r.read())
        return jsonify({"action_id": result.get("action", {}).get("id"), "status": "started"})
    except urllib.error.HTTPError as e:
        return jsonify({"error": "HTTP " + str(e.code) + ": " + str(e.reason)})
    except Exception as e:
        return jsonify({"error": str(e)})

# ---- RunPod Status & Deploy ----
@app.route("/api/runpod/status")
def api_runpod_status():
    import urllib.request, urllib.error, json as _json
    key = request.args.get("key", "")
    if not key:
        return jsonify({"error": "api_key required"})
    try:
        query = "viewer { id email gpuCount moneySpentCents }"
        req = urllib.request.Request(
            "https://api.runpod.io/graphql",
            data=_json.dumps({"query": "{" + query + "}"}).encode(),
            headers={"Authorization": key, "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=8) as r:
            data = _json.loads(r.read())
        viewer = data.get("data", {}).get("viewer", {})
        return jsonify({"endpoints": 0, "gpus": viewer.get("gpuCount", 0), "spent_today": viewer.get("moneySpentCents", 0) / 100, "balance": viewer.get("moneySpentCents", 0) / 100, "email": viewer.get("email", "unknown")})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/api/runpod/deploy", methods=["POST"])
def api_runpod_deploy():
    import urllib.request, urllib.error, json as _json
    body = request.get_json() or {}
    key = body.get("api_key", "")
    template = body.get("template", "freeai-inference")
    if not key:
        return jsonify({"error": "api_key required"})
    try:
        query = "containerTemplates(name: \"" + template + "\") { id name }"
        req = urllib.request.Request(
            "https://api.runpod.io/graphql",
            data=_json.dumps({"query": "{" + query + "}"}).encode(),
            headers={"Authorization": key, "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=8) as r:
            data = _json.loads(r.read())
        templates = data.get("data", {}).get("containerTemplates", [])
        if not templates:
            return jsonify({"error": "Template not found: " + template})
        return jsonify({"endpoint_id": templates[0].get("id"), "status": "deploying", "template": templates[0].get("name")})
    except urllib.error.HTTPError as e:
        return jsonify({"error": "HTTP " + str(e.code)})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/api/runpod/action", methods=["POST"])
def api_runpod_action():
    import urllib.request, urllib.error, json as _json
    body = request.get_json() or {}
    key = body.get("api_key", "")
    pod_id = body.get("id", "")
    action = body.get("action", "")
    if not key or not pod_id or not action:
        return jsonify({"error": "api_key, id, and action required"})
    try:
        mutate = "stopPod" if action == "stop" else "deletePod"
        query = mutate + "(input: { id: \"" + pod_id + "\" }) { id }"
        req = urllib.request.Request(
            "https://api.runpod.io/graphql",
            data=_json.dumps({"query": "{" + query + "}"}).encode(),
            headers={"Authorization": key, "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            result = _json.loads(r.read())
        return jsonify({"status": action + "d", "result": result})
    except Exception as e:
        return jsonify({"error": str(e)})

# ---- Hostinger Status & Operations ----
@app.route("/api/hostinger/status")
def api_hostinger_status():
    import urllib.request, urllib.error, json as _json
    key = request.args.get("key", "")
    if not key:
        return jsonify({"error": "api_key required"})
    try:
        req = urllib.request.Request(
            "https://api.hostinger.com/v1/websites",
            headers={"Authorization": "Bearer " + key},
        )
        with urllib.request.urlopen(req, timeout=8) as r:
            data = _json.loads(r.read())
        websites = data if isinstance(data, list) else data.get("websites", [])
        return jsonify({"websites": len(websites), "domains": len(websites), "vps": 0, "renewals": 0, "resources": websites})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/api/hostinger/create", methods=["POST"])
def api_hostinger_create():
    import urllib.request, urllib.error, json as _json
    body = request.get_json() or {}
    key = body.get("api_key", "")
    domain = body.get("domain", "")
    rtype = body.get("type", "website")
    if not key or not domain:
        return jsonify({"error": "api_key and domain required"})
    try:
        payload = _json.dumps({"domain": domain, "type": rtype}).encode()
        req = urllib.request.Request(
            "https://api.hostinger.com/v1/websites",
            data=payload,
            headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            result = _json.loads(r.read())
        return jsonify({"id": result.get("id", "pending"), "domain": domain, "status": "creating"})
    except urllib.error.HTTPError as e:
        return jsonify({"error": "HTTP " + str(e.code)})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/api/hostinger/action", methods=["POST"])
def api_hostinger_action():
    import urllib.request, urllib.error, json as _json
    body = request.get_json() or {}
    key = body.get("api_key", "")
    rid = body.get("id", "")
    action = body.get("action", "")
    if not key or not rid:
        return jsonify({"error": "api_key and resource id required"})
    try:
        if action == "delete":
            req = urllib.request.Request(
                "https://api.hostinger.com/v1/websites/" + rid,
                headers={"Authorization": "Bearer " + key},
                method="DELETE",
            )
            with urllib.request.urlopen(req, timeout=10) as r:
                r.read()
        return jsonify({"status": action + "d", "id": rid})
    except urllib.error.HTTPError as e:
        return jsonify({"error": "HTTP " + str(e.code)})
    except Exception as e:
        return jsonify({"error": str(e)})

# ΓöÇΓöÇ Notification In-Memory Store ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
_notifications = []
notif_lock = threading.Lock()

# ΓöÇΓöÇ Process/Task API ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
@app.route("/api/tasks")
def api_tasks():
    try:
        import subprocess, json as _json
        if os.name == 'nt':
            out = subprocess.check_output(
                ['tasklist', '/fo', 'json', '/v'],
                stderr=subprocess.STDOUT, timeout=5
            ).decode('utf-8', errors='ignore')
            data = _json.loads(out)
            tasks = []
            for p in data.get('Process', []):
                pid = p.get('PID', 0)
                name = p.get('Image Name', '')
                mem_str = p.get('Mem Usage', '0 K')
                try:
                    mem_val = int(mem_str.replace('K', '').replace(',', '')) / 1024
                except ValueError:
                    mem_val = 0
                tasks.append({"pid": int(pid), "name": name, "mem": round(mem_val), "cpu": 0})
            return jsonify(tasks)
        else:
            out = subprocess.check_output(
                ['ps', 'aux'],
                stderr=subprocess.STDOUT, timeout=5
            ).decode('utf-8', errors='ignore')
            tasks = []
            for line in out.strip().split('\n')[1:]:
                parts = line.split(None, 10)
                if len(parts) >= 11:
                    try:
                        tasks.append({
                            "pid": int(parts[1]),
                            "name": parts[10].split()[0] if parts[10] else 'unknown',
                            "cpu": float(parts[2]) if parts[2] else 0,
                            "mem": round(float(parts[3]) if parts[3] else 0, 1),
                        })
                    except (ValueError, IndexError):
                        pass
            return jsonify(tasks[:50])
    except Exception as e:
        return jsonify([])

@app.route("/api/tasks/kill", methods=["POST"])
def api_tasks_kill():
    body = request.get_json(silent=True) or {}
    pid = body.get('pid')
    if not pid:
        return jsonify({"ok": False, "error": "pid required"})
    try:
        if os.name == 'nt':
            subprocess.run(['taskkill', '/F', '/PID', str(pid)], capture_output=True, timeout=5)
        else:
            os.kill(int(pid), 9)
        return jsonify({"ok": True, "pid": pid})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})

# ΓöÇΓöÇ Army/Agents API ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
@app.route("/api/army/roster")
def api_army_roster():
    try:
        import subprocess, json as _json
        agents = []
        if os.name == 'nt':
            out = subprocess.check_output(
                ['tasklist', '/fo', 'json', '/v'],
                stderr=subprocess.STDOUT, timeout=5
            ).decode('utf-8', errors='ignore')
            data = _json.loads(out)
            for p in data.get('Process', []):
                name = p.get('Image Name', '').lower()
                if any(kw in name for kw in ['python', 'node', 'hermes', 'codex', 'claude', 'cursor', 'agent', 'llama', 'ollama', 'vllm', 'gemini']):
                    agents.append({
                        "name": p.get('Image Name', ''),
                        "pid": int(p.get('PID', 0)),
                        "status": "running",
                        "memory": round(int(p.get('Mem Usage', '0 K').replace('K','').replace(',','')) / 1024),
                    })
        else:
            out = subprocess.check_output(['ps', 'aux'], stderr=subprocess.STDOUT, timeout=5).decode('utf-8', errors='ignore')
            for line in out.strip().split('\n')[1:]:
                parts = line.split(None, 10)
                if len(parts) >= 11:
                    cmd = parts[10].lower()
                    if any(kw in cmd for kw in ['python', 'node', 'hermes', 'codex', 'claude', 'cursor', 'agent', 'llama', 'ollama', 'vllm']):
                        agents.append({
                            "name": parts[10].split()[0],
                            "pid": int(parts[1]),
                            "status": "running",
                            "memory": float(parts[3]) if parts[3] else 0,
                        })
        return jsonify(agents[:30])
    except Exception as e:
        return jsonify([])

# ΓöÇΓöÇ System Alerts API ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
@app.route("/api/alerts")
def api_alerts():
    alerts = []
    try:
        import psutil
        cpu_pct = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        if cpu_pct > 85:
            alerts.append({"level": "warn", "message": f"CPU usage high: {cpu_pct:.0f}%"})
        if mem.percent > 90:
            alerts.append({"level": "critical", "message": f"Memory usage critical: {mem.percent:.0f}%"})
        if disk.percent > 90:
            alerts.append({"level": "warn", "message": f"Disk usage high: {disk.percent:.0f}%"})
    except Exception:
        pass
    # Check service ports
    ports = {"proxy": 8100, "memory": 8110, "agents": 8120, "registry": 8130, "rag": 8140, "brain": 8150, "skills": 8160}
    import urllib.request
    for name, port in ports.items():
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=1).read()
        except Exception:
            alerts.append({"level": "down", "message": f"Service '{name}' on port {port} is unreachable"})
    return jsonify(alerts)

# ΓöÇΓöÇ Notification API ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
@app.route("/api/notifications", methods=["GET"])
def api_notifications_get():
    limit = request.args.get("limit", 50, type=int)
    with notif_lock:
        return jsonify(_notifications[-limit:])

@app.route("/api/notifications", methods=["POST"])
def api_notifications_post():
    body = request.get_json(silent=True) or {}
    msg = body.get("msg", "")
    ntype = body.get("type", "info")
    if not msg:
        return jsonify({"error": "msg required"}), 400
    entry = {
        "id": len(_notifications) + 1,
        "msg": msg,
        "type": ntype,
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "ts": int(time.time()),
    }
    with notif_lock:
        _notifications.insert(0, entry)
        if len(_notifications) > 200:
            _notifications.pop()
    return jsonify({"ok": True, "notification": entry})

@app.route("/api/notifications", methods=["DELETE"])
def api_notifications_delete():
    with notif_lock:
        _notifications.clear()
    return jsonify({"ok": True})

# ΓöÇΓöÇ WebSocket Notification Endpoint (Server-Sent Events) ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
@app.route("/api/ws/notifications")
def api_ws_notifications():
    from flask import Response

    def event_stream():
        last_id = 0
        while True:
            with notif_lock:
                current_ids = [n["id"] for n in _notifications]
                for nid in current_ids:
                    if nid > last_id:
                        idx = current_ids.index(nid)
                        yield f"data: {json.dumps(_notifications[idx])}\n\n"
                        last_id = nid
            time.sleep(2)

    return Response(event_stream(), mimetype="text/event-stream")

# ΓöÇΓöÇ Report Generation API ----
@app.route("/api/reports/generate", methods=["POST"])
def api_reports_generate():
    import uuid as _uuid
    body = request.get_json() or {}
    rtype = body.get("type", "custom")
    target = body.get("target", "")
    notes = body.get("notes", "")
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    rid = str(_uuid.uuid4())[:8]
    REPORT_TEMPLATES = {
        "audit": {"title": "Security Audit", "sections": ["Executive Summary", "Network Scan", "Vulnerability Findings", "MITRE ATT&CK Mapping", "Remediation Plan"]},
        "compliance": {"title": "Compliance Report", "sections": ["NIST 800-171 Controls", "Access Control", "Audit & Accountability", "Configuration Mgmt"]},
        "vuln": {"title": "Vulnerability Assessment", "sections": ["Scan Summary", "Critical Findings", "High Findings", "Medium Findings", "CVSS Distribution"]},
        "agent": {"title": "Agent Activity Report", "sections": ["Agent Roster", "Task Summary", "Telemetry Stats", "Error Log", "Performance"]},
        "browser": {"title": "Browser Operation Report", "sections": ["Session Summary", "Fingerprint Profile", "Stealth Metrics", "Navigation Log", "Extracted Data"]},
        "army": {"title": "Army Deployment Report", "sections": ["Deployment Summary", "Agent Roster", "Task Results", "Failure Analysis", "Resource Usage"]},
        "service": {"title": "Service Health Report", "sections": ["Service Status", "Uptime Stats", "Error Rates", "Resource Usage", "Alerts"]},
        "custom": {"title": "Custom Report", "sections": ["Scope", "Methodology", "Findings", "Recommendations"]},
    }
    rpt = REPORT_TEMPLATES.get(rtype, REPORT_TEMPLATES["custom"])
    return jsonify({
        "id": rid, "name": rtype + "_report_" + rid, "type": rtype,
        "title": rpt["title"], "target": target or "localhost",
        "sections": rpt["sections"], "generated_at": ts, "notes": notes,
        "summary": rpt["title"] + " for " + (target or "localhost"),
    })

# ΓöÇΓöÇ Custom Agents API ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
@app.route("/api/custom-agents", methods=["GET"])
def api_custom_agents_list():
    try:
        from agents.custom_agents import list_agents
        return jsonify(list_agents())
    except Exception as e:
        return jsonify([])

@app.route("/api/custom-agents/<agent_id>", methods=["GET"])
def api_custom_agent_get(agent_id):
    try:
        from agents.custom_agents import get_agent
        agent = get_agent(agent_id)
        return jsonify(agent or {})
    except Exception as e:
        return jsonify({"error": str(e)}), 404

@app.route("/api/custom-agents", methods=["POST"])
def api_custom_agent_create():
    try:
        from agents.custom_agents import create_agent
        body = request.get_json() or {}
        agent = create_agent(
            name=body.get("name", "Untitled"),
            prompt=body.get("prompt", ""),
            model=body.get("model", "claude-sonnet"),
            provider=body.get("provider", "anthropic"),
            mcp_tools=body.get("mcp_tools", []),
            delegation_rules=body.get("delegation_rules", {}),
        )
        return jsonify(agent), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/custom-agents/<agent_id>", methods=["PUT"])
def api_custom_agent_update(agent_id):
    try:
        from agents.custom_agents import update_agent
        body = request.get_json() or {}
        agent = update_agent(agent_id, **body)
        return jsonify(agent or {})
    except Exception as e:
        return jsonify({"error": str(e)}), 404

@app.route("/api/custom-agents/<agent_id>", methods=["DELETE"])
def api_custom_agent_delete(agent_id):
    try:
        from agents.custom_agents import delete_agent
        ok = delete_agent(agent_id)
        return jsonify({"ok": ok})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ΓöÇΓöÇ ACP Agents API ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
@app.route("/api/acp-agents", methods=["GET"])
def api_acp_agents_list():
    try:
        from agents.acp_agents import list_agents
        return jsonify(list_agents())
    except Exception as e:
        return jsonify([])

@app.route("/api/acp-agents", methods=["POST"])
def api_acp_agent_create():
    try:
        from agents.acp_agents import create_agent
        body = request.get_json() or {}
        agent = create_agent(
            name=body.get("name", "Untitled"),
            provider=body.get("provider", "claude-code"),
            endpoint=body.get("endpoint", ""),
            api_key_ref=body.get("api_key_ref", ""),
            config=body.get("config", {}),
        )
        return jsonify(agent), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/acp-agents/<agent_id>/test", methods=["POST"])
def api_acp_agent_test(agent_id):
    try:
        from agents.acp_agents import test_connection
        return jsonify(test_connection(agent_id))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/acp-agents/<agent_id>", methods=["DELETE"])
def api_acp_agent_delete(agent_id):
    try:
        from agents.acp_agents import delete_agent
        ok = delete_agent(agent_id)
        return jsonify({"ok": ok})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ΓöÇΓöÇ Multiplexer API ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
@app.route("/api/multiplexer/detect", methods=["GET"])
def api_multiplexer_detect():
    try:
        from agents.multiplexer import detect_multiplexer
        return jsonify(detect_multiplexer())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/multiplexer/sessions", methods=["GET"])
def api_multiplexer_sessions():
    try:
        from agents.multiplexer import list_sessions
        mx = request.args.get("multiplexer", "tmux")
        return jsonify(list_sessions(mx))
    except Exception as e:
        return jsonify([])

@app.route("/api/multiplexer/sessions/<session_id>/output", methods=["GET"])
def api_multiplexer_output(session_id):
    try:
        from agents.multiplexer import capture_pane
        lines = request.args.get("lines", 200, type=int)
        mx = request.args.get("multiplexer", "tmux")
        return jsonify({"output": capture_pane(session_id, mx, lines)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/multiplexer/sessions/<session_id>/send", methods=["POST"])
def api_multiplexer_send(session_id):
    try:
        from agents.multiplexer import send_keys
        body = request.get_json() or {}
        keys = body.get("keys", "")
        mx = body.get("multiplexer", "tmux")
        return jsonify(send_keys(session_id, keys, mx))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ΓöÇΓöÇ Codemap API ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
@app.route("/api/codemap/generate", methods=["POST"])
def api_codemap_generate():
    try:
        from agents.codemap import generate_codemap
        body = request.get_json() or {}
        path = body.get("path", ".")
        name = body.get("name")
        return jsonify(generate_codemap(path, name))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/codemap/list", methods=["GET"])
def api_codemap_list():
    try:
        from agents.codemap import list_codemaps
        return jsonify(list_codemaps())
    except Exception as e:
        return jsonify([])

@app.route("/api/codemap/<map_id>", methods=["GET"])
def api_codemap_get(map_id):
    try:
        from agents.codemap import get_codemap
        return jsonify(get_codemap(map_id) or {})
    except Exception as e:
        return jsonify({"error": str(e)}), 404

@app.route("/api/codemap/<map_id>/mermaid", methods=["GET"])
def api_codemap_mermaid(map_id):
    try:
        from agents.codemap import get_codemap
        cmap = get_codemap(map_id)
        if cmap:
            return jsonify({"mermaid": cmap.get("mermaid", "")})
        return jsonify({"error": "Not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/codemap/<map_id>", methods=["DELETE"])
def api_codemap_delete(map_id):
    try:
        from agents.codemap import delete_codemap
        ok = delete_codemap(map_id)
        return jsonify({"ok": ok})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ΓöÇΓöÇ Clonedeps API ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
@app.route("/api/clonedeps", methods=["GET"])
def api_clonedeps_list():
    try:
        from agents.clonedeps import list_deps
        return jsonify(list_deps())
    except Exception as e:
        return jsonify([])

@app.route("/api/clonedeps/scan", methods=["POST"])
def api_clonedeps_scan():
    try:
        from agents.clonedeps import scan_project
        body = request.get_json() or {}
        path = body.get("path", ".")
        return jsonify(scan_project(path))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/clonedeps/<name>/clone", methods=["POST"])
def api_clonedeps_clone(name):
    try:
        from agents.clonedeps import clone_dep
        body = request.get_json() or {}
        return jsonify(clone_dep(body.get("dep", {}), body.get("force", False)))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/clonedeps/<name>", methods=["DELETE"])
def api_clonedeps_delete(name):
    try:
        from agents.clonedeps import remove_dep
        return jsonify(remove_dep(name))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ΓöÇΓöÇ Worktrees API ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
@app.route("/api/worktrees", methods=["GET"])
def api_worktrees_list():
    try:
        from agents.worktrees import list_worktrees
        return jsonify(list_worktrees())
    except Exception as e:
        return jsonify([])

@app.route("/api/worktrees/create", methods=["POST"])
def api_worktrees_create():
    try:
        from agents.worktrees import create_worktree
        body = request.get_json() or {}
        return jsonify(create_worktree(
            name=body.get("name", ""),
            source_branch=body.get("source_branch", "main"),
            target_path=body.get("target_path"),
        ))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/worktrees/<name>", methods=["DELETE"])
def api_worktrees_delete(name):
    try:
        from agents.worktrees import delete_worktree
        return jsonify(delete_worktree(name))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/worktrees/<name>/switch", methods=["POST"])
def api_worktrees_switch(name):
    try:
        from agents.worktrees import switch_worktree
        return jsonify(switch_worktree(name))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ΓöÇΓöÇ Presets API ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
@app.route("/api/presets", methods=["GET"])
def api_presets_list():
    try:
        from agents.presets import list_presets, get_active, get_effective_config
        return jsonify({
            "presets": list_presets(),
            "active": get_active(),
            "effective": get_effective_config(),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/presets/active", methods=["GET"])
def api_presets_active():
    try:
        from agents.presets import get_active, get_effective_config
        return jsonify({
            "active": get_active(),
            "config": get_effective_config(),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/presets/switch", methods=["POST"])
def api_presets_switch():
    try:
        from agents.presets import switch_preset
        body = request.get_json() or {}
        return jsonify(switch_preset(body.get("name", "")))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/presets/save", methods=["POST"])
def api_presets_save():
    try:
        from agents.presets import save_custom_preset
        body = request.get_json() or {}
        return jsonify(save_custom_preset(body.get("name", ""), body.get("config", {})))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ΓöÇΓöÇ Interview API ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
@app.route("/api/interview/start", methods=["POST"])
def api_interview_start():
    try:
        from agents.interview import start_interview
        body = request.get_json() or {}
        return jsonify(start_interview(body.get("title", "New Interview")))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/interview/<sid>", methods=["GET"])
def api_interview_get(sid):
    try:
        from agents.interview import get_session
        return jsonify(get_session(sid) or {})
    except Exception as e:
        return jsonify({"error": str(e)}), 404

@app.route("/api/interview/<sid>/answer", methods=["POST"])
def api_interview_answer(sid):
    try:
        from agents.interview import submit_answer
        body = request.get_json() or {}
        return jsonify(submit_answer(sid, body.get("stage_id", ""), body.get("answer", "")) or {})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/interview/<sid>/spec", methods=["GET"])
def api_interview_spec(sid):
    try:
        from agents.interview import generate_spec
        spec = generate_spec(sid)
        return jsonify({"spec": spec or ""})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/interview/list", methods=["GET"])
def api_interview_list():
    try:
        from agents.interview import list_interviews
        return jsonify(list_interviews())
    except Exception as e:
        return jsonify([])

@app.route("/api/interview/<sid>", methods=["DELETE"])
def api_interview_delete(sid):
    try:
        from agents.interview import delete_interview
        return jsonify({"ok": delete_interview(sid)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ΓöÇΓöÇ Teams API ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
@app.route("/api/teams", methods=["GET"])
def api_teams_list():
    try:
        from agents.teams import list_teams, get_roles
        return jsonify({"teams": list_teams(), "roles": get_roles()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/teams", methods=["POST"])
def api_teams_create():
    try:
        from agents.teams import create_team
        body = request.get_json() or {}
        return jsonify(create_team(body.get("name", "New Team"), body.get("description", "")))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/teams/<team_id>/members", methods=["GET"])
def api_teams_members(team_id):
    try:
        from agents.teams import get_team
        team = get_team(team_id)
        if team:
            return jsonify({"members": team.get("members", []), "leaders": team.get("leaders", [])})
        return jsonify({"error": "Not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/teams/<team_id>/invite-user", methods=["POST"])
def api_teams_invite_user(team_id):
    try:
        from agents.teams import invite_user
        body = request.get_json() or {}
        return jsonify(invite_user(team_id, body.get("email", ""), body.get("role", "user")))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/teams/invite-leader", methods=["POST"])
def api_teams_invite_leader():
    try:
        from agents.teams import invite_leader
        body = request.get_json() or {}
        return jsonify(invite_leader(body.get("email", "")))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/invites", methods=["GET"])
def api_invites_list():
    try:
        from agents.teams import get_pending_invites
        return jsonify(get_pending_invites())
    except Exception as e:
        return jsonify([])

@app.route("/api/invites/<invite_id>/approve", methods=["POST"])
def api_invites_approve(invite_id):
    try:
        from agents.teams import approve_invite
        return jsonify(approve_invite(invite_id) or {})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/invites/<invite_id>/reject", methods=["POST"])
def api_invites_reject(invite_id):
    try:
        from agents.teams import reject_invite
        return jsonify(reject_invite(invite_id) or {})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ΓöÇΓöÇ Forum AI Agent API ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
@app.route("/api/forum/ai-agent", methods=["GET"])
def api_forum_ai_get():
    try:
        from agents.forum_ai import get_config
        return jsonify(get_config())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/forum/ai-agent", methods=["PUT"])
def api_forum_ai_set():
    try:
        from agents.forum_ai import set_config
        body = request.get_json() or {}
        return jsonify(set_config(body))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/forum/ai-agent/respond", methods=["POST"])
def api_forum_airespond():
    try:
        from agents.forum_ai import generate_response
        body = request.get_json() or {}
        return jsonify(generate_response(body.get("post_content", ""), body.get("context", "")))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ΓöÇΓöÇ Blog AI Agent API ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
@app.route("/api/blog/ai-agent", methods=["GET"])
def api_blog_ai_get():
    try:
        from agents.blog_ai import get_config
        return jsonify(get_config())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/blog/ai-agent", methods=["PUT"])
def api_blog_ai_set():
    try:
        from agents.blog_ai import set_config
        body = request.get_json() or {}
        return jsonify(set_config(body))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/blog/ai-agent/generate", methods=["POST"])
def api_blog_ai_generate():
    try:
        from agents.blog_ai import generate_post
        body = request.get_json() or {}
        return jsonify(generate_post(body.get("topic", ""), body.get("style", "technical")))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/blog/posts", methods=["GET"])
def api_blog_posts():
    try:
        from agents.blog_ai import get_posts
        status = request.args.get("status")
        return jsonify(get_posts(status))
    except Exception as e:
        return jsonify([])

@app.route("/api/blog/posts", methods=["POST"])
def api_blog_create():
    try:
        from agents.blog_ai import create_post
        body = request.get_json() or {}
        return jsonify(create_post(
            title=body.get("title", ""),
            content=body.get("content", ""),
            author=body.get("author", "admin"),
            status=body.get("status", "draft"),
        )), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/blog/posts/<post_id>/publish", methods=["POST"])
def api_blog_publish(post_id):
    try:
        from agents.blog_ai import publish_post
        return jsonify(publish_post(post_id) or {})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/blog/posts/<post_id>", methods=["DELETE"])
def api_blog_delete(post_id):
    try:
        from agents.blog_ai import delete_post
        return jsonify({"ok": delete_post(post_id)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ΓöÇΓöÇ Team Chat API ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
_team_messages = {}
_team_lock = None
try:
    import threading
    _team_lock = threading.Lock()
except ImportError:
    _team_lock = type('Lock', (), {'__enter__': lambda s: s, '__exit__': lambda s, *a: None})()

@app.route("/api/team-chat/messages", methods=["GET"])
def api_team_chat_messages():
    room = request.args.get("room", "general")
    with _team_lock:
        msgs = _team_messages.get(room, [])
        return jsonify(msgs[-50:])

@app.route("/api/team-chat/messages", methods=["POST"])
def api_team_chat_send():
    body = request.get_json() or {}
    room = body.get("room", "general")
    user = body.get("user", "anonymous")
    content = body.get("content", "")
    if not content:
        return jsonify({"error": "content required"}), 400
    msg = {
        "id": len(_team_messages.get(room, [])) + 1,
        "user": user,
        "content": content,
        "room": room,
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "ts": int(time.time()),
    }
    with _team_lock:
        if room not in _team_messages:
            _team_messages[room] = []
        _team_messages[room].append(msg)
    return jsonify({"ok": True, "message": msg})

@app.route("/api/team-chat/users", methods=["GET"])
def api_team_chat_users():
    return jsonify([
        {"user": "admin", "role": "admin", "online": True},
        {"user": "bot", "role": "bot", "online": True},
    ])

@app.route("/api/chatbot/settings", methods=["GET"])
def api_chatbot_settings():
    return jsonify({"mode": "popup", "features": ["questions", "specialist", "team"]})

@app.route("/api/chatbot/settings", methods=["POST"])
def api_chatbot_settings_set():
    body = request.get_json() or {}
    return jsonify({"ok": True, "settings": body})
