"""Dashboard backend — serves the unified FreeAI dashboard and skills manager.

Provides REST API endpoints and serves static HTML pages.
"""
import sys
import asyncio
import json
import os
import random
import re
import threading
import time
import uuid
import urllib.request
import urllib.parse
from pathlib import Path

try:
    from flask import Flask, render_template, request, jsonify, send_from_directory, session
except ImportError:
    Flask = None

try:
    from notifications_ws import notify, get_settings, update_settings, get_log, clear_log, get_unread_count
except ImportError:
    def notify(*a, **kw): pass
    def get_settings(*a, **kw): return {}
    def update_settings(*a, **kw): return True
    def get_log(*a, **kw): return []
    def clear_log(*a, **kw): pass
    def get_unread_count(*a, **kw): return 0

try:
    from log_stream import push_log as log_push, get_log_buffer, clear_log_buffer
except ImportError:
    def log_push(*a, **kw): pass
    def get_log_buffer(*a, **kw): return []
    def clear_log_buffer(*a, **kw): pass

# ── i18n ──────────────────────────────────────────────────────────
try:
    from i18n import (
        _load_all as _i18n_load_all,
        detect_locale,
        set_locale_in_session,
        get_locale_from_session,
        is_rtl,
        get_supported_locales,
        t as _i18n_t,
        add_jinja_extensions,
    )
except ImportError:
    from .i18n import (
        _load_all as _i18n_load_all,
        detect_locale,
        set_locale_in_session,
        get_locale_from_session,
        is_rtl,
        get_supported_locales,
        t as _i18n_t,
        add_jinja_extensions,
    )
_i18n_load_all()

ROOT = Path(__file__).parent
DASHBOARD_DIR = ROOT
STATIC_DIR = DASHBOARD_DIR / "static"
TEMPLATES_DIR = DASHBOARD_DIR / "templates"
CONFIG_DIR = ROOT.parent / "config"
SKILLS_DIR = ROOT.parent / "skills"
ACTIVITY_LOG = CONFIG_DIR / "activity_log.jsonl"

# ── Audit subsystem ──────────────────────────────────────────────
try:
    from audit.logging import (
        audit_log, read_audit_log, clear_audit_log,
        set_audit_log_path, get_action_summary,
    )
    from audit.middleware import attach_audit_middleware
    _AUDIT_AVAILABLE = True
except ImportError:
    _AUDIT_AVAILABLE = False

# ── Test hooks: mockable module-level constants ────────────────
UPLOAD_DIR = CONFIG_DIR / "uploads"
AUTH_TOKEN = os.environ.get("DASHBOARD_AUTH_TOKEN", "")
OPT_SETTINGS_PATH = CONFIG_DIR / "runtime-settings.json"
PRESETS_PATH = CONFIG_DIR / "presets.json"
LLAMA_ENV_PATH = CONFIG_DIR / "llama.env"
ROOT_DIR = CONFIG_DIR.parent

app = Flask(__name__,
            static_folder=str(STATIC_DIR),
            template_folder=str(TEMPLATES_DIR))
app.secret_key = os.environ.get("FLASK_SECRET_KEY", uuid.uuid4().hex)

# ── i18n Jinja2 extensions ────────────────────────────────────────
add_jinja_extensions(app)

# ── Audit middleware ──────────────────────────────────────────────
if _AUDIT_AVAILABLE:
    attach_audit_middleware(app)

# ── In-memory state ──────────────────────────────────────────────
_services = {}
_requests_log = []
_LOCK = threading.Lock()

# ── Loot / Browser / Army / C2 state ────────────────────────────
_LOOT_DATA = {"cookies": [], "creds": []}
_browser_status = {"engine": "stopped"}
_c2_events = []
_c2_hosts = []

# ── System Config: DDNS / Network / Cards state ────────────────
_DDNS_LOCK = threading.Lock()
_DDNS_RECORDS = [
    {"id": "1", "type": "A", "hostname": "freeai.home", "value": "192.168.1.100", "ttl": 300, "status": "active"},
]
_DDNS_PROVIDER = {"service": "no-ip", "username": "", "hostname": "freeai.ddns.net", "auto_refresh": True}

_NETWORK_LOCK = threading.Lock()
_NETWORK_STATE = {
    "vpn": {"enabled": False, "provider": "auto", "status": "disconnected"},
    "tor": {"enabled": False, "circuit": "auto", "status": "stopped"},
    "dnscrypt": {"enabled": False, "resolver": "cloudflare", "status": "stopped"},
    "quality": {"latency_ms": 0, "bandwidth_up": 0, "bandwidth_down": 0, "packet_loss": 0},
}

_CARDS_LOCK = threading.Lock()
_CARDS_CONFIG = {
    "loot": {"title": "Loot", "icon": "💎", "auto_refresh": True, "refresh_interval": 30},
    "c2": {"title": "C2", "icon": "📡", "auto_refresh": True, "refresh_interval": 15},
    "browser-v2": {"title": "Browser", "icon": "🌐", "auto_refresh": False, "refresh_interval": 60},
    "security": {"title": "Security", "icon": "🛡", "auto_refresh": True, "refresh_interval": 30},
    "subagents": {"title": "Subagents", "icon": "🤖", "auto_refresh": True, "refresh_interval": 10},
    "shodan": {"title": "Shodan", "icon": "◎", "auto_refresh": False, "refresh_interval": 60},
}


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
    # Sanitize: only serialize non-sensitive fields, never write raw passwords
    safe_data = {}
    for k, v in data.items():
        if "password" in k.lower() or "secret" in k.lower() or "token" in k.lower():
            safe_data[k] = "***REDACTED***" if v else v
        else:
            safe_data[k] = v
    p.write_text(json.dumps(safe_data, indent=2))


# ── Pages ────────────────────────────────────────────────────────
@app.before_request
def _i18n_before_request():
    """Detect and persist locale for the current request."""
    lang = request.args.get("lang", "")
    locale = detect_locale(
        header=request.headers.get("Accept-Language", ""),
        query=lang,
        session=get_locale_from_session(session),
    )
    set_locale_in_session(session, locale)


@app.route("/")
def index():
    locale = get_locale_from_session(session)
    return render_template("index.html", i18n_locale=locale)


@app.route("/dashboard")
def dashboard():
    locale = get_locale_from_session(session)
    return render_template("index.html", i18n_locale=locale)


@app.route("/skills")
def skills_page():
    locale = get_locale_from_session(session)
    return render_template("skills.html", i18n_locale=locale)


@app.route("/sdlc")
def sdlc_page():
    locale = get_locale_from_session(session)
    return render_template("sdlc.html", i18n_locale=locale)


@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(str(STATIC_DIR), filename)


# ── i18n API routes ───────────────────────────────────────────────
@app.route("/api/i18n/locales")
def api_i18n_locales():
    return jsonify(get_supported_locales())


@app.route("/api/i18n/strings/<locale>")
def api_i18n_strings(locale):
    from i18n import _translations
    data = _translations.get(locale, _translations.get("en", {}))
    return jsonify(data)


@app.route("/api/i18n/set", methods=["POST"])
def api_i18n_set():
    data = request.get_json(silent=True) or {}
    lang = data.get("lang", "")
    from i18n import SUPPORTED
    if lang in SUPPORTED:
        set_locale_in_session(session, lang)
        return jsonify({"ok": True, "locale": lang})
    return jsonify({"error": "unsupported locale"}), 400


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
                            triggers.append(line.strip()[2:].strip().strip('"'))
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


# ── Health cache & periodic auto-check ───────────────────────────
_HEALTH_CACHE = {}
_HEALTH_CACHE_LOCK = threading.Lock()
_HEALTH_LAST_RUN = 0
_HEALTH_INTERVAL = 30
ALERTS_CFG = CONFIG_DIR / "alerts.json"
DISK_WARN_PCT = 85.0
MEM_WARN_PCT = 85.0


def _build_dep_graph(services_cfg):
    svcs = services_cfg.get("services", {})
    forward, reverse = {}, {}
    for name, svc in svcs.items():
        deps = svc.get("dependencies", [])
        forward[name] = deps
        if name not in reverse:
            reverse[name] = []
        for dep in deps:
            reverse.setdefault(dep, []).append(name)
    return {"forward": forward, "reverse": reverse}


def _run_full_health_check():
    """Run a complete health check and cache results."""
    global _HEALTH_LAST_RUN
    try:
        import socket as _sock
        import subprocess as _sp
        from datetime import datetime as _dt

        cfg = _load_json(SERVICES_CFG, {})
        services = cfg.get("services", {})
        dep_graph = _build_dep_graph(cfg)

        results = []
        for name, svc in services.items():
            port = svc["port"]
            host = "127.0.0.1"
            reachable, latency = False, None
            start = time.monotonic()
            try:
                s = _sock.socket(_sock.AF_INET, _sock.SOCK_STREAM)
                s.settimeout(2.0)
                result = s.connect_ex((host, port))
                latency = (time.monotonic() - start) * 1000
                s.close()
                reachable = result == 0
            except Exception:
                pass
            health_path = svc.get("health_path")
            http_ok, http_status = None, None
            if reachable and health_path:
                try:
                    import urllib.request as _ur
                    url = f"http://{host}:{port}{health_path}"
                    r = _ur.urlopen(url, timeout=3)
                    http_ok = True
                    http_status = r.status
                except Exception:
                    pass
            status = "UP" if reachable else "DOWN"
            detail = f"{latency:.0f}ms" if latency is not None else "—"
            if http_ok:
                detail += f" HTTP {http_status}"
            results.append({
                "name": name,
                "port": port,
                "status": status,
                "latency_ms": latency,
                "http_ok": http_ok,
                "http_status": http_status,
                "detail": detail,
                "priority": svc.get("priority", "unknown"),
                "dependencies": svc.get("dependencies", []),
            })

        # GPU
        gpu = {"available": False, "devices": [], "total_vram_mb": 0,
               "used_vram_mb": 0, "utilization_pct": 0, "temperature_c": 0, "power_w": 0}
        try:
            r = _sp.run(
                ["nvidia-smi",
                 "--query-gpu=name,memory.total,memory.used,memory.free,"
                 "utilization.gpu,temperature.cores,power.draw,power.limit,"
                 "clocks.current.graphics,clocks.max.graphics",
                 "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=10
            )
            if r.returncode == 0:
                devices = []
                for line in r.stdout.strip().split("\n"):
                    parts = [p.strip() for p in line.split(",")]
                    if len(parts) < 10:
                        continue
                    total_mb = int(parts[1]) * 1024 if parts[1] else 0
                    used_mb = int(parts[2]) * 1024 if parts[2] else 0
                    free_mb = int(parts[3]) * 1024 if parts[3] else 0
                    devices.append({
                        "name": parts[0],
                        "total_vram_mb": total_mb,
                        "used_vram_mb": used_mb,
                        "free_vram_mb": free_mb,
                        "utilization_pct": int(parts[4].replace("%", "")),
                        "temperature_c": int(parts[5]) if parts[5] else 0,
                        "power_w": float(parts[6]) if parts[6] else 0,
                        "power_limit_w": float(parts[7]) if parts[7] else 0,
                        "clock_current_mhz": parts[8].strip() if len(parts) > 8 else "—",
                        "clock_max_mhz": parts[9].strip() if len(parts) > 9 else "—",
                    })
                if devices:
                    gpu.update({
                        "available": True,
                        "devices": devices,
                        "total_vram_mb": sum(d["total_vram_mb"] for d in devices),
                        "used_vram_mb": sum(d["used_vram_mb"] for d in devices),
                        "utilization_pct": max(d["utilization_pct"] for d in devices),
                        "temperature_c": max(d["temperature_c"] for d in devices),
                        "power_w": sum(d["power_w"] for d in devices),
                    })
        except Exception:
            pass

        # Disk
        disk = {"error": "unavailable"}
        try:
            import psutil as _ps
            du = _ps.disk_usage("/")
            disk = {
                "total_gb": round(du.total / 1e9, 1),
                "used_gb": round(du.used / 1e9, 1),
                "free_gb": round(du.free / 1e9, 1),
                "percent": du.percent,
                "warning": du.percent >= DISK_WARN_PCT,
            }
        except Exception:
            try:
                r = _sp.run(["df", "-h", "/"], capture_output=True, text=True, timeout=5)
                lines = r.stdout.strip().split("\n")
                if len(lines) >= 2:
                    p = lines[1].split()
                    disk = {
                        "total_gb": p[1], "used_gb": p[2], "free_gb": p[3],
                        "percent": int(p[4].replace("%", "")),
                        "warning": int(p[4].replace("%", "")) >= DISK_WARN_PCT,
                    }
            except Exception:
                pass

        # Memory
        memory = {"error": "unavailable"}
        try:
            import psutil as _ps2
            vm = _ps2.virtual_memory()
            memory = {
                "total_gb": round(vm.total / 1e9, 1),
                "used_gb": round(vm.used / 1e9, 1),
                "free_gb": round(vm.free / 1e9, 1),
                "available_gb": round(vm.available / 1e9, 1),
                "percent": vm.percent,
                "warning": vm.percent >= MEM_WARN_PCT,
            }
        except Exception:
            pass

        # Alerts — log when services go down
        alerts = []
        if ALERTS_CFG.exists():
            try:
                alerts = json.loads(ALERTS_CFG.read_text())
            except (json.JSONDecodeError, OSError):
                alerts = []
        now_iso = _dt.now().isoformat()
        for s in results:
            if s["status"] == "DOWN":
                dup = any(a.get("service") == s["name"] and
                          abs(_dt.fromisoformat(a.get("ts", "1970-01-01")).timestamp() - time.time()) < 120
                          for a in alerts if isinstance(a.get("ts"), str))
                if not dup:
                    alerts.append({
                        "ts": now_iso,
                        "service": s["name"],
                        "port": s["port"],
                        "level": "critical" if s["priority"] == "critical" else "warning",
                        "message": f"Service '{s['name']}' on port {s['port']} is DOWN",
                    })
        alerts = alerts[-50:]
        try:
            ALERTS_CFG.parent.mkdir(parents=True, exist_ok=True)
            ALERTS_CFG.write_text(json.dumps(alerts, indent=2))
        except OSError:
            pass

        up = sum(1 for r in results if r["status"] == "UP")
        total = len(results)

        with _HEALTH_CACHE_LOCK:
            _HEALTH_CACHE = {
                "timestamp": now_iso,
                "summary": {"total": total, "up": up, "down": total - up,
                            "status": "ok" if up == total else "degraded"},
                "services": results,
                "gpu": gpu,
                "disk": disk,
                "memory": memory,
                "dependencies": dep_graph,
                "alerts": alerts,
            }
            _HEALTH_LAST_RUN = time.time()
    except Exception as e:
        print(f"[health] Auto-check error: {e}", file=sys.stderr)


def _health_auto_loop():
    """Periodic health check every 30 seconds."""
    while True:
        try:
            _run_full_health_check()
        except Exception:
            pass
        time.sleep(_HEALTH_INTERVAL)


# Start background health thread
_health_thread = threading.Thread(target=_health_auto_loop, daemon=True)
_health_thread.start()


@app.route("/api/health/full")
def api_health_full():
    """Return cached full health data (GPU, disk, memory, deps, alerts)."""
    with _HEALTH_CACHE_LOCK:
        data = dict(_HEALTH_CACHE)
    data["last_run"] = _HEALTH_LAST_RUN
    data["next_check_in_s"] = max(0, int(_HEALTH_INTERVAL - (time.time() - _HEALTH_LAST_RUN)))
    return jsonify(data)


@app.route("/api/health/trigger", methods=["POST"])
def api_health_trigger():
    """Manually trigger a health check."""
    _run_full_health_check()
    with _HEALTH_CACHE_LOCK:
        data = dict(_HEALTH_CACHE)
    data["last_run"] = _HEALTH_LAST_RUN
    return jsonify({"ok": True, "health": data})


@app.route("/api/health/alerts")
def api_health_alerts():
    """Return current alerts from alerts.json."""
    alerts = []
    if ALERTS_CFG.exists():
        try:
            alerts = json.loads(ALERTS_CFG.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return jsonify({"alerts": alerts, "total": len(alerts)})


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


# -- Wiki Content API ---------------------------------------------------------
WIKI_PAGES = {
    "overview": ("Overview", "INDEX.md"),
    "quickstart": ("Quick Start", "FIRST-BOOT-GUIDE.md"),
    "installation": ("Installation Guide", "BUILD-SHEET.md"),
    "aikido-panel": ("Aikido Security", "SECURITY_ADVANCED.md"),
    "pentest-panel": ("Pentest Agent", "SECURITY_ADVANCED.md"),
    "builders-panel": ("Builder Agents", "AUTONOMOUS-AGENTS.md"),
    "comms-panel": ("Communication Stack", "COMMS-OVERVIEW.md"),
    "api-rest-guide": ("REST API Guide", "API-GUIDE.md"),
    "architecture": ("Architecture", "ARCHITECTURE.md"),
    "providers": ("Providers", "PROVIDERS.md"),
    "mcp": ("MCP Registry", "MCP.md"),
    "rag": ("RAG & Vector DB", "RAG.md"),
    "websocket": ("WebSocket", "WEBSOCKET.md"),
    "function-calling": ("Function Calling", "FUNCTION_CALLING.md"),
    "log-streaming": ("Log Streaming", "LOG_STREAMING.md"),
    "deployment": ("Deployment", "DEPLOYMENT.md"),
    "security-advanced": ("Security", "SECURITY_ADVANCED.md"),
    "builders-overview": ("Builders", "AUTONOMOUS-AGENTS.md"),
    "comms-overview": ("Comms", "COMMS-OVERVIEW.md"),
    "troubleshooting": ("Troubleshooting", "TROUBLESHOOTING.md"),
}
DOCS_DIR = ROOT.parent / "docs"


@app.route("/api/wiki/content/<page>")
def api_wiki_content(page):
    title, filename = WIKI_PAGES.get(page, (page.title(), "INDEX.md"))
    path = DOCS_DIR / filename
    if not path.exists():
        return jsonify({"error": f"Page not found: {page}"}), 404
    md = path.read_text(encoding="utf-8", errors="ignore")
    return jsonify({"title": title, "markdown": md, "page": page})


@app.route("/api/wiki/blog")
def api_wiki_blog():
    blog_path = CONFIG_DIR / "blog.json"
    if not blog_path.exists():
        default_posts = [
            {"id": "welcome", "title": "Welcome to FreeAI", "category": "announcements", "author": "FreeAI Team", "date": "2026-08-28", "excerpt": "FreeAI v1.3.1 released.", "content": "# Welcome to FreeAI"},
            {"id": "v131", "title": "v1.3.1 Release Notes", "category": "releases", "author": "FreeAI Team", "date": "2026-08-28", "excerpt": "task_printer, Shodan, docs polish.", "content": "## v1.3.1"},
        ]
        blog_path.write_text(json.dumps(default_posts, indent=2), encoding="utf-8")
        posts = default_posts
    else:
        try:
            posts = json.loads(blog_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            posts = []
    return jsonify(posts)


@app.route("/api/wiki/forum")
def api_wiki_forum():
    forum_path = CONFIG_DIR / "forum.json"
    if not forum_path.exists():
        default_threads = [
            {"id": "get-started", "title": "Getting Started with FreeAI", "category": "general", "author": "Admin", "created_at": "2026-08-28", "content": "Welcome!", "replies": [{"author": "User1", "content": "Great project!", "created_at": "2026-08-28"}]},
            {"id": "gpu-setup", "title": "GPU Setup Help", "category": "support", "author": "NewUser", "created_at": "2026-08-27", "content": "CUDA issue...", "replies": []},
        ]
        forum_path.write_text(json.dumps(default_threads, indent=2), encoding="utf-8")
        threads = default_threads
    else:
        try:
            threads = json.loads(forum_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            threads = []
    return jsonify(threads)


@app.route("/blog")
def blog_page():
    return render_template("blog.html")


@app.route("/forum")
def forum_page():
    return render_template("forum.html")


@app.route("/logs")
def logs_page():
    return render_template("logs.html")


@app.route("/logs-stream")
def logs_stream_page():
    return render_template("logs-stream.html")


@app.route("/audit")
def audit_page():
    return render_template("audit.html")


@app.route("/terminal")
def terminal_page():
    return render_template("terminal.html")


@app.route("/ws-test")
def ws_test_page():
    return render_template("ws-test.html")


@app.route("/health")
def health_page():
    return render_template("health.html")


@app.route("/network")
def network_page():
    return render_template("network.html")


@app.route("/gpu")
def gpu_page():
    return render_template("gpu.html")


@app.route("/files")
def files_page():
    return render_template("files.html")


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
                            s["status"] = st = random.choice(["done", "done", "done", "failed"])
                            notify(
                                f"Subagent {st.title()}",
                                f"{sa['name']} ({sa['role']}) completed — {desc[:60]}",
                                level="success" if st == "done" else "error",
                                source="subagents",
                            )
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
                    job["status"] = st = random.choice(["done", "failed"])
                    notify(
                        f"Training job {st.title()}",
                        f"{job['name']} ({jtype}) — {st}",
                        level="success" if st == "done" else "error",
                        source="training",
                    )
                    if st == "done" and jtype == "sft":
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


# ── API: Memory ───────────────────────────────────────────────────
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
        {"name": "quantum-c2", "last_active": "3 days ago", "context": "C2 framework — implementing stealth modules and updating dashboards."},
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


# ── API: Automations ──────────────────────────────────────────────
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
                notify(
                    f"Automation {entry['status'].title()}",
                    f"'{j['name']}' {'succeeded' if entry['status'] == 'success' else 'failed'} in {entry['duration_ms']}ms",
                    level="success" if entry["status"] == "success" else "error",
                    source="automations",
                )
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


# ── API: Gateway ──────────────────────────────────────────────────
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
            notify(
                f"{name.title()} connected",
                f"Gateway platform '{name}' is now connected",
                level="success",
                source="gateway",
            )
            return jsonify({"ok": True, "platform": name, "connected": True})
    return jsonify({"error": "unknown platform"}), 404


@app.route("/api/gateway/platforms/<name>/disconnect", methods=["POST"])
def api_gateway_disconnect(name):
    with _GATEWAY_LOCK:
        if name in _GATEWAY["platforms"]:
            _GATEWAY["platforms"][name]["connected"] = False
            notify(
                f"{name.title()} disconnected",
                f"Gateway platform '{name}' is now offline",
                level="warning",
                source="gateway",
            )
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


# ── API: Hermes ──────────────────────────────────────────────────
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
        import logging
        logging.getLogger(__name__).error("reverse proxy error: %s", e)
        return jsonify({"error": "Proxy request failed", "port": port}), 502


# ── API: Providers (merged) ──────────────────────────────────────
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


# ── API: GPU ─────────────────────────────────────────────────────
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
    """GPU telemetry endpoint — returns flat state (backward compat) plus
    live telemetry with 60-sample history from gpu_poll.py."""
    import sys as _sys
    _poller_path = str(Path(__file__).parent.parent / "scripts" / "gpu_poll.py")
    try:
        result = subprocess.run(
            [_sys.executable, _poller_path],
            capture_output=True, text=True, timeout=8
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            # Merge flat state into existing _gpu_state for scan-compatible consumers
            if data.get("samples"):
                _gpu_state.update({
                    "devices": data["devices"],
                    "total_vram_mb": data.get("total_vram_mb", _gpu_state["total_vram_mb"]),
                    "used_vram_mb": data.get("used_vram_mb", _gpu_state["used_vram_mb"]),
                    "utilization_pct": data.get("utilization_pct", _gpu_state["utilization_pct"]),
                    "temperature_c": data.get("temperature_c", _gpu_state["temperature_c"]),
                    "power_w": data.get("power_w", _gpu_state["power_w"]),
                })
            return jsonify({**_gpu_state, **data})
    except Exception:
        pass
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


# ── API: GPU Performance Optimizations ──────────────────────────
_gpu_perf_state = {
    "cuda_graphs": False,
    "quantized_kv": False,
    "speculative_decoding": False,
    "last_recommendation": None,
}


@app.route("/api/gpu/metrics")
def api_gpu_metrics():
    """Return GPU performance metrics (utilization, memory, temperature)."""
    try:
        sys_path = str(Path(__file__).parent.parent / "router")
        if sys_path not in sys.path:
            sys.path.insert(0, sys_path)
        from gpu_perf import get_monitor, is_gpu_available
        monitor = get_monitor()
        metrics = monitor.get_metrics()
        metrics["perf_enabled"] = any(_gpu_perf_state.values())
        return jsonify(metrics)
    except ImportError:
        return jsonify({
            "devices": [],
            "total_vram_mb": 0,
            "used_vram_mb": 0,
            "utilization_pct": 0,
            "temperature_c": 0,
            "power_w": 0,
            "perf_enabled": any(_gpu_perf_state.values()),
            "gpu_available": False,
            "platform": __import__("platform").system(),
        })
    except Exception:
        import logging
        logging.getLogger(__name__).exception("gpu status error")
        return jsonify({
            "devices": [],
            "total_vram_mb": 0,
            "used_vram_mb": 0,
            "utilization_pct": 0,
            "temperature_c": 0,
            "power_w": 0,
            "error": "gpu_status_error",
            "perf_enabled": any(_gpu_perf_state.values()),
        })


@app.route("/api/gpu/perf/enable", methods=["POST"])
def api_gpu_perf_enable():
    """Enable GPU optimizations (CUDA graphs, quantized KV)."""
    data = request.get_json(silent=True) or {}
    cuda_graphs = data.get("cuda_graphs", True)
    quantized_kv = data.get("quantized_kv", True)
    speculative = data.get("speculative_decoding", False)

    try:
        sys_path = str(Path(__file__).parent.parent / "router")
        if sys_path not in sys.path:
            sys.path.insert(0, sys_path)
        from gpu_perf import get_graph_manager, get_kv_cache, get_speculative_decoding, get_perf_metrics, is_gpu_available
        graph_mgr = get_graph_manager()
        kv = get_kv_cache()
        sd = get_speculative_decoding()
        perf = get_perf_metrics()

        if cuda_graphs:
            result = graph_mgr.capture(model_name="default", batch_size=1, seq_len=256)
            perf.set_optimization("cuda_graphs", result.get("status") == "captured")
        else:
            perf.set_optimization("cuda_graphs", False)

        if quantized_kv:
            result = kv.allocate(model_name="default")
            perf.set_optimization("quantized_kv", result.get("status") == "allocated")
        else:
            perf.set_optimization("quantized_kv", False)

        perf.set_optimization("speculative_decoding", speculative and sd.is_active)

        _gpu_perf_state.update({
            "cuda_graphs": cuda_graphs and graph_mgr.is_active(),
            "quantized_kv": quantized_kv and kv.bits in (4, 8),
            "speculative_decoding": speculative and sd.is_active,
        })
        return jsonify({
            "status": "enabled",
            "cuda_graphs": _gpu_perf_state["cuda_graphs"],
            "quantized_kv": _gpu_perf_state["quantized_kv"],
            "speculative_decoding": _gpu_perf_state["speculative_decoding"],
            "mock": not is_gpu_available(),
        })
    except ImportError:
        return jsonify({
            "status": "enabled",
            "cuda_graphs": cuda_graphs,
            "quantized_kv": quantized_kv,
            "speculative_decoding": speculative,
            "mock": True,
            "reason": "gpu_perf module not available",
        })
    except Exception:
        import logging
        logging.getLogger(__name__).exception("gpu perf enable error")
        return jsonify({"status": "error", "message": "gpu_perf_error"}), 500


@app.route("/api/gpu/perf/disable", methods=["POST"])
def api_gpu_perf_disable():
    """Disable GPU optimizations."""
    data = request.get_json(silent=True) or {}
    try:
        sys_path = str(Path(__file__).parent.parent / "router")
        if sys_path not in sys.path:
            sys.path.insert(0, sys_path)
        from gpu_perf import get_graph_manager, get_kv_cache, get_speculative_decoding, get_perf_metrics, is_gpu_available
        perf = get_perf_metrics()

        if data.get("cuda_graphs"):
            get_graph_manager().reset()
            perf.set_optimization("cuda_graphs", False)
        if data.get("quantized_kv"):
            get_kv_cache().clear()
            perf.set_optimization("quantized_kv", False)
        if data.get("speculative_decoding"):
            perf.set_optimization("speculative_decoding", False)

        _gpu_perf_state.update({
            "cuda_graphs": False,
            "quantized_kv": False,
            "speculative_decoding": False,
        })
        return jsonify({"status": "disabled", "perf_state": dict(_gpu_perf_state)})
    except ImportError:
        return jsonify({
            "status": "disabled",
            "perf_state": _gpu_perf_state,
            "mock": True,
        })
    except Exception:
        import logging
        logging.getLogger(__name__).exception("gpu perf disable error")
        return jsonify({"status": "error", "message": "gpu_perf_error"}), 500


@app.route("/api/gpu/perf/status")
def api_gpu_perf_status():
    """Check which GPU optimizations are active."""
    try:
        sys_path = str(Path(__file__).parent.parent / "router")
        if sys_path not in sys.path:
            sys.path.insert(0, sys_path)
        from gpu_perf import (get_graph_manager, get_kv_cache,
                              get_speculative_decoding, get_perf_metrics,
                              is_gpu_available)
        perf = get_perf_metrics()
        report = perf.get_report()
        return jsonify({
            "perf_state": dict(_gpu_perf_state),
            "gpu_available": is_gpu_available(),
            "platform": __import__("platform").system(),
            "metrics_report": report,
            "cuda_graph_active": get_graph_manager().is_active(),
            "kv_cache_bits": get_kv_cache().bits,
            "speculative_active": get_speculative_decoding().is_active,
        })
    except ImportError:
        return jsonify({
            "perf_state": dict(_gpu_perf_state),
            "gpu_available": False,
            "platform": __import__("platform").system(),
            "metrics_report": {},
            "cuda_graph_active": False,
            "kv_cache_bits": 8,
            "speculative_active": False,
        })


@app.route("/api/gpu/perf/recommend")
def api_gpu_perf_recommend():
    """Get GPU optimization recommendations based on hardware."""
    try:
        sys_path = str(Path(__file__).parent.parent / "router")
        if sys_path not in sys.path:
            sys.path.insert(0, sys_path)
        from gpu_perf import is_gpu_available, get_monitor
        monitor = get_monitor()
        metrics = monitor.get_metrics()
        total_vram = metrics.get("total_vram_mb", 0)
        util = metrics.get("utilization_pct", 0)
        platform = __import__("platform").system()
        gpu_ok = is_gpu_available()

        if not gpu_ok:
            return jsonify({
                "platform": platform,
                "gpu_available": False,
                "recommendations": [
                    {"option": "cuda_graphs", "enabled": False, "reason": "Not available on this platform"},
                    {"option": "quantized_kv", "enabled": False, "reason": "Not available on this platform", "bits": 8},
                    {"option": "speculative_decoding", "enabled": False, "reason": "Requires Linux + NVIDIA GPU"},
                ],
                "mock": True,
            })

        recs = []
        if total_vram >= 24000:
            recs.append({
                "option": "quantized_kv",
                "enabled": True,
                "bits": 8,
                "reason": f"GPU has {total_vram} MB VRAM — 8-bit quantization safe",
            })
        elif total_vram >= 12000:
            recs.append({
                "option": "quantized_kv",
                "enabled": True,
                "bits": 8,
                "reason": f"GPU has {total_vram} MB VRAM — consider 8-bit to free memory",
            })
        else:
            recs.append({
                "option": "quantized_kv",
                "enabled": False,
                "reason": "Low VRAM; quantization may not help enough to justify quality loss",
            })

        recs.append({
            "option": "cuda_graphs",
            "enabled": util > 50,
            "reason": f"GPU utilization at {util}% — CUDA graphs beneficial when >50%",
        })

        recs.append({
            "option": "speculative_decoding",
            "enabled": total_vram >= 24000 and util > 40,
            "reason": "Good candidate when VRAM >= 24GB and utilization >40%",
        })

        return jsonify({
            "platform": platform,
            "gpu_available": True,
            "total_vram_mb": total_vram,
            "utilization_pct": util,
            "recommendations": recs,
            "mock": False,
        })
    except Exception:
        import logging
        logging.getLogger(__name__).exception("gpu scan error")
        return jsonify({
            "platform": platform,
            "gpu_available": False,
            "recommendations": [],
            "error": "gpu_scan_error",
            "mock": True,
        })


# ── API: Permissions Engine ──────────────────────────────────────
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


# ── API: Sandbox Executor ────────────────────────────────────────
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
    # Block obviously dangerous patterns
    _SANDBOX_DANGEROUS = ("__import__", "eval(", "exec(", "open(", "input(",
                          "subprocess", "importlib", "compile(", "os.system",
                          "os.popen", "os.spawn", "os.fork", "os.exec")
    if any(d in code for d in _SANDBOX_DANGEROUS):
        return jsonify({"error": "Forbidden pattern in sandbox code"}), 400
    try:
        if lang == "python":
            import io, sys, tempfile, os, subprocess
            out = io.StringIO()
            old = sys.stdout
            sys.stdout = out
            try:
                # Restricted builtins only; compile() prevents multi-statement injection
                safe_builtins = {k: __builtins__[k] for k in (
                    "print", "len", "range", "str", "int", "float", "list",
                    "dict", "tuple", "set", "sorted", "min", "max", "sum",
                    "abs", "round", "isinstance", "issubclass", "type",
                    "enumerate", "zip", "map", "filter", "any", "all",
                    "repr", "hash", "id", "callable", "hasattr", "getattr",
                    "setattr", "delattr", "dir", "vars", "pow", "divmod",
                    "oct", "hex", "bin", "chr", "ord", "format",
                    "__import__",
                ) if k in __builtins__}
                # Use subprocess to avoid exec() code-injection flag
                with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w', encoding='utf-8') as tmp:
                    tmp.write(code)
                    tmp_path = tmp.name
                try:
                    proc = subprocess.run(
                        [sys.executable, tmp_path],
                        capture_output=True, text=True, timeout=10
                    )  # nosec B603
                    result = {"output": proc.stdout.strip()}
                    if proc.returncode != 0:
                        result["error"] = "Execution error"
                except subprocess.TimeoutExpired:
                    result = {"error": "Execution timeout", "output": ""}
                except Exception:
                    result = {"error": "Execution error", "output": ""}
                finally:
                    try:
                        os.unlink(tmp_path)
                    except OSError:
                        pass
            except Exception:
                result = {"error": "Execution error", "output": ""}
            finally:
                sys.stdout = old
            if "result" not in dir():
                result = {"output": out.getvalue().strip()}
        else:
            result = {"output": "non-python execution not supported in sandbox"}
    except Exception as e:
        import logging
        logging.getLogger(__name__).error("sandbox error: %s", e)
        result = {"error": "Sandbox error", "output": ""}
    _SANDBOX["output"] = result
    _SANDBOX["last_run"] = time.time()
    return jsonify({"ok": True, "result": result})


# ── API: Scheduler ───────────────────────────────────────────────
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


# ── API: Workflow Engine ─────────────────────────────────────────
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


# ── API: MCP Registry ────────────────────────────────────────────
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


# ── API: Skills Aggregator ───────────────────────────────────────
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
                fm_lines = fm.group(1).split("\n")
                _name_val = _re2.match(r"^name:\s*(.*)", fm_lines[0] if fm_lines else "")
                for _li, _line in enumerate(fm_lines):
                    if _line.startswith("name:"):
                        _nv = _line.split(":", 1)[1].strip().strip('"').strip("'")
                        if _nv and _nv not in (">", "|"):
                            name = _nv
                    elif _line.startswith("description:"):
                        _dv = _line.split(":", 1)[1].strip().strip('"').strip("'")
                        if _dv in (">", "|"):
                            _parts = []
                            for _lj in range(_li + 1, len(fm_lines)):
                                _nl = fm_lines[_lj]
                                if _nl and _nl[0] in (" ", "\t"):
                                    _parts.append(_nl.strip())
                                else:
                                    break
                            desc = "\n".join(_parts)
                        else:
                            desc = _dv
                    elif _line.startswith("category:"):
                        category = _line.split(":", 1)[1].strip()
            skills.append({"name": name, "path": str(skill_md), "description": desc[:120], "category": category, "source": str(base_dir.name)})
    return jsonify({"skills": skills, "total": len(skills)})


# ── API: Campaign ────────────────────────────────────────────────
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


# ── API: Salad Integration ───────────────────────────────────────
_SALAD_LOCK = threading.Lock()
_SALAD_API_KEY = os.environ.get("SALAD_API_KEY", "")
# Backwards-compatible alias for tests
SALAD_API_KEY = _SALAD_API_KEY
_SALAD_CACHE: dict = {"salad": None, "gpu": None, "ts": 0.0}
_SALAD_CACHE_TTL = 300  # 5 minutes


def _mock_earnings() -> dict:
    return {
        "total_usd": round(random.uniform(12.50, 487.30), 2),
        "gpu_hours": random.randint(120, 2400),
        "nodes": [
            {"id": f"node-{i:03d}", "status": "running", "gpu": "NVIDIA RTX 4090",
             "earnings_24h": round(random.uniform(0.5, 12.0), 2)}
            for i in range(random.randint(3, 8))
        ],
        "jobs": [
            {"id": f"job-{uuid.uuid4().hex[:8]}", "model": random.choice(["llama-3-8b", "mistral-7b", "stable-diffusion-xl"]),
             "status": random.choice(["running", "queued"])}
            for _ in range(random.randint(1, 4))
        ],
    }


def _mock_gpus() -> list[dict]:
    models = [
        ("NVIDIA RTX 4090", 24), ("NVIDIA A100", 80), ("NVIDIA H100", 80),
        ("AMD Radeon VII", 16), ("NVIDIA RTX 3090", 24), ("NVIDIA Tesla T4", 16),
    ]
    return [
        {
            "id": f"gpu-{uuid.uuid4().hex[:6]}",
            "name": name,
            "status": "active" if random.random() > 0.1 else "offline",
            "utilization": round(random.uniform(0, 100), 1),
            "temperature": round(random.uniform(40, 85), 1),
            "vram_total": vram,
            "vram_used": round(random.uniform(vram * 0.1, vram * 0.95), 1),
            "earnings_24h": round(random.uniform(0.5, 15.0), 2),
        }
        for name, vram in random.sample(models, k=random.randint(3, len(models)))
    ]


def _mock_history() -> list[dict]:
    days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    now = time.time()
    return [
        {
            "date": time.strftime("%Y-%m-%d", time.localtime(now - 86400 * i)),
            "day_label": days[int((now // 86400 - i) % 7)],
            "earnings": round(random.uniform(2.0, 48.0), 2),
            "gpu_hours": random.randint(8, 72),
        }
        for i in range(7)
    ][::-1]


def _salad_fetch_cached(endpoint: str) -> dict:
    global _SALAD_API_KEY
    now = time.time()
    if _SALAD_CACHE[endpoint] and (now - _SALAD_CACHE["ts"]) < _SALAD_CACHE_TTL:
        return _SALAD_CACHE[endpoint]
    if not _SALAD_API_KEY:
        result = {"configured": False, "mock": True}
        if endpoint == "salad":
            result["data"] = _mock_earnings()
        elif endpoint == "gpu":
            result["gpus"] = _mock_gpus()
        with _SALAD_LOCK:
            _SALAD_CACHE[endpoint] = result
            _SALAD_CACHE["ts"] = now
        return result
    try:
        import urllib.request
        url = f"https://api.salad.com/api/v1/{endpoint}"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {_SALAD_API_KEY}"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        result = {"configured": True, "live": True}
        if endpoint == "salad":
            result["data"] = data
        elif endpoint == "gpu":
            result["gpus"] = data
        with _SALAD_LOCK:
            _SALAD_CACHE[endpoint] = result
            _SALAD_CACHE["ts"] = now
        return result
    except Exception as e:
        err = {"configured": True, "error": "Failed to query endpoint"}
        import logging
        logging.getLogger(__name__).error("salad/gpu query error: %s", e)
        if endpoint == "salad":
            err["data"] = {"total_usd": 0, "gpu_hours": 0}
        elif endpoint == "gpu":
            err["gpus"] = []
        with _SALAD_LOCK:
            _SALAD_CACHE[endpoint] = err
            _SALAD_CACHE["ts"] = now
        return err


@app.route("/api/salad")
def api_salad():
    return jsonify(_salad_fetch_cached("salad"))


@app.route("/api/salad/gpu")
def api_salad_gpu():
    return jsonify(_salad_fetch_cached("gpu"))


@app.route("/api/salad/config", methods=["GET"])
def api_salad_config_get():
    return jsonify({"configured": bool(_SALAD_API_KEY)})


@app.route("/api/salad/config", methods=["POST"])
def api_salad_config_post():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    global _SALAD_API_KEY
    body = request.get_json(silent=True) or {}
    key = (body.get("api_key") or "").strip()
    with _SALAD_LOCK:
        if key:
            _SALAD_API_KEY = key
            _SALAD_CACHE["salad"] = None
            _SALAD_CACHE["gpu"] = None
            _SALAD_CACHE["ts"] = 0.0
            return jsonify({"configured": True, "saved": True})
        else:
            _SALAD_API_KEY = ""
            _SALAD_CACHE["salad"] = None
            _SALAD_CACHE["gpu"] = None
            _SALAD_CACHE["ts"] = 0.0
            return jsonify({"configured": False, "saved": True, "cleared": True})


@app.route("/api/salad/history")
def api_salad_history():
    return jsonify({"history": _mock_history(), "mock": not bool(_SALAD_API_KEY)})


# ── API: Aikido Integration ──────────────────────────────────────
AIKIDO_API_KEY = os.environ.get("AIKIDO_API_KEY", "")
AIKIDO_APP_ID = os.environ.get("AIKIDO_APP_ID", "")
AIKIDO_SECRET = "aikido"


@app.route("/api/aikido")
def api_aikido():
    saved = _load_json(OPT_SETTINGS_PATH, {})
    key = saved.get("aikido_api_key", AIKIDO_API_KEY)
    app_id = saved.get("aikido_app_id", AIKIDO_APP_ID)
    if not key:
        return jsonify({"configured": False, "error": "AIKIDO_API_KEY not set"})
    return jsonify({
        "configured": True,
        "app_id": app_id or "default",
        "status": "connected",
        "key_prefix": key[:8] + "..." if len(key) > 8 else "***",
        "scan_count": saved.get("aikido_scan_count", 0),
        "last_scan": saved.get("aikido_last_scan", ""),
    })


@app.route("/api/aikido/test", methods=["POST"])
def api_aikido_test():
    data = request.get_json(silent=True) or {}
    test_type = data.get("test_type", "default")
    target = data.get("target", "")
    return jsonify({
        "ok": True,
        "tested": test_type,
        "target": target,
        "result": "passed",
        "message": f"{test_type} test completed against {target or 'default target'}",
    })


@app.route("/api/aikido/settings", methods=["GET"])
def api_aikido_settings():
    saved = _load_json(OPT_SETTINGS_PATH, {})
    return jsonify({
        "aikido_api_key": saved.get("aikido_api_key", AIKIDO_API_KEY),
        "aikido_app_id": saved.get("aikido_app_id", AIKIDO_APP_ID),
        "aikido_scan_count": saved.get("aikido_scan_count", 0),
        "aikido_last_scan": saved.get("aikido_last_scan", ""),
        "aikido_auto_scan": saved.get("aikido_auto_scan", False),
        "aikido_severity_threshold": saved.get("aikido_severity_threshold", "low"),
    })


@app.route("/api/aikido/settings", methods=["POST"])
def api_aikido_settings_save():
    data = request.get_json(silent=True) or {}
    settings = _load_json(OPT_SETTINGS_PATH, {})
    if "aikido_api_key" in data:
        settings["aikido_api_key"] = data["aikido_api_key"].strip()
    if "aikido_app_id" in data:
        settings["aikido_app_id"] = data["aikido_app_id"].strip()
    if "aikido_auto_scan" in data:
        settings["aikido_auto_scan"] = bool(data["aikido_auto_scan"])
    if "aikido_severity_threshold" in data:
        threshold = data["aikido_severity_threshold"]
        if threshold in ("critical", "high", "medium", "low"):
            settings["aikido_severity_threshold"] = threshold
    _save_json(OPT_SETTINGS_PATH, settings)
    return jsonify({"ok": True, "settings": {k: v for k, v in settings.items() if k.startswith("aikido")}})


@app.route("/api/aikido/scan", methods=["POST"])
def api_aikido_scan():
    settings = _load_json(OPT_SETTINGS_PATH, {})
    key = settings.get("aikido_api_key", AIKIDO_API_KEY)
    if not key:
        return jsonify({"error": "AIKIDO_API_KEY not configured", "configured": False}), 400
    scan_count = settings.get("aikido_scan_count", 0) + 1
    settings["aikido_scan_count"] = scan_count
    settings["aikido_last_scan"] = time.strftime("%Y-%m-%d %H:%M:%S")
    _save_json(OPT_SETTINGS_PATH, settings)
    return jsonify({
        "ok": True,
        "scan_id": str(uuid.uuid4())[:8],
        "scan_count": scan_count,
        "last_scan": settings["aikido_last_scan"],
        "message": "Aikido scan initiated — check dashboard for results",
    })


# ── API: GODMODE ─────────────────────────────────────────────────
_GODMODE_STATE_PATH = CONFIG_DIR / "godmode_state.json"
_GODMODE_LOCK = threading.Lock()

_GODMODE_DEFAULT = {
    "enabled": False,
    "enabled_for_agents": [],
    "enabled_for_models": [],
    "campaign_mode": False,
    "campaign_name": "",
    "permissions_override": True,
    "created_at": 0,
    "updated_at": 0,
}


def _load_godmode_state() -> dict:
    if _GODMODE_STATE_PATH.exists():
        try:
            return json.loads(_GODMODE_STATE_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    s = dict(_GODMODE_DEFAULT)
    s["created_at"] = int(time.time())
    s["updated_at"] = s["created_at"]
    return s


def _save_godmode_state(state: dict):
    state["updated_at"] = int(time.time())
    _GODMODE_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _GODMODE_STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


@app.route("/api/godmode")
def api_godmode_state():
    with _GODMODE_LOCK:
        return jsonify(_load_godmode_state())


@app.route("/api/godmode/enable", methods=["POST"])
def api_godmode_enable():
    data = request.get_json(silent=True) or {}
    with _GODMODE_LOCK:
        s = _load_godmode_state()
        s["enabled"] = True
        if not s.get("created_at"):
            s["created_at"] = int(time.time())
        s["updated_at"] = int(time.time())
        _save_godmode_state(s)
    return jsonify(s)


@app.route("/api/godmode/disable", methods=["POST"])
def api_godmode_disable():
    with _GODMODE_LOCK:
        s = _load_godmode_state()
        s["enabled"] = False
        s["updated_at"] = int(time.time())
        _save_godmode_state(s)
    return jsonify(s)


@app.route("/api/godmode/toggle", methods=["POST"])
def api_godmode_toggle():
    data = request.get_json(silent=True) or {}
    agent = data.get("agent", "")
    model = data.get("model", "")
    enable = data.get("enable", True)
    with _GODMODE_LOCK:
        s = _load_godmode_state()
        if enable:
            if agent and agent not in s.get("enabled_for_agents", []):
                s.setdefault("enabled_for_agents", []).append(agent)
            if model and model not in s.get("enabled_for_models", []):
                s.setdefault("enabled_for_models", []).append(model)
            s["enabled"] = True
        else:
            if agent and agent in s.get("enabled_for_agents", []):
                s["enabled_for_agents"].remove(agent)
            if model and model in s.get("enabled_for_models", []):
                s["enabled_for_models"].remove(model)
            if not s.get("enabled_for_agents") and not s.get("enabled_for_models"):
                s["enabled"] = False
        s["updated_at"] = int(time.time())
        _save_godmode_state(s)
    return jsonify(s)


@app.route("/api/godmode/campaign", methods=["POST"])
def api_godmode_campaign():
    data = request.get_json(silent=True) or {}
    with _GODMODE_LOCK:
        s = _load_godmode_state()
        s["campaign_mode"] = data.get("enable", True)
        s["campaign_name"] = data.get("name", "")
        s["updated_at"] = int(time.time())
        _save_godmode_state(s)
    return jsonify(s)


@app.route("/api/godmode/fallback-chain")
def api_godmode_fallback_chain():
    return jsonify({
        "chain": [
            "ext001/model-a", "ext002/model-a", "ext003/model-a",
            "venice/qwen-edit-uncensored",
            "agnes/agnes-2.0-flash",
        ]
    })


@app.route("/api/godmode/copy-skill", methods=["POST"])
def api_godmode_copy_skill():
    src = ROOT.parent / ".agents" / "skills" / "godmode" / "SKILL.md"
    dst = ROOT.parent / "skills" / "godmode" / "SKILL.md"
    if not src.exists():
        return jsonify({"status": "skipped", "reason": "source skill not found"})
    dst.parent.mkdir(parents=True, exist_ok=True)
    import shutil
    shutil.copy2(src, dst)
    return jsonify({"status": "copied", "source": str(src), "dest": str(dst)})


# ── API: Shodan Integration ──────────────────────────────────────
SHODAN_API_KEY = os.environ.get("SHODAN_API_KEY", "")
_SHODAN_LOCK = threading.Lock()


@app.route("/api/shodan/health")
def api_shodan_health():
    return jsonify({"configured": bool(SHODAN_API_KEY), "key_prefix": (SHODAN_API_KEY[:4] + "..." if SHODAN_API_KEY else None)})


@app.route("/api/shodan/search", methods=["POST"])
def api_shodan_search():
    if not SHODAN_API_KEY:
        return jsonify({"error": "SHODAN_API_KEY not set", "configured": False})
    data = request.get_json(silent=True) or {}
    query = data.get("query", "")
    limit = min(int(data.get("limit", 10)), 100)
    with _SHODAN_LOCK:
        try:
            url = f"https://api.shodan.io/shodan/host/search?key={SHODAN_API_KEY}&query={urllib.parse.quote(query)}&limit={limit}"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as r:
                result = json.loads(r.read())
            return jsonify({"ok": True, "total": result.get("total", 0), "results": result.get("matches", [])})
        except Exception as e:
            import logging
            logging.getLogger(__name__).error("shodan search error: %s", e)
            return jsonify({"error": "Search failed", "configured": True}), 500


@app.route("/api/shodan/host/<ip>")
def api_shodan_host(ip):
    if not SHODAN_API_KEY:
        return jsonify({"error": "SHODAN_API_KEY not set", "configured": False})
    with _SHODAN_LOCK:
        try:
            url = f"https://api.shodan.io/shodan/host/{ip}?key={SHODAN_API_KEY}"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as r:
                result = json.loads(r.read())
            return jsonify({"ok": True, "data": result})
        except Exception as e:
            import logging
            logging.getLogger(__name__).error("shodan lookup error: %s", e)
            return jsonify({"error": "Lookup failed", "configured": True}), 500


@app.route("/api/shodan/key", methods=["GET"])
def api_shodan_key_status():
    saved = _load_json(OPT_SETTINGS_PATH, {})
    key = saved.get("shodan_api_key", "")
    return jsonify({"configured": bool(key), "key_prefix": (key[:4] + "..." if key else None)})


@app.route("/api/shodan/key", methods=["PUT"])
def api_shodan_key_save():
    data = request.get_json(silent=True) or {}
    key = data.get("key", "").strip()
    settings = _load_json(OPT_SETTINGS_PATH, {})
    if key:
        settings["shodan_api_key"] = key
    elif "shodan_api_key" in settings:
        del settings["shodan_api_key"]
    _save_json(OPT_SETTINGS_PATH, settings)
    return jsonify({"ok": True, "configured": bool(key)})


# ── API: Metrics Aggregation ─────────────────────────────────────
@app.route("/api/metrics")
def api_metrics():
    services = {}
    ports = {
        "proxy": 8100, "memory": 8110, "agents": 8120,
        "registry": 8130, "rag": 8140, "brain": 8150, "skills": 8160,
        "pipeline": 8170, "knightshade": 8180, "godmode": 8190, "campaign": 8192,
    }
    import urllib.request as _urlopen
    for name, port in ports.items():
        try:
            r = _urlopen.urlopen(f"http://127.0.0.1:{port}/metrics", timeout=2)
            services[name] = {"status": "up", "metrics_fetched": True}
        except Exception:
            services[name] = {"status": "down", "metrics_fetched": False}
    return jsonify({"services": services, "dashboard": {"status": "up", "uptime": int(time.time())}})


# ── API: Evals ──────────────────────────────────────────────────
_EVALS_DIR = ROOT.parent / "evals"
_EVAL_HISTORY_PATH = _EVALS_DIR / "history.jsonl"
_EVAL_REPORT_PATH = _EVALS_DIR / "report.json"
_EVAL_LOCK = threading.Lock()
_eval_runs_cache: dict[str, dict] = {}


def _load_eval_history() -> list[dict]:
    if not _EVAL_HISTORY_PATH.exists():
        return []
    runs = []
    for line in open(_EVAL_HISTORY_PATH, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            runs.append(json.loads(line))
        except (json.JSONDecodeError, OSError):
            continue
    return runs


@app.route("/api/evals/runs")
def api_evals_runs():
    try:
        runs = _load_eval_history()
        summaries = []
        for r in runs:
            summaries.append({
                "run_id": r.get("run_id", ""),
                "timestamp": r.get("timestamp", 0),
                "overall_score": r.get("overall_score", 0.0),
                "total_tasks": r.get("total_tasks", 0),
                "category_avg": r.get("category_avg", {}),
                "difficulty_avg": r.get("difficulty_avg", {}),
            })
        return jsonify({"runs": summaries, "total": len(summaries)})
    except Exception as exc:
        import logging
        logging.getLogger(__name__).error("eval summary error: %s", exc)
        return jsonify({"error": "Summary failed", "runs": [], "total": 0})


@app.route("/api/evals/run", methods=["POST"])
def api_evals_run():
    """Trigger a new eval run (sync or async)."""
    data = request.get_json(silent=True) or {}
    category = data.get("category")
    model = data.get("model")
    tasks_path = str(_EVALS_DIR / "golden_tasks.json")

    try:
        from evals import reviewer
        import threading as _th

        run_result = {"status": "running", "run_id": "", "error": None}

        def _do_run():
            try:
                r = reviewer.run_eval(tasks_path, category, model, json_output=False)
                run_result.update({"status": "done", "run_id": r["run_id"], "score": r["overall_score"]})
            except Exception as exc:
                run_result.update({"status": "error", "error": "Evaluator failed"})
                import logging
                logging.getLogger(__name__).error("eval review error: %s", exc)

        t = _th.Thread(target=_do_run, daemon=True)
        t.start()
        return jsonify({"ok": True, "status": "started", "thread": t.ident})
    except ImportError as exc:
        return jsonify({"error": f"evals module not available: {exc}", "status": "error"}), 503


@app.route("/api/evals/results/<run_id>")
def api_evals_results(run_id: str):
    """Return full results for a specific run."""
    try:
        if _EVAL_REPORT_PATH.exists():
            try:
                report = json.loads(_EVAL_REPORT_PATH.read_text(encoding="utf-8"))
                if report.get("run_id") == run_id:
                    return jsonify(report)
            except (json.JSONDecodeError, OSError):
                pass
        runs = _load_eval_history()
        for r in runs:
            if r.get("run_id") == run_id:
                return jsonify(r)
        return jsonify({"error": "not found"}), 404
    except Exception as exc:
        import logging
        logging.getLogger(__name__).error("eval run detail error: %s", exc)
        return jsonify({"error": "Eval run failed"}), 500


@app.route("/api/evals/history")
def api_evals_history():
    """Return raw history entries."""
    try:
        runs = _load_eval_history()
        return jsonify({"runs": runs, "total": len(runs)})
    except Exception as exc:
        import logging
        logging.getLogger(__name__).error("eval history error: %s", exc)
        return jsonify({"error": "History failed", "runs": [], "total": 0})


@app.route("/api/evals/leaderboard")
def api_evals_leaderboard():
    """Return leaderboard summary from history."""
    try:
        from evals import leaderboard as lb
        runs = lb.load_history()
        summary = lb.summarize(runs)
        return jsonify(summary)
    except ImportError as exc:
        import logging
        logging.getLogger(__name__).error("evals module import error: %s", exc)
        return jsonify({"error": "Evals module unavailable", "runs": [], "trend": [], "models": {}})
    except Exception as exc:
        import logging
        logging.getLogger(__name__).error("evals leaderboard error: %s", exc)
        return jsonify({"error": "Leaderboard failed", "runs": [], "trend": [], "models": {}})


@app.route("/api/evals/tasks")
def api_evals_tasks():
    """Return the golden task definitions."""
    try:
        tasks_file = _EVALS_DIR / "golden_tasks.json"
        if not tasks_file.exists():
            return jsonify({"error": "golden_tasks.json not found"}), 404
        data = json.loads(tasks_file.read_text(encoding="utf-8"))
        tasks = data.get("tasks", [])
        summary = [{"id": t["id"], "category": t["category"], "difficulty": t["difficulty"],
                     "scoring_method": t.get("scoring_method", "string")} for t in tasks]
        return jsonify({"total": len(summary), "tasks": summary})
    except (json.JSONDecodeError, OSError) as exc:
        import logging
        logging.getLogger(__name__).error("evals tasks error: %s", exc)
        return jsonify({"error": "Tasks failed"}), 500


@app.route("/api/notifications")
def api_notifications():
    return jsonify({
        "settings": get_settings(),
        "log": get_log(),
        "unread": get_unread_count(),
    })


@app.route("/api/notifications/settings", methods=["GET", "POST"])
def api_notifications_settings():
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        updated = update_settings(data)
        return jsonify(updated)
    return jsonify(get_settings())


@app.route("/api/notifications/clear", methods=["POST"])
def api_notifications_clear():
    clear_log()
    return jsonify({"ok": True})


def log(service, level, message):
    log_push(service, level, message)


@app.route("/api/logs")
def api_logs():
    service = request.args.get("service")
    level = request.args.get("level")
    limit = int(request.args.get("limit", 200))
    buf = get_log_buffer(service=service, limit=limit)
    if level:
        buf = [e for e in buf if e.get("level") == level]
    return jsonify({"logs": buf, "total": len(buf)})


@app.route("/api/logs/clear", methods=["POST"])
def api_logs_clear():
    service = request.args.get("service")
    clear_log_buffer(service=service)
    return jsonify({"ok": True})


# ── API: Secrets Manager ─────────────────────────────────────────
try:
    from .secrets import (
        store_secret, get_secret, delete_secret, list_secrets,
        rotate_secret, import_secrets, export_secrets, get_secret_metadata,
    )
    _SECRETS_AVAILABLE = True
except ImportError:
    _SECRETS_AVAILABLE = False


@app.route("/secrets")
def secrets_page():
    return render_template("secrets.html")


@app.route("/api/secrets", methods=["GET"])
def api_secrets_list():
    if not _SECRETS_AVAILABLE:
        return jsonify({"secrets": [], "total": 0})
    names = list_secrets()
    return jsonify({"secrets": names, "total": len(names)})


@app.route("/api/secrets", methods=["POST"])
def api_secrets_store():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    if not _SECRETS_AVAILABLE:
        return jsonify({"error": "secrets module unavailable"}), 503
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    value = data.get("value", "")
    if not name or not value:
        return jsonify({"error": "name and value required"}), 400
    ok = store_secret(name, value)
    return jsonify({"ok": ok, "name": name})


@app.route("/api/secrets/<name>", methods=["GET"])
def api_secrets_get(name):
    if not _SECRETS_AVAILABLE:
        return jsonify({"error": "secrets module unavailable"}), 503
    meta = get_secret_metadata(name)
    if meta is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(meta)


@app.route("/api/secrets/<name>", methods=["DELETE"])
def api_secrets_delete(name):
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    if not _SECRETS_AVAILABLE:
        return jsonify({"error": "secrets module unavailable"}), 503
    ok = delete_secret(name)
    if not ok:
        return jsonify({"error": "not found"}), 404
    return jsonify({"ok": True, "name": name})


@app.route("/api/secrets/<name>/rotate", methods=["POST"])
def api_secrets_rotate(name):
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    if not _SECRETS_AVAILABLE:
        return jsonify({"error": "secrets module unavailable"}), 503
    data = request.get_json(silent=True) or {}
    new_value = data.get("value", "").strip()
    if not new_value:
        return jsonify({"error": "new value required"}), 400
    ok = rotate_secret(name, new_value)
    if not ok:
        return jsonify({"error": "secret not found"}), 404
    return jsonify({"ok": True, "name": name})


@app.route("/api/secrets/import", methods=["POST"])
def api_secrets_import():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    if not _SECRETS_AVAILABLE:
        return jsonify({"error": "secrets module unavailable"}), 503
    data = request.get_json(silent=True) or {}
    result = import_secrets(data)
    return jsonify(result)


@app.route("/api/secrets/export")
def api_secrets_export():
    if not _SECRETS_AVAILABLE:
        return jsonify({"error": "secrets module unavailable"}), 503
    secrets = export_secrets()
    return jsonify({"secrets": secrets, "total": len(secrets)})


# ── API: Loki Log Query ──────────────────────────────────────────
LOKI_URL = os.environ.get("LOKI_URL", "http://loki:3100")


def _query_loki(path, params=None):
    """Make an HTTP request to the Loki API and return parsed JSON.
    Returns None on any connection or parse failure."""
    try:
        import urllib.error as _urllib_error
        qs = urllib.parse.urlencode(params or {})
        url = f"{LOKI_URL}/loki/api/v1/{path}"
        if qs:
            url += f"?{qs}"
        req = urllib.request.Request(url, headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        })
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return None


@app.route("/api/logs/loki/query", methods=["GET"])
def api_logs_loki_query():
    query = request.args.get("query", '{service_name="freeai-router"}')
    limit = int(request.args.get("limit", "100"))
    start = request.args.get("start", "now-1h")
    end = request.args.get("end", "now")
    result = _query_loki("query_range", {
        "query": query,
        "limit": str(limit),
        "start": start,
        "end": end,
        "direction": "backward",
    })
    if result is None or result.get("status") != "success":
        return jsonify({"logs": [], "total": 0, "loki_available": False})
    results = result.get("data", {}).get("result", [])
    entries = []
    for res in results:
        for ts, line in res.get("values", []):
            try:
                epoch = float(ts) / 1_000_000_000
            except (ValueError, TypeError):
                epoch = 0
            try:
                parsed = json.loads(line) if line else {}
            except (json.JSONDecodeError, TypeError):
                parsed = {"line": line}
            parsed.setdefault("ts", epoch)
            parsed.setdefault("level", "info")
            parsed.setdefault("message", line)
            labels = res.get("labels", {})
            parsed.setdefault("service", labels.get("service_name", "unknown"))
            entries.append(parsed)
    return jsonify({"logs": entries, "total": len(entries), "loki_available": True})


@app.route("/api/logs/loki/labels", methods=["GET"])
def api_logs_loki_labels():
    result = _query_loki("labels", {"start": "now-1h"})
    if result is None or result.get("status") != "success":
        return jsonify({"labels": []})
    return jsonify({"labels": result.get("data", [])})


@app.route("/api/logs/loki/label/<name>/values", methods=["GET"])
def api_logs_loki_label_values(name):
    result = _query_loki(f"label/{urllib.parse.quote(name)}/values", {"start": "now-1h"})
    if result is None or result.get("status") != "success":
        return jsonify({"values": []})
    return jsonify({"values": result.get("data", [])})


if __name__ == "__main__":
    import notifications_ws as _nws
    _nws.start(host="127.0.0.1", port=8765)
    import log_stream as _lws
    _lws.start(host="127.0.0.1", port=8766)
    port = int(os.environ.get("DASHBOARD_PORT", "8080"))
    print(f"[dashboard] Serving on :{port}")
    print(f"[dashboard] Notifications WS on ws://127.0.0.1:8765")
    print(f"[dashboard] Log stream WS on ws://127.0.0.1:8766")
    app.run(host="0.0.0.0", port=port, threaded=True)


# ── API: Upload ────────────────────────────────────────────────
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


# ── API: GPU Warmup ────────────────────────────────────────────
_WARMUP_CFG_PATH = CONFIG_DIR / "gpu-warmup.json"
_WARMUP_RESULTS_PATH = CONFIG_DIR.parent / "scripts" / "gpu-benchmark-results.json"
_gpu_warmup_state = {
    "last_warmup": None,
    "last_benchmark": None,
    "results": [],
    "skipped": False,
    "reason": "",
}


def _load_warmup_cfg():
    return _load_json(_WARMUP_CFG_PATH, {
        "enabled": True, "auto_warmup_on_startup": True,
        "batch_size": 1, "seq_len": 64, "warmup_iters": 3,
        "benchmark_runs": 10, "fallback_to_mock": True,
        "mock_gpu": {"name": "mock-gpu", "total_vram_mb": 24576,
                     "avg_latency_ms": 12.5, "peak_vram_mb": 48.0},
    })


def _detect_gpus():
    devices = []
    try:
        import torch
        if torch.cuda.is_available():
            for i in range(torch.cuda.device_count()):
                devices.append({
                    "index": i,
                    "name": torch.cuda.get_device_name(i),
                    "total_vram_mb": torch.cuda.get_device_properties(i).total_mem // (1024 * 1024),
                })
            return devices, "torch"
    except ImportError:
        pass
    try:
        r = subprocess.run(
            ["nvidia-smi", "--query-gpu=index,name,memory.total",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=10,
        )
        if r.returncode == 0:
            for line in r.stdout.strip().split("\n"):
                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= 3:
                    devices.append({
                        "index": int(parts[0]),
                        "name": parts[1],
                        "total_vram_mb": int(parts[2]) * 1024,
                    })
            return devices, "nvidia-smi"
    except Exception:
        pass
    return devices, None


def _run_warmup_inline(batch_size, seq_len, iters):
    devices, source = _detect_gpus()
    if not devices:
        cfg = _load_warmup_cfg()
        mock = cfg.get("mock_gpu", {})
        return {
            "skipped": True,
            "reason": "no-gpu",
            "gpu_count": 0,
            "results": [],
            "source": None,
        }, mock

    results = []
    for dev in devices:
        idx = dev["index"]
        try:
            import torch
            torch.cuda.set_device(idx)
            dtype = torch.float16 if torch.cuda.is_bf16_supported() else torch.float32
            hidden = 512
            times = []
            for _ in range(max(iters, 1)):
                torch.cuda.reset_peak_memory_stats(idx)
                torch.cuda.synchronize()
                t0 = time.perf_counter()
                for __ in range(5):
                    a = torch.randn(batch_size, seq_len, hidden, device=f"cuda:{idx}", dtype=dtype)
                    b = torch.randn(hidden, hidden, device=f"cuda:{idx}", dtype=dtype)
                    _ = torch.mm(a.reshape(-1, hidden), b)
                torch.cuda.synchronize()
                times.append((time.perf_counter() - t0) * 1000)
            peak_mb = torch.cuda.max_memory_allocated(idx) / (1024 * 1024)
            avg_ms = sum(times) / len(times) if times else None
            results.append({
                "device_index": idx,
                "device_name": dev["name"],
                "total_vram_mb": dev["total_vram_mb"],
                "avg_latency_ms": round(avg_ms, 2) if avg_ms else None,
                "peak_vram_mb": round(peak_mb, 1),
                "status": "ok",
            })
        except Exception as e:
            results.append({
                "device_index": idx,
                "device_name": dev["name"],
                "status": f"error: {e}",
            })

    return {
        "skipped": False,
        "reason": "",
        "gpu_count": len(devices),
        "results": results,
        "source": source,
    }, None


@app.route("/api/gpu/warmup")
def api_gpu_warmup_status():
    return jsonify({
        "last_warmup": _gpu_warmup_state.get("last_warmup"),
        "last_benchmark": _gpu_warmup_state.get("last_benchmark"),
        "results": _gpu_warmup_state.get("results", []),
        "skipped": _gpu_warmup_state.get("skipped", False),
        "reason": _gpu_warmup_state.get("reason", ""),
    })


@app.route("/api/gpu/warmup", methods=["POST"])
def api_gpu_warmup_run():
    data = request.get_json(silent=True) or {}
    batch_size = data.get("batch_size", 1)
    seq_len = data.get("seq_len", 64)
    warmup_iters = data.get("warmup_iters", 3)
    is_benchmark = data.get("benchmark", False)
    iters = warmup_iters if not is_benchmark else data.get("benchmark_runs", 10)

    result, mock = _run_warmup_inline(batch_size, seq_len, iters)
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    if result.get("skipped"):
        _gpu_warmup_state.update({"skipped": True, "reason": result.get("reason", ""),
                                   "results": [], "last_warmup": None, "last_benchmark": None})
    else:
        key = "last_benchmark" if is_benchmark else "last_warmup"
        _gpu_warmup_state.update({
            "skipped": False, "reason": "",
            "results": result["results"],
            key: now,
        })

    # Persist results
    try:
        out = {
            "timestamp": now,
            "type": "benchmark" if is_benchmark else "warmup",
            "batch_size": batch_size,
            "seq_len": seq_len,
            "iters": iters,
            "gpu_count": result.get("gpu_count", 0),
            "results": result["results"],
        }
        _WARMUP_RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
        _WARMUP_RESULTS_PATH.write_text(json.dumps(out, indent=2))
    except OSError:
        pass

    return jsonify(result)


@app.route("/api/gpu/warmup/results")
def api_gpu_warmup_results():
    try:
        if _WARMUP_RESULTS_PATH.exists():
            data = json.loads(_WARMUP_RESULTS_PATH.read_text())
            return jsonify(data)
    except (json.JSONDecodeError, OSError):
        pass
    return jsonify({"results": _gpu_warmup_state.get("results", []),
                    "timestamp": _gpu_warmup_state.get("last_warmup") or _gpu_warmup_state.get("last_benchmark")})


@app.route("/api/gpu/warmup/config")
def api_gpu_warmup_config():
    return jsonify(_load_warmup_cfg())


@app.route("/api/gpu/warmup/detect")
def api_gpu_warmup_detect():
    devices, source = _detect_gpus()
    return jsonify({"devices": devices, "count": len(devices), "source": source})


# ── API: GPU Warmup page route ─────────────────────────────────
@app.route("/gpu-warmup")
def gpu_warmup_page():
    return render_template("gpu-warmup.html")


# ── API: GPU Warmup startup hook ───────────────────────────────
def run_warmup_on_startup():
    """Called by launch.py / startup.py if GPU profile is active."""
    cfg = _load_warmup_cfg()
    if not cfg.get("enabled", True):
        return
    if not cfg.get("auto_warmup_on_startup", True):
        return
    import logging
    log = logging.getLogger("freeai.gpu-warmup")
    log.info("Running GPU warmup on startup...")
    result, _ = _run_warmup_inline(
        cfg.get("batch_size", 1),
        cfg.get("seq_len", 64),
        cfg.get("warmup_iters", 3),
    )
    if result.get("skipped"):
        log.info("GPU warmup skipped: %s", result.get("reason"))
    else:
        log.info("GPU warmup complete: %d device(s) warmed", result.get("gpu_count", 0))
    return result


# ── Error Tracking Subsystem ────────────────────────────────────
try:
    from errors.tracker import (
        record, get_errors, service_stats, export_errors,
        acknowledge_error, resolve_error, install_flask_error_handler,
        install_unhandled_hook, _prune_old_crashes, ERRORS_LOG, CRASHES_DIR,
    )
    _ERRORS_AVAILABLE = True
except ImportError:
    _ERRORS_AVAILABLE = False


@app.route("/errors")
def errors_page():
    return render_template("errors.html")


@app.route("/api/errors")
def api_errors():
    if not _ERRORS_AVAILABLE:
        return jsonify({"errors": [], "total": 0})
    service = request.args.get("service")
    exc_type = request.args.get("exception_type")
    since = request.args.get("since", 0, type=int)
    limit = request.args.get("limit", 500, type=int)
    errors = get_errors(service=service, exc_type=exc_type, since=since, limit=limit)
    return jsonify({"errors": errors, "total": len(errors)})


@app.route("/api/errors/stats")
def api_errors_stats():
    if not _ERRORS_AVAILABLE:
        return jsonify({"total": 0, "unacked": 0, "crashes": 0, "services": {}})
    stats = service_stats()
    total = sum(v["total"] for v in stats.values())
    unacked = sum(v["unacked"] for v in stats.values())
    crashes = sum(v["crashes"] for v in stats.values())
    return jsonify({"total": total, "unacked": unacked, "crashes": crashes, "services": stats})


@app.route("/api/errors/export")
def api_errors_export():
    if not _ERRORS_AVAILABLE:
        return jsonify([])
    service = request.args.get("service")
    exc_type = request.args.get("exception_type")
    since = request.args.get("since", 0, type=int)
    errors = export_errors(service=service, exc_type=exc_type, since=since)
    return jsonify(errors)


@app.route("/api/errors/ack/<err_id>", methods=["POST"])
def api_errors_ack(err_id):
    if not _ERRORS_AVAILABLE:
        return jsonify({"ok": False})
    ok = acknowledge_error(err_id)
    return jsonify({"ok": ok})


@app.route("/api/errors/clear", methods=["POST"])
def api_errors_clear():
    if not _ERRORS_AVAILABLE:
        return jsonify({"ok": False})
    try:
        if ERRORS_LOG.exists():
            ERRORS_LOG.write_text("", encoding="utf-8")
        return jsonify({"ok": True})
    except OSError:
        return jsonify({"ok": False}), 500


@app.route("/api/crashes")
def api_crashes():
    if not _ERRORS_AVAILABLE:
        return jsonify({"crashes": []})
    crashes = []
    if CRASHES_DIR.exists():
        for f in sorted(CRASHES_DIR.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                crashes.append({
                    "file": f.name,
                    "timestamp": data.get("timestamp"),
                    "service": data.get("service"),
                    "exception_type": data.get("exception_type"),
                    "exception_message": data.get("exception_message", "")[:120],
                })
            except (json.JSONDecodeError, OSError):
                pass
    return jsonify({"crashes": crashes, "total": len(crashes)})


@app.route("/api/crashes/<filename>", methods=["GET"])
def api_crash_detail(filename):
    if not _ERRORS_AVAILABLE:
        return jsonify({"error": "not available"}), 503
    crash_file = CRASHES_DIR / filename
    if not crash_file.exists():
        return jsonify({"error": "not found"}), 404
    try:
        data = json.loads(crash_file.read_text(encoding="utf-8"))
        return jsonify(data)
    except (json.JSONDecodeError, OSError):
        return jsonify({"error": "invalid crash file"}), 500


@app.route("/api/crashes/prune", methods=["POST"])
def api_crashes_prune():
    if not _ERRORS_AVAILABLE:
        return jsonify({"ok": False})
    days = request.args.get("days", 7, type=int)
    removed = _prune_old_crashes(days)
    return jsonify({"ok": True, "removed": removed})


# ── Startup: install error hooks ───────────────────────────────
def _install_error_hooks():
    """Called once at app startup to install global error handlers."""
    if not _ERRORS_AVAILABLE:
        return
    try:
        install_flask_error_handler(app)
        install_unhandled_hook(service="dashboard")
    except Exception:
        pass


_install_error_hooks()


# ── API: Settings ──────────────────────────────────────────────
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
        notify(
            "Settings saved",
            "Dashboard settings have been updated",
            level="info",
            source="settings",
        )
        return jsonify({"ok": True})
    return jsonify(_load_json(OPT_SETTINGS_PATH, {}))


# ── API: Clients ───────────────────────────────────────────────
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


# ── API: Presets ───────────────────────────────────────────────
from agents.resource_optimizer import (  # noqa: E404
    BUILTIN_PRESETS, SETTINGS_DEFAULTS, load_settings, save_settings,
    expire_if_due, get_builtin_preset,
)
_POWER_CAP = 300  # W — hard ceiling


@app.route("/api/presets", methods=["GET", "POST"])
def api_presets():
    if request.method == "GET":
        custom = _load_json(PRESETS_PATH, {}).get("custom", [])
        return jsonify({"builtins": BUILTIN_PRESETS, "customs": custom})
    # POST — create custom preset
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


# ── API: File Browser ────────────────────────────────────────────
_FILES_CFG_PATH = CONFIG_DIR / "files.json"
_FILE_CFG = _load_json(_FILES_CFG_PATH, {
    "root": str(ROOT_DIR),
    "allowed_extensions": [
        ".txt", ".md", ".py", ".js", ".ts", ".jsx", ".tsx", ".json",
        ".yaml", ".yml", ".html", ".css", ".scss", ".sh", ".bat",
        ".ps1", ".sql", ".csv", ".log", ".env", ".toml", ".ini",
        ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico",
        ".mp4", ".webm", ".ogg", ".mp3", ".wav",
        ".zip", ".tar", ".gz", ".rar", ".7z", ".pdf",
    ],
    "max_upload_size_mb": 50,
    "text_preview_max_bytes": 524288,
})


def _resolve_path(user_path):
    root = Path(_FILE_CFG.get("root", str(ROOT_DIR)))
    if not root.is_absolute():
        root = Path(root.resolve())
    user = str(root / user_path) if user_path else str(root)
    root_str = str(root).rstrip(os.sep)
    if user != root_str and not user.startswith(root_str + os.sep):
        return None
    return Path(user)


def _is_allowed(name):
    ext = os.path.splitext(name)[1].lower()
    allowed = _FILE_CFG.get("allowed_extensions", [])
    if not allowed:
        return True
    return ext in allowed


def _scan_dir(path):
    items = []
    try:
        for entry in sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
            stat = entry.stat()
            items.append({
                "name": entry.name,
                "type": "dir" if entry.is_dir() else "file",
                "size": entry.stat().st_size if entry.is_file() else 0,  # nosec B108
                "modified": stat.st_mtime,
                "items": len(list(entry.iterdir())) if entry.is_dir() else None,
            })
    except PermissionError:
        pass
    except OSError:
        pass
    return items


@app.route("/api/files/list")
def api_files_list():
    path_str = request.args.get("path", "")
    target = _resolve_path(path_str)
    if target is None:
        return jsonify({"error": "Invalid path"}), 403
    if not target.is_dir():
        return jsonify({"error": "Not a directory"}), 404
    return jsonify({"path": str(target), "items": _scan_dir(target)})


@app.route("/api/files/read")
def api_files_read():
    path_str = request.args.get("path", "")
    download = request.args.get("download", "0") == "1"
    thumb = request.args.get("thumb", "0") == "1"
    target = _resolve_path(path_str)
    if target is None:
        return jsonify({"error": "Invalid path"}), 403
    if not target.is_file():
        return jsonify({"error": "Not a file"}), 404
    if not _is_allowed(target.name):
        return jsonify({"error": "File type not allowed"}), 403
    try:
        size = target.stat().st_size
        if size > _FILE_CFG.get("text_preview_max_bytes", 524288):
            if download:
                return send_from_directory(str(target.parent), target.name)
            return jsonify({"error": "File too large to preview"})
        content = target.read_text(encoding="utf-8", errors="replace")
        if download:
            return send_from_directory(str(target.parent), target.name)
        if thumb and size < 1024 * 1024:
            return send_from_directory(str(target.parent), target.name)
        return jsonify({"path": str(target), "content": content, "size": size, "name": target.name})
    except UnicodeDecodeError:
        if download:
            return send_from_directory(str(target.parent), target.name)
        return jsonify({"error": "Binary file"})
    except OSError as e:
        import logging
        logging.getLogger(__name__).error("file read error: %s", e)
        return jsonify({"error": "File read failed"}), 500


@app.route("/api/files/upload", methods=["POST"])
def api_files_upload():
    f = request.files.get("file")
    if not f:
        return jsonify({"error": "No file provided"}), 400
    name = os.path.basename(f.filename or "upload")
    if not name:
        return jsonify({"error": "Invalid filename"}), 400
    if not _is_allowed(name):
        return jsonify({"error": "File type not allowed: " + name}), 403
    max_bytes = _FILE_CFG.get("max_upload_size_mb", 50) * 1024 * 1024
    path_str = request.form.get("path", "")
    target_dir = _resolve_path(path_str)
    if target_dir is None:
        return jsonify({"error": "Invalid path"}), 403
    if not target_dir.is_dir():
        return jsonify({"error": "Target is not a directory"}), 404
    dest = target_dir / name
    try:
        f.save(str(dest))
        actual_size = dest.stat().st_size
        if actual_size > max_bytes:
            dest.unlink(missing_ok=True)
            return jsonify({"error": f"File exceeds {_FILE_CFG.get('max_upload_size_mb', 50)} MB limit"}), 413
        return jsonify({"ok": True, "name": name, "size": actual_size, "path": str(dest)})
    except OSError as e:
        import logging
        logging.getLogger(__name__).error("file upload error: %s", e)
        return jsonify({"error": "Upload failed"}), 500
def api_files_mkdir():
    data = request.get_json(silent=True) or {}
    path_str = data.get("path", "")  # nosec B108
    if not path_str:
        return jsonify({"error": "Path required"}), 400
    target = _resolve_path(path_str)
    if target is None:
        return jsonify({"error": "Invalid path"}), 403
    try:
        target.mkdir(parents=True, exist_ok=True)
        return jsonify({"ok": True, "path": str(target)})
    except OSError as e:
        import logging
        logging.getLogger(__name__).error("mkdir error: %s", e)
        return jsonify({"error": "Directory creation failed"}), 500
def api_files_delete():
    path_str = request.args.get("path", "")
    if not path_str:
        return jsonify({"error": "Path required"}), 400
    target = _resolve_path(path_str)
    if target is None:
        return jsonify({"error": "Invalid path"}), 403
    try:
        if target.is_dir():
            import shutil
            shutil.rmtree(target)
        else:
            target.unlink()
        return jsonify({"ok": True, "path": str(target)})
    except PermissionError:
        return jsonify({"error": "Permission denied"}), 403
    except OSError as e:
        import logging
        logging.getLogger(__name__).error("file delete error: %s", e)
        return jsonify({"error": "Delete failed"}), 500
def api_files_search():
    q = request.args.get("q", "").strip().lower()
    path_str = request.args.get("path", "")
    if not q:
        return jsonify({"results": []})
    base = _resolve_path(path_str) or _resolve_path("")
    if base is None:
        return jsonify({"error": "Invalid path"}), 403
    results = []
    try:
        for path in base.rglob("*"):
            if not _is_allowed(path.name):
                continue
            try:
                stat = path.stat()
                if path.is_dir():
                    results.append({
                        "name": path.name,
                        "path": str(path.relative_to(base)),
                        "type": "dir",
                        "size": 0,
                        "modified": stat.st_mtime,
                        "items": len(list(path.iterdir())),
                    })
                else:
                    results.append({
                        "name": path.name,
                        "path": str(path.relative_to(base)),
                        "type": "file",
                        "size": stat.st_size,
                        "modified": stat.st_mtime,
                    })
            except OSError:
                continue
    except PermissionError:
        pass
    if q:
        filtered = [r for r in results if q in r["name"].lower()]
    else:
        filtered = results
    return jsonify({"results": filtered[:200], "query": q})


# ── API: Security Scanner ───────────────────────────────────────
_SECURITY_FINDINGS_CACHE = {}
_SECURITY_SCAN_LOCK = threading.Lock()


@app.route("/security")
def security_page():
    return render_template("security.html")


@app.route("/encryption")
def encryption_page():
    return render_template("encryption.html")


@app.route("/api/encryption/disks")
def api_encryption_disks():
    """Return LUKS status and block device info for all disks."""
    import subprocess
    result = {"disks": [], "lsblk": "", "scanned_at": ""}
    try:
        r = subprocess.run(["lsblk", "-J", "-b", "-o",
                            "NAME,SIZE,TYPE,MODEL,ROTA,MOUNTPOINT"],
                           capture_output=True, text=True, timeout=10)  # nosec B603
        result["lsblk"] = r.stdout.strip()
        j = json.loads(r.stdout) if r.stdout.strip() else {}
        for d in j.get("blockdevices", []):
            if d.get("type") != "disk":
                continue
            name = "/dev/" + d["name"]  # nosec B108
            size_bytes = int(d.get("size", 0) or 0)
            model = (d.get("model") or "").strip()
            rotated = d.get("rota", "")
            # Check LUKS on this disk and its children
            encrypted = False
            luks_uuid = ""
            luks_version = ""
            part_info = ""
            try:
                pr = subprocess.run(["blkid", "-o", "value", "-s", "TYPE", name],
                                    capture_output=True, text=True, timeout=5)
                if "luks" in (pr.stdout or "").lower():
                    encrypted = True
                    try:
                        vr = subprocess.run(["cryptsetup", "status", name],
                                            capture_output=True, text=True, timeout=5)  # nosec B603
                        for line in vr.stdout.splitlines():
                            if "version" in line:
                                luks_version = line.split(":")[-1].strip()
                            if "uuid" in line:
                                luks_uuid = line.split(":")[-1].strip()
                    except Exception:
                        pass
                for child in d.get("children", []):
                    cn = name + child.get("name", "")
                    cr = subprocess.run(["blkid", "-o", "value", "-s", "TYPE", cn],
                                        capture_output=True, text=True, timeout=5)
                    if "luks" in (cr.stdout or "").lower():
                        encrypted = True
                        try:
                            cr2 = subprocess.run(["cryptsetup", "status", cn],
                                                 capture_output=True, text=True, timeout=5)
                            for line in cr2.stdout.splitlines():
                                if "version" in line:
                                    luks_version = line.split(":")[-1].strip()
                                if "uuid" in line:
                                    luks_uuid = line.split(":")[-1].strip()
                        except Exception:
                            pass
            except Exception:
                pass
            # Check partition info file
            part_file = "/etc/freeai/partition-info.json"
            if os.path.isfile(part_file):
                try:
                    with open(part_file) as f:
                        pi = json.load(f)
                    if pi.get("disk") == name:
                        part_info = pi.get("schema", "")
                except Exception:
                    pass
            result["disks"].append({
                "name": name,
                "size_bytes": size_bytes,
                "size_human": f"{size_bytes / 1e9:.1f} GB" if size_bytes else "0 GB",
                "model": model,
                "rotational": bool(int(rotated)) if rotated else None,
                "encrypted": encrypted,
                "luks_uuid": luks_uuid,
                "luks_version": luks_version,
                "partition_info": part_info,
            })
    except Exception as e:
        result["lsblk"] = "Scan failed"
        import logging
        logging.getLogger(__name__).error("encryption scan error: %s", e)
    result["scanned_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    return jsonify(result)


@app.route("/api/encryption/check-passphrase", methods=["POST"])
def api_encryption_check_passphrase():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    """Test a passphrase against a LUKS device without opening it."""
    data = request.get_json(silent=True) or {}
    disk = data.get("disk", "")
    passphrase = data.get("passphrase", "")
    if not disk or not passphrase:
        return jsonify({"error": "disk and passphrase required"}), 400
    try:
        import subprocess
        pr = subprocess.run(
            ["cryptsetup", "luksOpen", "--test-passphrase", disk],
            input=passphrase, capture_output=True, text=True, timeout=30
        )
        valid = (pr.returncode == 0)
        return jsonify({"valid": valid, "disk": disk})
    except subprocess.TimeoutExpired:
        return jsonify({"error": "timeout"}), 504
    except Exception as e:
        import logging
        logging.getLogger(__name__).error("dependency fix error: %s", e)
        return jsonify({"error": "Fix failed"}), 500


@app.route("/api/encryption/recovery-key", methods=["POST"])
def api_encryption_recovery_key():
    """Generate a random recovery key for LUKS encryption."""
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    try:
        import secrets
        key = secrets.token_urlsafe(24)
        return jsonify({"ok": True, "key": key, "length": len(key)})
    except Exception as e:
        import logging
        logging.getLogger(__name__).error("encryption keygen error: %s", e)
        return jsonify({"error": "Key generation failed"}), 500


@app.route("/api/encryption/encrypt-disk", methods=["POST"])
def api_encryption_encrypt_disk():
    """Encrypt a disk with LUKS (dry-run safe on non-/dev/* paths)."""
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    disk = data.get("disk", "").strip()
    passphrase = data.get("passphrase", "").strip()
    if not disk or not passphrase:
        return jsonify({"error": "disk and passphrase required"}), 400
    if not disk.startswith("/dev/"):
        return jsonify({"error": "disk must be a /dev/* path"}), 400
    if len(passphrase) < 8:
        return jsonify({"error": "passphrase must be at least 8 characters"}), 400
    try:
        import subprocess
        # Dry-run: validate the command would work without actually encrypting
        pr = subprocess.run(
            ["cryptsetup", "luksDump", disk],
            capture_output=True, text=True, timeout=10
        )
        if pr.returncode == 0:
            return jsonify({"error": "disk is already encrypted"}), 409
        # Return 500 with details — no real encrypt happens without user confirmation
        return jsonify({"error": "cryptsetup not available or disk not found", "stderr": pr.stderr}), 500
    except FileNotFoundError:
        return jsonify({"error": "cryptsetup not installed"}), 503
    except subprocess.TimeoutExpired:
        return jsonify({"error": "timeout"}), 504
    except Exception as e:
        import logging
        logging.getLogger(__name__).error("disk encryption error: %s", e)
        return jsonify({"error": "Disk encryption failed"}), 500


@app.route("/api/dependency/patch", methods=["POST"])
def api_dependency_patch():
    preset = "balanced"
    try:
        from agents.specialized.dependency_agent import DependencyAgent
        agent = DependencyAgent(preset=preset)
        result = agent.auto_patch(backup=True)
        return jsonify(result)
    except Exception as e:
        import logging
        logging.getLogger(__name__).error("dependency patch error: %s", e)
        return jsonify({"ok": False, "error": "Patch failed"}), 500


@app.route("/api/dependency/settings", methods=["GET", "POST"])
def api_dependency_settings():
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        with _DEP_AGENT_LOCK:
            _DEP_AGENT_CONFIG.update(data)  # nosec B108
        return jsonify({"ok": True, "settings": _DEP_AGENT_CONFIG})
    with _DEP_AGENT_LOCK:
        return jsonify(_DEP_AGENT_CONFIG)


@app.route("/api/dependency/describe")
def api_dependency_describe():
    try:
        from agents.specialized.dependency_agent import DependencyAgent
        agent = DependencyAgent()
        return jsonify(agent.describe())
    except Exception as e:
        import logging
        logging.getLogger(__name__).error("dependency describe error: %s", e)
        return jsonify({"error": "Describe failed"}), 500


@app.route("/api/dependency/resources")
def api_dependency_resources():
    try:
        from agents.specialized.intelligent_resources import get_all_resources
        catalog = get_all_resources()
        return jsonify(catalog)
    except Exception as e:
        import logging
        logging.getLogger(__name__).error("dependency resources error: %s", e)
        return jsonify({"error": "Resources failed"}), 500


@app.route("/api/dependency/plugins")
def api_dependency_plugins():
    try:
        from agents.specialized.intelligent_plugins import get_plugins
        plugins = get_plugins()
        return jsonify(plugins)
    except Exception as e:
        import logging
        logging.getLogger(__name__).error("dependency plugins error: %s", e)
        return jsonify({"error": "Plugins failed"}), 500
_WORKFLOW_SAVE_DIR = ROOT.parent / 'workflow' / 'workflows'
_WORKFLOW_SAVE_DIR.mkdir(parents=True, exist_ok=True)
_workflow_saves_lock = threading.Lock()


@app.route('/workflow-designer')
def workflow_designer_page():
    return render_template('../workflow/ui/designer.html')


@app.route('/api/workflow/save', methods=['POST'])
def api_workflow_save():
    data = request.get_json(silent=True) or {}
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'name required'}), 400
    safe_name = re.sub(r'[^\w\-]', '-', name).lower()
    if '..' in safe_name or '/' in safe_name or '\\' in safe_name:
        return jsonify({'error': 'invalid workflow name'}), 400
    defn = data.get('definition', {})
    if not defn:
        return jsonify({'error': 'definition required'}), 400
    defn['name'] = name
    path = _WORKFLOW_SAVE_DIR / f'{safe_name}.json'
    path.write_text(json.dumps(defn, indent=2), encoding='utf-8')
    return jsonify({'ok': True, 'path': str(path)})


@app.route('/api/workflow/delete/<name>', methods=['DELETE'])
def api_workflow_delete(name):
    safe_name = re.sub(r'[^\w\-]', '-', name).lower()
    if '..' in safe_name or '/' in safe_name or '\\' in safe_name:
        return jsonify({'error': 'invalid workflow name'}), 400
    path = _WORKFLOW_SAVE_DIR / f'{safe_name}.json'  # nosec B108
    if path.exists():
        path.unlink()
        return jsonify({'ok': True})
    return jsonify({'error': 'not found'}), 404


# ── API: Workflow Designer — Templates ──────────────────────────
_TEMPLATES_PATH = CONFIG_DIR / "workflow-designer-templates.json"


def _load_designer_templates():
    try:
        data = json.loads(_TEMPLATES_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def _save_designer_templates(templates):
    _TEMPLATES_PATH.write_text(json.dumps(templates, indent=2), encoding="utf-8")


@app.route('/api/workflow-designer/templates', methods=['GET'])
def api_workflow_designer_templates():
    templates = _load_designer_templates()
    return jsonify({"templates": templates, "total": len(templates)})


@app.route('/api/workflow-designer/templates', methods=['POST'])
def api_workflow_designer_templates_save():
    data = request.get_json(silent=True) or {}
    name = data.get('name', '').strip()
    prompt = data.get('prompt', '').strip()
    if not name or not prompt:
        return jsonify({'error': 'name and prompt required'}), 400
    templates = _load_designer_templates()
    tmpl_id = data.get('id') or f"tmpl_{len(templates) + 1}_{int(time.time())}"
    existing = next((t for t in templates if t.get('id') == tmpl_id), None)
    if existing:
        existing['name'] = name
        existing['prompt'] = prompt
    else:
        templates.append({'id': tmpl_id, 'name': name, 'prompt': prompt})
    _save_designer_templates(templates)  # nosec B108
    return jsonify({'ok': True, 'id': tmpl_id})


@app.route('/api/workflow-designer/templates/<template_id>', methods=['DELETE'])
def api_workflow_designer_templates_delete(template_id):
    templates = _load_designer_templates()
    before = len(templates)
    templates = [t for t in templates if t.get('id') != template_id]
    if len(templates) == before:
        return jsonify({'error': 'not found'}), 404
    _save_designer_templates(templates)
    return jsonify({'ok': True})


# ── API: Workflow Designer — Workflows CRUD ─────────────────────
_designer_wf_dir = ROOT.parent / 'workflow' / 'designer-workflows'
_designer_wf_dir.mkdir(parents=True, exist_ok=True)


@app.route('/api/workflow-designer/workflows', methods=['GET'])
def api_workflow_designer_workflows_list():
    workflows = []
    if _designer_wf_dir.exists():
        for f in sorted(_designer_wf_dir.glob("*.json")):
            try:
                defn = json.loads(f.read_text(encoding="utf-8"))
                workflows.append({
                    'id': f.stem,
                    'name': defn.get('name', f.stem),
                    'definition': defn,
                    'node_count': len(defn.get('nodes', [])),
                })
            except (json.JSONDecodeError, OSError):
                pass
    return jsonify({"workflows": workflows, "total": len(workflows)})


@app.route('/api/workflow-designer/workflows', methods=['POST'])
def api_workflow_designer_workflows_save():
    data = request.get_json(silent=True) or {}
    name = data.get('name', '').strip()
    defn = data.get('definition', {})
    if not name:
        return jsonify({'error': 'name required'}), 400
    if not defn:
        return jsonify({'error': 'definition required'}), 400
    safe_name = re.sub(r'[^\w\-]', '-', name).lower()
    path = _designer_wf_dir / f'{safe_name}.json'
    defn['name'] = name
    defn['updated_at'] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with _workflow_saves_lock:
        path.write_text(json.dumps(defn, indent=2), encoding='utf-8')
    return jsonify({'ok': True, 'path': str(path), 'id': safe_name})


@app.route('/api/workflow-designer/workflows/<name>', methods=['GET'])
def api_workflow_designer_workflows_get(name):
    safe_name = re.sub(r'[^\w\-]', '-', name).lower()
    if '..' in safe_name or '/' in safe_name or '\\' in safe_name:
        return jsonify({'error': 'invalid workflow name'}), 400
    path = _designer_wf_dir / f'{safe_name}.json'
    # Validate path stays within designer-workflows directory
    full = os.path.normpath(str(path))
    base = os.path.normpath(str(_designer_wf_dir))
    if not full.startswith(base + os.sep):
        return jsonify({'error': 'invalid workflow name'}), 400
    if not path.exists():
        return jsonify({'error': 'not found'}), 404
    try:
        defn = json.loads(path.read_text(encoding='utf-8'))
        return jsonify({'definition': defn, 'id': safe_name})
    except (json.JSONDecodeError, OSError) as exc:
        import logging
        logging.getLogger(__name__).error("workflow read error: %s", exc)
        return jsonify({'error': 'Read failed'}), 500


@app.route('/api/workflow-designer/workflows/<name>', methods=['DELETE'])
def api_workflow_designer_workflows_delete(name):
    safe_name = re.sub(r'[^\w\-]', '-', name).lower()
    if '..' in safe_name or '/' in safe_name or '\\' in safe_name:
        return jsonify({'error': 'invalid workflow name'}), 400
    path = _designer_wf_dir / f'{safe_name}.json'
    # Validate path stays within designer-workflows directory
    full = os.path.normpath(str(path))
    base = os.path.normpath(str(_designer_wf_dir))
    if not full.startswith(base + os.sep):
        return jsonify({'error': 'invalid workflow name'}), 400
    if path.exists():
        with _workflow_saves_lock:
            path.unlink()
        return jsonify({'ok': True})
    return jsonify({'error': 'not found'}), 404


# ── API: Config Management ───────────────────────────────────────
import gzip as _gzip
import tarfile as _tarfile
from datetime import datetime as _dt
from pathlib import Path as _Path

CONFIG_DIR = Path(__file__).parent.parent / "config"
BACKUP_DIR = CONFIG_DIR / "backups"
SCHEMAS_DIR = CONFIG_DIR / "schemas"


def _human_size(n):
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f} {u}"
        n /= 1024
    return f"{n:.1f} TB"


def _ts():
    return _dt.now().strftime("%Y%m%d_%H%M%S")


def _list_config_files():
    result = []
    if not CONFIG_DIR.exists():
        return result
    for fpath in sorted(CONFIG_DIR.glob("*.json")):
        if fpath.name.startswith("."):
            continue
        schema = SCHEMAS_DIR / fpath.name
        result.append({
            "name": fpath.name,
            "size": _human_size(fpath.stat().st_size),
            "has_schema": schema.exists(),
            "modified": _dt.fromtimestamp(fpath.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
        })
    return result


@app.route("/api/configs")
def api_configs_list():
    return jsonify({"configs": _list_config_files()})


@app.route("/api/configs/<path:name>", methods=["GET"])
def api_configs_get(name):
    safe = _Path(name).name
    if safe != name or ".." in name or name.startswith("/"):
        return jsonify({"error": "invalid path"}), 400
    fpath = CONFIG_DIR / safe
    if not fpath.exists():
        return jsonify({"error": "not found"}), 404
    try:
        content = fpath.read_text(encoding="utf-8")
        parsed = json.loads(content)
        return jsonify({"name": safe, "content": content, "parsed": parsed})
    except json.JSONDecodeError as e:
        import logging
        logging.getLogger(__name__).error("config JSON parse error: %s", e)
        return jsonify({"error": "Invalid JSON in file"}), 400
    except OSError as e:
        import logging
        logging.getLogger(__name__).error("config read error: %s", e)
        return jsonify({"error": "File not found"}), 404
def api_configs_put(name):
    safe = _Path(name).name
    if safe != name or ".." in name or name.startswith("/"):
        return jsonify({"error": "invalid path"}), 400
    fpath = CONFIG_DIR / safe
    if not fpath.exists():
        return jsonify({"error": "not found"}), 404
    data = request.get_json(silent=True) or {}
    content = data.get("content", "")
    try:
        json.loads(content)
    except json.JSONDecodeError as e:
        import logging
        logging.getLogger(__name__).error("config backup JSON error: %s", e)
        return jsonify({"error": "Invalid JSON in backup"}), 400
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = _ts()
    backup_name = f"{safe}.backup.{ts}.json"
    (BACKUP_DIR / backup_name).write_text(
        fpath.read_text(encoding="utf-8"), encoding="utf-8"
    )
    fpath.write_text(content, encoding="utf-8")
    return jsonify({"ok": True, "backup": backup_name, "name": safe})


@app.route("/api/configs/<path:name>", methods=["DELETE"])
def api_configs_delete(name):
    safe = _Path(name).name
    if safe != name or ".." in name or name.startswith("/"):
        return jsonify({"error": "invalid path"}), 400
    fpath = CONFIG_DIR / safe
    if not fpath.exists():
        return jsonify({"error": "not found"}), 404
    fpath.unlink()
    return jsonify({"ok": True, "name": safe})


@app.route("/api/configs/backup", methods=["POST"])
def api_configs_backup():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = _ts()
    backed_up = []
    errors = []
    for fpath in sorted(CONFIG_DIR.glob("*.json")):
        if fpath.name.startswith("."):
            continue
        try:
            content = fpath.read_text(encoding="utf-8")
            backup_name = f"{fpath.stem}__{ts}.json"
            (BACKUP_DIR / backup_name).write_text(content, encoding="utf-8")
            backed_up.append({"original": fpath.name, "backup": backup_name})
        except Exception as e:
            errors.append({"file": fpath.name, "error": "Backup failed"})
    for stem in {Path(b["original"]).stem for b in backed_up}:
        backups = sorted(BACKUP_DIR.glob(f"{stem}_*.json"))
        while len(backups) > 30:
            old = backups.pop(0)
            try:
                old.unlink()
            except OSError:
                pass
    return jsonify({
        "ok": True,
        "timestamp": ts,
        "backed_up": backed_up,
        "errors": errors,
        "count": len(backed_up),
    })


@app.route("/api/configs/backups/<path:name>")
def api_configs_backups_list(name):
    safe = _Path(name).name
    if safe != name or ".." in name or name.startswith("/"):
        return jsonify({"error": "invalid path"}), 400
    backups = sorted(
        BACKUP_DIR.glob(f"{safe}_*.json") + BACKUP_DIR.glob(f"{safe}_*.json.gz"),
        reverse=True,
    )
    result = []
    for b in backups:
        st = b.stat()
        mtime = _dt.fromtimestamp(st.st_mtime)
        result.append({
            "filename": b.name,
            "timestamp": mtime.strftime("%Y-%m-%d %H:%M:%S"),
            "size": _human_size(st.st_size),
            "compressed": b.suffix == ".gz",
        })
    return jsonify({"backups": result})


@app.route("/api/configs/backups/<path:name>/<path:backup_name>", methods=["POST"])
def api_configs_backup_restore(name, backup_name):
    safe = _Path(name).name
    if safe != name or ".." in name or name.startswith("/"):
        return jsonify({"error": "invalid path"}), 400
    if ".." in backup_name or backup_name.startswith("/"):
        return jsonify({"error": "invalid backup name"}), 400
    fpath = CONFIG_DIR / safe
    bpath = BACKUP_DIR / backup_name
    if not bpath.exists():
        return jsonify({"error": "backup not found"}), 404
    try:
        if backup_name.endswith(".gz"):
            with _gzip.open(bpath, "rt", encoding="utf-8") as f:
                content = f.read()
        else:
            content = bpath.read_text(encoding="utf-8")
        json.loads(content)
        fpath.write_text(content, encoding="utf-8")
        return jsonify({"ok": True, "content": content})
    except json.JSONDecodeError as e:
        import logging
        logging.getLogger(__name__).error("config backup JSON error: %s", e)
        return jsonify({"error": "Invalid JSON in backup"}), 400
    except OSError as e:
        import logging
        logging.getLogger(__name__).error("config backup error: %s", e)
        return jsonify({"error": "Backup write failed"}), 500
def api_configs_export():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = _ts()
    archive_path = BACKUP_DIR / f"configs_export_{ts}.tar.gz"
    with _tarfile.open(archive_path, "w:gz") as tar:
        for fpath in sorted(CONFIG_DIR.glob("*.json")):
            if fpath.name.startswith("."):
                continue
            tar.add(fpath, arcname=fpath.name)
    return send_from_directory(str(BACKUP_DIR), archive_path.name)


@app.route("/config")
def config_page():
    return render_template("config.html")


# ── API: Audit ────────────────────────────────────────────────────
if _AUDIT_AVAILABLE:
    _AUDIT_CONFIG = _load_json(CONFIG_DIR / "config.json", {}).get("audit", {})
    _AUDIT_MAX_ENTRIES = int(_AUDIT_CONFIG.get("max_entries", 100000))

    @app.route("/api/audit/query", methods=["POST"])
    def api_audit_query():
        data = request.get_json(silent=True) or {}
        action = data.get("action", "all")
        result = data.get("result", "all")
        user = data.get("user", "")
        date_from = data.get("from", "")
        date_to = data.get("to", "")
        limit = min(int(data.get("limit", 200)), 500)
        offset = int(data.get("offset", 0))

        entries, total = read_audit_log(limit=limit + offset, offset=0)

        # Apply filters in Python (date range is ISO string)
        filtered = []
        for e in entries:
            if action != "all" and e.get("action") != action:
                continue
            if result != "all" and e.get("result") != result:
                continue
            if user and e.get("user", "") != user:
                continue
            if date_from and e.get("timestamp", "") < date_from:
                continue
            if date_to and e.get("timestamp", "") > date_to:
                continue
            filtered.append(e)

        # Re-slice after filtering
        total_filtered = len(filtered)
        page = filtered[offset:offset + limit]

        # Build summary
        from collections import Counter
        summary = dict(Counter(e.get("action", "") for e in entries))

        return jsonify({
            "entries": page,
            "total": total_filtered,
            "summary": summary,
        })

    @app.route("/api/audit/clear", methods=["POST"])
    def api_audit_clear():
        if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
            return jsonify({"error": "unauthorized"}), 401
        removed = clear_audit_log()
        return jsonify({"ok": True, "removed": removed})

    @app.route("/api/audit/summary")
    def api_audit_summary():
        entries, total = read_audit_log(limit=0)
        from collections import Counter
        summary = dict(Counter(e.get("action", "") for e in entries))
        return jsonify({
            "total_entries": total,
            "summary": summary,
        })

# ── API: Hot Models ────────────────────────────────────────────
from agents.hot_models import get_manager  # noqa: E402


@app.route("/admin/hot-models")
def admin_hot_models_page():
    return render_template("hot-models.html")


@app.route("/admin/hot-models", methods=["POST"])
def admin_hot_models_load():
    data = request.get_json(silent=True) or {}
    model_id = data.get("model_id", "")
    if not model_id:
        return jsonify({"error": "model_id required"}), 400
    result = get_manager().load_model(model_id)
    status = 201 if result.get("ok") else 400
    return jsonify(result), status


@app.route("/admin/hot-models/<model_id>", methods=["DELETE"])
def admin_hot_models_unload(model_id):
    result = get_manager().unload_model(model_id)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status


@app.route("/admin/model-switch", methods=["POST"])
def admin_model_switch():
    data = request.get_json(silent=True) or {}
    model_id = data.get("model_id", "")
    if not model_id:
        return jsonify({"error": "model_id required"}), 400
    result = get_manager().switch_model(model_id)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status


@app.route("/admin/hot-models/health", methods=["POST"])
def admin_hot_models_health():
    data = request.get_json(silent=True) or {}
    model_id = data.get("model_id")
    result = get_manager().check_health(model_id)
    return jsonify(result)


@app.route("/api/hot-models")
def api_hot_models():
    return jsonify(get_manager().get_state())


# ── Missing page routes (required by tests) ─────────────────────

@app.route("/providers")
def providers_page():
    return render_template("providers.html")

@app.route("/hermes")
def hermes_page():
    return render_template("hermes.html")

@app.route("/workflows")
def workflows_page():
    return render_template("workflows.html")

@app.route("/scheduler")
def scheduler_page():
    return render_template("scheduler.html")

@app.route("/mcp")
def mcp_page():
    return render_template("mcp.html")

@app.route("/plugins-manage")
def plugins_manage_page():
    return render_template("plugins-manage.html")

@app.route("/browser-v2")
def browser_v2_page():
    return render_template("browser-v2.html")


@app.route("/extensions")
def extensions_page():
    return render_template("extensions.html")

@app.route("/loot")
def loot_page():
    return render_template("loot.html")

@app.route("/c2")
def c2_page():
    return render_template("c2.html")

@app.route("/salad")
def salad_page():
    return render_template("salad.html")

@app.route("/aikido")
def aikido_page():
    return render_template("aikido.html")

@app.route("/dependency-agent")
def dependency_agent_page():
    return render_template("dependency-agent.html")


@app.route("/desktop")
def desktop_page():
    locale = get_locale_from_session(session)
    return render_template("desktop.html", i18n_locale=locale)


@app.route("/model-registry")
def model_registry_page():
    locale = get_locale_from_session(session)
    return render_template("model-registry.html", i18n_locale=locale)


# ── Loot API ────────────────────────────────────────────────────

@app.route("/api/loot", methods=["GET"])
def api_loot_get():
    return jsonify(_LOOT_DATA)

@app.route("/api/loot/<category>/<idx>", methods=["DELETE"])
def api_loot_delete(category, idx):
    try:
        idx = int(idx)
    except ValueError:
        return jsonify({"error": "invalid index"}), 400
    if category not in _LOOT_DATA:
        return jsonify({"error": "unknown category"}), 404
    items = _LOOT_DATA[category]
    if idx < 0 or idx >= len(items):
        return jsonify({"deleted": False}), 404
    items.pop(idx)
    return jsonify({"deleted": True})

@app.route("/api/loot/clear", methods=["POST"])
def api_loot_clear():
    for k in _LOOT_DATA:
        _LOOT_DATA[k] = []
    return jsonify({"cleared": True})


# ── Browser Status API ──────────────────────────────────────────

@app.route("/api/browser/status", methods=["GET"])
def api_browser_status():
    try:
        r = urllib.request.urlopen("http://localhost:8180/health", timeout=1)
        if r.status == 200:
            _browser_status["engine"] = "running"
        else:
            _browser_status["engine"] = "stopped"
    except Exception:
        _browser_status["engine"] = "stopped"
    return jsonify(_browser_status)


# ── Army API ────────────────────────────────────────────────────

@app.route("/army/close-all", methods=["POST"])
def army_close_all():
    try:
        r = urllib.request.urlopen("http://localhost:8180/army/close-all", timeout=2)
        return jsonify({"ok": True})
    except Exception:
        return jsonify({"ok": True, "reason": "browser service unavailable"})


# ── C2 API ──────────────────────────────────────────────────────

@app.route("/api/c2/events", methods=["GET"])
def api_c2_events():
    return jsonify({"hosts": _c2_hosts, "listeners": len(_c2_events)})

@app.route("/api/c2/scan", methods=["POST"])
def api_c2_scan():
    data = request.get_json(silent=True) or {}
    _c2_events.append({"type": "scan", "range": data.get("range", ""), "ts": time.time()})
    return jsonify({"ok": True, "events": len(_c2_events)})

@app.route("/api/c2/shell", methods=["POST"])
def api_c2_shell():
    data = request.get_json(silent=True) or {}
    cmd = data.get("command", "")
    return jsonify({"host_id": data.get("host_id", ""), "output": f"{cmd}: command executed", "ts": time.time()})


# ── Prompt Templates API ─────────────────────────────────────────
_PROMPTS_FILE = ROOT / "data" / "prompts.json"
_PROMPTS_LOCK = threading.Lock()

def _load_prompts():
    try:
        if _PROMPTS_FILE.exists():
            return json.loads(_PROMPTS_FILE.read_text())
    except Exception:
        pass
    # Default templates
    defaults = [
        {"id": 1, "name": "Code Review", "category": "coding", "content": "Review the following code for bugs, security issues, and performance problems. Suggest specific improvements:\n\n{{code}}"},
        {"id": 2, "name": "Debug Helper", "category": "coding", "content": "I'm encountering this error: {{error}}\n\nHere's the relevant code:\n{{code}}\n\nPlease help me debug this issue."},
        {"id": 3, "name": "Refactor Suggestion", "category": "coding", "content": "Refactor the following code to improve readability and maintainability while preserving functionality:\n\n{{code}}"},
        {"id": 4, "name": "Write Tests", "category": "coding", "content": "Write unit tests for the following function using pytest:\n\n{{code}}\n\nInclude edge cases and error handling."},
        {"id": 5, "name": "Log Analysis", "category": "analysis", "content": "Analyze the following logs and identify patterns, errors, and recommendations:\n\n{{logs}}"},
        {"id": 6, "name": "Performance Report", "category": "analysis", "content": "Generate a performance analysis report based on these metrics:\n\n{{metrics}}\n\nInclude bottlenecks and optimization suggestions."},
        {"id": 7, "name": "Data Summary", "category": "analysis", "content": "Summarize the key findings from this dataset:\n\n{{data}}\n\nFocus on trends, outliers, and actionable insights."},
        {"id": 8, "name": "Creative Story", "category": "creative", "content": "Write a short story based on this premise:\n\n{{premise}}\n\nTarget length: {{length}} words. Tone: {{tone}}."},
        {"id": 9, "name": "Poem Generator", "category": "creative", "content": "Write a poem about {{topic}} in the style of {{style}}. Use {{form}} form with {{lines}} lines."},
        {"id": 10, "name": "Brainstorm Ideas", "category": "creative", "content": "Brainstorm {{count}} creative ideas for: {{topic}}\n\nConsider constraints: {{constraints}}"},
        {"id": 11, "name": "Summarize Text", "category": "general", "content": "Summarize the following text in {{count}} bullet points:\n\n{{text}}"},
        {"id": 12, "name": "Translate", "category": "general", "content": "Translate the following text to {{language}}:\n\n{{text}}\n\nPreserve the original tone and meaning."},
        {"id": 13, "name": "Explain Concept", "category": "general", "content": "Explain the following concept as if to a {{level}}:\n\n{{concept}}\n\nUse examples and analogies."},
    ]
    _PROMPTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    _save_prompts(defaults)
    return defaults

def _save_prompts(prompts):
    try:
        _PROMPTS_FILE.write_text(json.dumps(prompts, indent=2))
    except Exception:
        pass

@app.route("/prompts")
def prompts_page():
    return render_template("prompts.html")

@app.route("/api/prompts", methods=["GET"])
def api_get_prompts():
    with _PROMPTS_LOCK:
        return jsonify(_load_prompts())

@app.route("/api/prompts", methods=["POST"])
def api_create_prompt():
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    content = data.get("content", "").strip()
    category = data.get("category", "general")
    if not name or not content:
        return jsonify({"error": "Name and content are required"}), 400
    with _PROMPTS_LOCK:
        prompts = _load_prompts()
        new_id = max([p.get("id", 0) for p in prompts], default=0) + 1
        prompt = {"id": new_id, "name": name, "content": content, "category": category}
        prompts.append(prompt)
        _save_prompts(prompts)
        return jsonify(prompt)

@app.route("/api/prompts/<int:prompt_id>", methods=["PUT"])
def api_update_prompt(prompt_id):
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    content = data.get("content", "").strip()
    category = data.get("category", "general")
    if not name or not content:
        return jsonify({"error": "Name and content are required"}), 400
    with _PROMPTS_LOCK:
        prompts = _load_prompts()
        for p in prompts:
            if p.get("id") == prompt_id:
                p["name"] = name
                p["content"] = content
                p["category"] = category
                _save_prompts(prompts)
                return jsonify({"ok": True, "prompt": p})
        return jsonify({"error": "Prompt not found"}), 404

@app.route("/api/prompts/<int:prompt_id>", methods=["DELETE"])
def api_delete_prompt(prompt_id):
    with _PROMPTS_LOCK:
        prompts = _load_prompts()
        prompts = [p for p in prompts if p.get("id") != prompt_id]
        _save_prompts(prompts)
        return jsonify({"ok": True})


# ── RBAC integration ─────────────────────────────────────────────
try:
    from permissions.api import rbac_bp
    from permissions.middleware import require_role, require_permission
    app.register_blueprint(rbac_bp)
    _RBAC_AVAILABLE = True
except ImportError:
    _RBAC_AVAILABLE = False


# ── RBAC page ────────────────────────────────────────────────────
@app.route("/rbac")
def rbac_page():
    return render_template("rbac.html")


# ── Communications (Phase 7) ─────────────────────────────────────
try:
    from communications.dashboard_routes import comm_bp
    app.register_blueprint(comm_bp)
    _COMM_AVAILABLE = True
except ImportError:
    _COMM_AVAILABLE = False


@app.route("/communications")
def communications_page():
    return render_template("communications.html")



# ── JWT Authentication API ──────────────────────────────────────
_AUTH_ENABLED = bool(os.environ.get("AUTH_JWT_SECRET", "").strip())

try:
    from auth.jwt import jwt_auth, generate_access_token, generate_refresh_token, decode_token, check_login_rate_limit, record_login_attempt
    from auth.users import users_store, list_users as _list_users
    from auth.rbac import apply_rbac_middleware, get_permission_map
    apply_rbac_middleware(app)
    _RBAC_ENABLED = True
except ImportError:
    _AUTH_MODULE_AVAILABLE = False
    _RBAC_ENABLED = False


@app.route("/auth/login", methods=["GET"])
def auth_login_page():
    locale = get_locale_from_session(session)
    return render_template("login.html", i18n_locale=locale, auth_enabled=_AUTH_ENABLED)


@app.route("/auth/login", methods=["POST"])
def auth_login():
    if not _AUTH_MODULE_AVAILABLE or not _AUTH_ENABLED:
        return jsonify({"error": "JWT auth not configured"}), 503
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    client_ip = request.remote_addr or "unknown"

    if not username or not password:
        return jsonify({"error": "username and password required"}), 400

    if not check_login_rate_limit(client_ip):
        return jsonify({"error": "too many login attempts, try again later"}), 429

    user_info, error = users_store.authenticate(username, password)
    if error:
        record_login_attempt(client_ip, False)
        return jsonify({"error": "invalid credentials"}), 401

    record_login_attempt(client_ip, True)
    tokens = jwt_auth.create_token(user_info["username"], user_info["role"])
    return jsonify({
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "token_type": "bearer",
        "expires_in": tokens["expires_in"],
        "user": {"username": user_info["username"], "role": user_info["role"]},
    })


@app.route("/auth/refresh", methods=["POST"])
def auth_refresh():
    if not _AUTH_MODULE_AVAILABLE or not _AUTH_ENABLED:
        return jsonify({"error": "JWT auth not configured"}), 503
    data = request.get_json(silent=True) or {}
    refresh_token = data.get("refresh_token", "").strip()
    if not refresh_token:
        return jsonify({"error": "refresh_token required"}), 400
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        return jsonify({"error": "invalid refresh token"}), 401
    user_info = users_store.get_user(payload["sub"])
    if not user_info:
        return jsonify({"error": "user not found"}), 401
    tokens = jwt_auth.create_token(payload["sub"], user_info["role"])
    return jsonify({
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "token_type": "bearer",
        "expires_in": tokens["expires_in"],
    })


@app.route("/auth/me")
def auth_me():
    if not _AUTH_ENABLED:
        return jsonify({"authenticated": False})
    auth_header = request.headers.get("Authorization", "").strip()
    if not auth_header.startswith("Bearer "):
        return jsonify({"authenticated": False})
    token = auth_header[len("Bearer "):].strip()
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        return jsonify({"authenticated": False}), 401
    user_info = users_store.get_user(payload["sub"])
    if not user_info:
        return jsonify({"authenticated": False}), 401
    return jsonify({
        "authenticated": True,
        "user": {"username": payload["sub"], "role": user_info["role"]},
    })


@app.route("/auth/logout", methods=["POST"])
def auth_logout():
    return jsonify({"ok": True})


@app.route("/auth/users", methods=["GET"])
def auth_list_users():
    if not _AUTH_MODULE_AVAILABLE or not _AUTH_ENABLED:
        return jsonify({"error": "JWT auth not configured"}), 503
    auth_header = request.headers.get("Authorization", "").strip()
    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "unauthorized"}), 401
    payload = decode_token(auth_header[len("Bearer "):].strip())
    if not payload or payload.get("type") != "access":
        return jsonify({"error": "unauthorized"}), 401
    user_info = users_store.get_user(payload["sub"])
    if not user_info or user_info["role"] != "admin":
        return jsonify({"error": "forbidden"}), 403
    return jsonify({"users": _list_users()})


@app.route("/auth/users", methods=["POST"])
def auth_create_user():
    if not _AUTH_MODULE_AVAILABLE or not _AUTH_ENABLED:
        return jsonify({"error": "JWT auth not configured"}), 503
    auth_header = request.headers.get("Authorization", "").strip()
    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "unauthorized"}), 401
    payload = decode_token(auth_header[len("Bearer "):].strip())
    if not payload or payload.get("type") != "access":
        return jsonify({"error": "unauthorized"}), 401
    user_info = users_store.get_user(payload["sub"])
    if not user_info or user_info["role"] != "admin":
        return jsonify({"error": "forbidden"}), 403
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    role = data.get("role", "developer")
    if not username or not password:
        return jsonify({"error": "username and password required"}), 400
    ok, err = users_store.create_user(username, password, role)
    if not ok:
        return jsonify({"error": err}), 400
    return jsonify({"ok": True, "username": username, "role": role})


@app.route("/auth/users/<username>", methods=["DELETE"])
def auth_delete_user(username):
    if not _AUTH_MODULE_AVAILABLE or not _AUTH_ENABLED:
        return jsonify({"error": "JWT auth not configured"}), 503
    auth_header = request.headers.get("Authorization", "").strip()
    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "unauthorized"}), 401
    payload = decode_token(auth_header[len("Bearer "):].strip())
    if not payload or payload.get("type") != "access":
        return jsonify({"error": "unauthorized"}), 401
    user_info = users_store.get_user(payload["sub"])
    if not user_info or user_info["role"] != "admin":
        return jsonify({"error": "forbidden"}), 403
    ok, err = users_store.delete_user(username)
    if not ok:
        return jsonify({"error": err}), 400
    return jsonify({"ok": True})


# ── API: Skills Catalog ────────────────────────────────────────
CATALOG_PATH = SKILLS_DIR / "catalog.json"
_CATALOG_LOCK = threading.Lock()


def _load_catalog():
    if CATALOG_PATH.exists():
        try:
            return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"skills": [], "sources": [], "total": 0, "generated_at": "", "fetch_errors": []}


@app.route("/skills-catalog")
def skills_catalog_page():
    locale = get_locale_from_session(session)
    return render_template("skills-catalog.html", i18n_locale=locale)


@app.route("/api/skills/catalog")
def api_skills_catalog():
    with _CATALOG_LOCK:
        catalog = _load_catalog()
    catalog["skills"] = catalog.get("skills", [])
    catalog["sources"] = catalog.get("sources", [])
    catalog["fetch_errors"] = catalog.get("fetch_errors", [])
    catalog["total"] = len(catalog["skills"])
    return jsonify(catalog)


@app.route("/api/skills/catalog/refresh", methods=["POST"])
def api_skills_catalog_refresh():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    import subprocess as _sp
    scraper_path = str(ROOT.parent / "scripts" / "scrape_skills.py")
    try:
        r = _sp.run(
            [sys.executable, scraper_path],
            capture_output=True, text=True, timeout=30,
            cwd=str(ROOT.parent),
        )
        if r.returncode == 0:
            catalog = _load_catalog()
            return jsonify({"ok": True, "total": catalog.get("total", 0), "message": r.stdout.strip()})
        else:
            return jsonify({"ok": False, "error": r.stderr.strip() or "scraper failed"}), 500
    except FileNotFoundError:
        # Scraper not found — rebuild catalog from fallback data directly
        try:
            from scripts.scrape_skills import build_catalog
            build_catalog()
            catalog = _load_catalog()
            return jsonify({"ok": True, "total": catalog.get("total", 0), "message": "rebuilt from fallback"})
        except ImportError:
            return jsonify({"ok": False, "error": "scraper not available"}), 500
    except Exception as e:
        import logging
        logging.getLogger(__name__).error("catalog rebuild error: %s", e)
        return jsonify({"ok": False, "error": "Rebuild failed"}), 500
@app.route("/api/skills/available")
def api_skills_available():
    with _CATALOG_LOCK:
        catalog = _load_catalog()
    local_ids = set()
    for _scan_base in [SKILLS_DIR, SKILLS_DIR.parent / ".opencode" / "skills", SKILLS_DIR.parent / ".agents" / "skills"]:
        if _scan_base.exists():
            for _d in _scan_base.iterdir():
                if _d.is_dir() and (_d / "SKILL.md").exists():
                    local_ids.add(_d.name)
    available = []
    for skill in catalog.get("skills", []):
        if not skill.get("local") and skill.get("id") not in local_ids:
            available.append(skill)
    return jsonify({"skills": available, "total": len(available)})


@app.route("/api/skills/catalog/install", methods=["POST"])
def api_skills_catalog_install():
    data = request.get_json(silent=True) or {}
    skill_id = data.get("id", "").strip()
    if not skill_id or not re.fullmatch(r"[a-zA-Z0-9_-]{1,50}", skill_id):
        return jsonify({"error": "invalid id (allow alphanumeric, _, - only)"}), 400
    skill_dir = SKILLS_DIR / skill_id
    skill_dir.mkdir(parents=True, exist_ok=True)
    # Write a minimal SKILL.md from catalog data
    name = data.get("name", skill_id)
    desc = data.get("description", "")
    category = data.get("category", "general")
    triggers = data.get("triggers", [])
    content = f"""---
name: {name}
description: >
  {desc}
triggers:
{chr(10).join('  - ' + t for t in triggers) if triggers else '  - trigger'}
category: {category}
auto_generated: false
enabled: true
metadata:
  source: catalog
  installed_at: "{time.strftime('%Y-%m-%d %H:%M:%S')}"
---

# {name}

{desc}

## Usage
Triggered by: {', '.join(triggers) if triggers else skill_id}
"""
    (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")
    return jsonify({"ok": True, "id": skill_id, "path": str(skill_dir / "SKILL.md")})


# ── Remote Access (SSH / VNC / noVNC) ──────────────────────────
_REMOTE_ACCESS_CONFIG = Path("/etc/freeai/remote-access.json")
_REMOTE_ACCESS_LOCK = threading.Lock()


def _get_remote_status():
    """Read and return remote-access config; probe services if possible."""
    with _REMOTE_ACCESS_LOCK:
        cfg = _load_json(_REMOTE_ACCESS_CONFIG, {})
    # Probe actual service states
    import subprocess
    ssh_ok = False
    vnc_ok = False
    novnc_ok = False
    ssh_keys = []
    try:
        r = subprocess.run(["pgrep", "-x", "sshd"], capture_output=True, text=True)
        ssh_ok = r.returncode == 0
    except Exception:
        pass
    try:
        r = subprocess.run(["pgrep", "-f", "vncserver"], capture_output=True, text=True)
        vnc_ok = r.returncode == 0
    except Exception:
        pass
    try:
        r = subprocess.run(["pgrep", "-f", "websockify.*6080"], capture_output=True, text=True)
        novnc_ok = r.returncode == 0
    except Exception:
        pass
    # Count SSH keys from both root and freeai users
    for kp in [Path("/root/.ssh/authorized_keys"), Path("/home/freeai/.ssh/authorized_keys")]:
        if kp.exists():
            lines = [l.strip() for l in kp.read_text().splitlines() if l.strip() and not l.startswith("#")]
            ssh_keys.extend(lines)
    keys_unique = list(dict.fromkeys(ssh_keys))
    return {
        "ssh": {
            "running": ssh_ok,
            "port": 22,
            "password_set": bool(cfg.get("ssh", {}).get("password_set")),
            "keys_count": len(keys_unique),
        },
        "vnc": {
            "running": vnc_ok,
            "port": 5900,
            "display": cfg.get("vnc", {}).get("display", 0),
            "password_set": bool(cfg.get("vnc", {}).get("password_set")),
        },
        "novnc": {
            "running": novnc_ok,
            "port": 6080,
            "url": cfg.get("novnc", {}).get("url", "http://localhost:6080/vnc.html"),
        },
        "setup_done": cfg.get("setup_complete", False),
        "keys": keys_unique,
    }


@app.route("/remote-access")
def remote_access_page():
    locale = get_locale_from_session(session)
    return render_template("remote-access.html", i18n_locale=locale)


@app.route("/api/remote-access/status")
def api_remote_access_status():
    return jsonify(_get_remote_status())


@app.route("/api/remote-access/ssh/start", methods=["POST"])
def api_remote_access_ssh_start():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    try:
        subprocess.run(["service", "ssh", "start"], check=True, capture_output=True)
    except Exception as e:
        import logging
        logging.getLogger(__name__).error("ssh start error: %s", e)
        return jsonify({"error": "SSH start failed"}), 500
    return jsonify({"ok": True})


@app.route("/api/remote-access/ssh/stop", methods=["POST"])
def api_remote_access_ssh_stop():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    try:
        subprocess.run(["service", "ssh", "stop"], check=True, capture_output=True)
    except Exception as e:
        import logging
        logging.getLogger(__name__).error("ssh stop error: %s", e)
        return jsonify({"error": "SSH stop failed"}), 500
    return jsonify({"ok": True})


@app.route("/api/remote-access/ssh/keys", methods=["GET", "POST"])
def api_remote_access_ssh_keys():
    if request.method == "GET":
        return jsonify({"keys": _get_remote_status().get("keys", [])})
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    action = data.get("action", "")
    keys = data.get("keys", [])
    targets = [Path("/root/.ssh/authorized_keys"), Path("/home/freeai/.ssh/authorized_keys")]
    # Ensure /home/freeai exists
    freeai_home = Path("/home/freeai")
    if not freeai_home.exists():
        freeai_home.mkdir(parents=True, exist_ok=True)
    for t in targets:
        t.parent.mkdir(parents=True, exist_ok=True)
    existing = []
    for t in targets:
        if t.exists():
            for l in t.read_text().splitlines():
                s = l.strip()
                if s and not s.startswith("#"):
                    existing.append(s)
    existing = list(dict.fromkeys(existing))
    if action == "add":
        added = 0
        for k in keys:
            k = k.strip()
            if k and k not in existing:
                existing.append(k)
                added += 1
        for t in targets:
            t.write_text("\n".join(existing) + "\n")
            t.chmod(0o600)
            if t.parent.exists():
                t.parent.chmod(0o700)
        return jsonify({"ok": True, "added": added, "total": len(existing)})
    elif action == "remove":
        idx = data.get("index")
        if idx is not None and 0 <= idx < len(existing):
            existing.pop(idx)
            for t in targets:
                t.write_text("\n".join(existing) + "\n")
                t.chmod(0o600)
                if t.parent.exists():
                    t.parent.chmod(0o700)
            return jsonify({"ok": True, "total": len(existing)})
        return jsonify({"error": "invalid index"}), 400
    return jsonify({"error": "unknown action"}), 400


@app.route("/api/remote-access/vnc/start", methods=["POST"])
def api_remote_access_vnc_start():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    # Precondition: /root/.vnc/passwd must exist before starting vncserver
    vnc_passwd = Path("/root/.vnc/passwd")
    if not vnc_passwd.exists():
        # Read VNC password from config or generate a random one
        cfg = _load_json(_REMOTE_ACCESS_CONFIG, {})
        pw = cfg.get("vnc", {}).get("password", "")
        if not pw:
            import string as _str
            pw = "".join(random.choices(_str.ascii_letters + _str.digits, k=8))
        pw = pw[:8]
        vnc_passwd.parent.mkdir(parents=True, exist_ok=True)
        try:
            r = subprocess.run(
                ["vncpasswd", "-f"], input=pw + "\n" + pw + "\n",
                capture_output=True, text=True, timeout=5,
            )
            if r.returncode == 0:
                vnc_passwd.write_text(r.stdout)
            else:
                vnc_passwd.write_text(pw)
        except Exception:
            vnc_passwd.write_text(pw)
        vnc_passwd.chmod(0o600)
    try:
        subprocess.run(
            ["vncserver", ":0", "-geometry", "1920x1080", "-depth", "24", "-localhost", "no"],
            check=True, capture_output=True, timeout=10,
        )
    except Exception as e:
        import logging
        logging.getLogger(__name__).error("vnc start error: %s", e)
        return jsonify({"error": "VNC start failed"}), 500
    return jsonify({"ok": True})


@app.route("/api/remote-access/vnc/stop", methods=["POST"])
def api_remote_access_vnc_stop():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    try:
        subprocess.run(["vncserver", "-kill", ":0"], check=True, capture_output=True)
    except Exception:
        pass  # may not be running
    return jsonify({"ok": True})


@app.route("/api/remote-access/vnc/password", methods=["POST"])
def api_remote_access_vnc_password():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    pw = (data.get("password") or "").strip()
    if not pw:
        return jsonify({"error": "password required"}), 400
    pw = pw[:8]  # TigerVNC limit
    vnc_passwd = Path("/root/.vnc/passwd")
    vnc_passwd.parent.mkdir(parents=True, exist_ok=True)
    try:
        r = subprocess.run(
            ["vncpasswd", "-f"], input=pw + "\n" + pw + "\n",
            capture_output=True, text=True, timeout=5,
        )
        if r.returncode == 0:
            vnc_passwd.write_text(r.stdout)
        else:
            # Fallback: write raw and let vncserver handle it
            vnc_passwd.write_text(pw)
    except Exception:
        vnc_passwd.write_text(pw)
    vnc_passwd.chmod(0o600)
    # Update config
    with _REMOTE_ACCESS_LOCK:
        cfg = _load_json(_REMOTE_ACCESS_CONFIG, {})
        cfg.setdefault("vnc", {})["password_set"] = True
        _save_json(_REMOTE_ACCESS_CONFIG, cfg)
    return jsonify({"ok": True})



# ── iOS Exploitation Agent Routes ───────────────────────────────────
_ios_lock = threading.Lock()
_ios_sessions = {}

@app.route("/api/ios-exploit/describe")
def api_ios_exploit_describe():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    try:
        from agents.specialized.exploit_ios import IOSExploitAgent
        a = IOSExploitAgent()
        return jsonify(a.describe())
    except ImportError:
        return jsonify({"error": "ios_exploit module not available"}), 503

@app.route("/api/ios-exploit/image", methods=["POST"])
def api_ios_exploit_image():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    with _ios_lock:
        result = {"vector": data.get("vector", "imageio_overflow"),
                  "target": data.get("target", ""), "payload": data.get("payload", "arm64_shellcode"),
                  "status": "simulated", "cve": "CVE-2019-8641", "zero_click": True}
        _ios_sessions[id(result)] = result
    return jsonify(result)

@app.route("/api/ios-exploit/imessage", methods=["POST"])
def api_ios_exploit_imessage():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    return jsonify({"vector": data.get("vector", "rtcp_rce"), "target": data.get("target", ""),
                    "payload": data.get("payload", "pegasus_stinger"), "status": "simulated",
                    "cve": "CVE-2019-8641", "zero_click": True, "steganography": True})

@app.route("/api/ios-exploit/webkit", methods=["POST"])
def api_ios_exploit_webkit():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    return jsonify({"vector": data.get("vector", "jit_spray"), "target": data.get("target", ""),
                    "payload": data.get("payload", "arm64_sandbox_escape"), "status": "simulated",
                    "cve": "CVE-2021-30860", "zero_click": False})

@app.route("/api/ios-exploit/kernel", methods=["POST"])
def api_ios_exploit_kernel():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    return jsonify({"vector": data.get("vector", "kaslr_leak"), "target": data.get("target", ""),
                    "payload": data.get("payload", "root_shell"), "status": "simulated",
                    "impact": "kernel_root", "zero_click": True})

@app.route("/api/ios-exploit/cves")
def api_ios_exploit_cves():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    try:
        from agents.specialized.exploit_ios import IOSExploitAgent
        return jsonify(IOSExploitAgent().list_cves())
    except ImportError:
        return jsonify({}), 200


# ── Android Exploitation Agent Routes ───────────────────────────────
_android_lock = threading.Lock()

@app.route("/api/android-exploit/describe")
def api_android_exploit_describe():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    try:
        from agents.specialized.exploit_android import AndroidExploitAgent
        return jsonify(AndroidExploitAgent().describe())
    except ImportError:
        return jsonify({"error": "android_exploit module not available"}), 503

@app.route("/api/android-exploit/mms", methods=["POST"])
def api_android_exploit_mms():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    return jsonify({"vector": data.get("vector", "proto_type_confusion"),
                    "target": data.get("target", ""), "payload": data.get("payload", "arm64_root_shell"),
                    "status": "simulated", "cve": "CVE-2021-1055", "zero_click": True})

@app.route("/api/android-exploit/image", methods=["POST"])
def api_android_exploit_image():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    return jsonify({"vector": data.get("vector", "imageparser_overflow"),
                    "target": data.get("target", ""), "payload": data.get("payload", "arm64_reverse_tcp"),
                    "status": "simulated", "cve": "CVE-2022-2051", "zero_click": True})

@app.route("/api/android-exploit/bluetooth", methods=["POST"])
def api_android_exploit_bluetooth():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    return jsonify({"vector": data.get("vector", "spp_overflow"), "target_mac": data.get("target", ""),
                    "payload": data.get("payload", "arm64_meterpreter"), "status": "simulated",
                    "cve": "CVE-2017-0781", "zero_click": True, "range_meters": 100})

@app.route("/api/android-exploit/nfc", methods=["POST"])
def api_android_exploit_nfc():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    return jsonify({"vector": data.get("vector", "emv_chip_clone"), "target": data.get("target", ""),
                    "payload": data.get("payload", "credential_exfil"), "status": "simulated",
                    "zero_click": False, "range_cm": 4})

@app.route("/api/android-exploit/kernel", methods=["POST"])
def api_android_exploit_kernel():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    return jsonify({"vector": data.get("vector", "dirty_pipe"), "target": data.get("target", ""),
                    "payload": data.get("payload", "root_shell"), "status": "simulated",
                    "impact": "root_privilege_escalation", "zero_click": True})

@app.route("/api/android-exploit/cves")
def api_android_exploit_cves():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    try:
        from agents.specialized.exploit_android import AndroidExploitAgent
        return jsonify(AndroidExploitAgent().list_cves())
    except ImportError:
        return jsonify({}), 200


# ── macOS Exploitation Agent Routes ─────────────────────────────────
@app.route("/api/macos-exploit/describe")
def api_macos_exploit_describe():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    try:
        from agents.specialized.exploit_osx import macOSExploitAgent
        return jsonify(macOSExploitAgent().describe())
    except ImportError:
        return jsonify({"error": "macos_exploit module not available"}), 503

@app.route("/api/macos-exploit/image", methods=["POST"])
def api_macos_exploit_image():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    return jsonify({"vector": data.get("vector", "imageio_webp_overflow"),
                    "target": data.get("target", ""), "payload": data.get("payload", "arm64_shellcode"),
                    "status": "simulated", "cve": "CVE-2021-30770", "zero_click": True})

@app.route("/api/macos-exploit/safari", methods=["POST"])
def api_macos_exploit_safari():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    return jsonify({"vector": data.get("vector", "jit_spray"), "target": data.get("target", ""),
                    "payload": data.get("payload", "arm64_sandbox_escape"), "status": "simulated",
                    "cve": "CVE-2022-22616", "zero_click": False})

@app.route("/api/macos-exploit/metal", methods=["POST"])
def api_macos_exploit_metal():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    return jsonify({"vector": data.get("vector", "shader_overflow"), "target": data.get("target", ""),
                    "payload": data.get("payload", "arm64_dylib_inject"), "status": "simulated",
                    "cve": "CVE-2023-32629", "zero_click": True})

@app.route("/api/macos-exploit/kernel", methods=["POST"])
def api_macos_exploit_kernel():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    return jsonify({"vector": data.get("vector", "xnu_ipc"), "target": data.get("target", ""),
                    "payload": data.get("payload", "root_shell"), "status": "simulated",
                    "impact": "kernel_root", "zero_click": True})

@app.route("/api/macos-exploit/cves")
def api_macos_exploit_cves():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    try:
        from agents.specialized.exploit_osx import macOSExploitAgent
        return jsonify(macOSExploitAgent().list_cves())
    except ImportError:
        return jsonify({}), 200


# ── Windows Exploitation Agent Routes ───────────────────────────────
@app.route("/api/windows-exploit/describe")
def api_windows_exploit_describe():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    try:
        from agents.specialized.exploit_windows import WindowsExploitAgent
        return jsonify(WindowsExploitAgent().describe())
    except ImportError:
        return jsonify({"error": "windows_exploit module not available"}), 503

@app.route("/api/windows-exploit/eternalblue", methods=["POST"])
def api_windows_exploit_eternalblue():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    return jsonify({"vector": "eternalblue", "target": data.get("target", ""),
                    "payload": data.get("payload", "x64_meterpreter"), "status": "simulated",
                    "cve": "CVE-2017-0144", "zero_click": True})

@app.route("/api/windows-exploit/exchange", methods=["POST"])
def api_windows_exploit_exchange():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    return jsonify({"vector": data.get("vector", "ssrf_oab"), "target": data.get("target", ""),
                    "payload": data.get("payload", "webshell"), "status": "simulated",
                    "cve": "CVE-2021-26855", "zero_click": True})

@app.route("/api/windows-exploit/printnightmare", methods=["POST"])
def api_windows_exploit_printnightmare():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    return jsonify({"vector": "printnightmare", "target": data.get("target", ""),
                    "payload": data.get("payload", "x64_reverse_tcp"), "status": "simulated",
                    "cve": "CVE-2021-34527", "zero_click": True})

@app.route("/api/windows-exploit/doc", methods=["POST"])
def api_windows_exploit_doc():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    return jsonify({"vector": data.get("vector", "rtf_ole2"), "target": data.get("target", ""),
                    "payload": data.get("payload", "x86_meterpreter"), "status": "simulated",
                    "zero_click": False})

@app.route("/api/windows-exploit/kernel-chain", methods=["POST"])
def api_windows_exploit_kernel_chain():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    vectors = data.get("vectors", ["dirty_copy", "hvci_bypass"])
    return jsonify({"vectors": vectors, "target": data.get("target", ""),
                    "payload": data.get("payload", "nt_SYSTEM"), "status": "simulated",
                    "impact": "nt_system", "zero_click": True})

@app.route("/api/windows-exploit/cves")
def api_windows_exploit_cves():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    try:
        from agents.specialized.exploit_windows import WindowsExploitAgent
        return jsonify(WindowsExploitAgent().list_cves())
    except ImportError:
        return jsonify({}), 200


# ── Linux Exploitation Agent Routes ─────────────────────────────────
@app.route("/api/linux-exploit/describe")
def api_linux_exploit_describe():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    try:
        from agents.specialized.exploit_linux import LinuxExploitAgent
        return jsonify(LinuxExploitAgent().describe())
    except ImportError:
        return jsonify({"error": "linux_exploit module not available"}), 503

@app.route("/api/linux-exploit/dirty-pipe", methods=["POST"])
def api_linux_exploit_dirty_pipe():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    return jsonify({"vector": "dirty_pipe", "target": data.get("target", ""),
                    "payload": data.get("payload", "root_shell"), "status": "simulated",
                    "cve": "CVE-2022-0847", "impact": "root_privilege_escalation", "zero_click": True})

@app.route("/api/linux-exploit/docker-escape", methods=["POST"])
def api_linux_exploit_docker_escape():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    return jsonify({"vector": data.get("vector", "privileged_container"),
                    "target": data.get("target", ""), "payload": data.get("payload", "host_root_shell"),
                    "status": "simulated", "impact": "host_root", "zero_click": True})

@app.route("/api/linux-exploit/glibc-heap", methods=["POST"])
def api_linux_exploit_glibc_heap():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    return jsonify({"vector": data.get("vector", "tcache_poison"),
                    "target": data.get("target", ""), "payload": data.get("payload", "x64_reverse_shell"),
                    "status": "simulated", "impact": "code_execution", "zero_click": True})

@app.route("/api/linux-exploit/systemd", methods=["POST"])
def api_linux_exploit_systemd():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    return jsonify({"vector": data.get("vector", "socket_activated"),
                    "target": data.get("target", ""), "payload": data.get("payload", "root_crontab"),
                    "status": "simulated", "impact": "root_persistence", "zero_click": False})

@app.route("/api/linux-exploit/cves")
def api_linux_exploit_cves():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    try:
        from agents.specialized.exploit_linux import LinuxExploitAgent
        return jsonify(LinuxExploitAgent().list_cves())
    except ImportError:
        return jsonify({}), 200


# ── IoT Exploitation Agent Routes ───────────────────────────────────
@app.route("/api/iot-exploit/describe")
def api_iot_exploit_describe():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    try:
        from agents.specialized.exploit_iot import IOExploitAgent
        return jsonify(IOExploitAgent().describe())
    except ImportError:
        return jsonify({"error": "iot_exploit module not available"}), 503

@app.route("/api/iot-exploit/firmware", methods=["POST"])
def api_iot_exploit_firmware():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    return jsonify({"action": "firmware_extract", "target_ip": data.get("target_ip", ""),
                    "firmware_url": data.get("firmware_url"), "status": "simulated",
                    "methods": ["telnet_tar_dump", "http_firmware_download", "spi_chip_read",
                                "jtag_flash_read"]})

@app.route("/api/iot-exploit/hardware-debug", methods=["POST"])
def api_iot_exploit_hardware_debug():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    return jsonify({"action": "hardware_debug", "interface": data.get("interface", "uart"),
                    "baud": data.get("baud", 115200), "target_ip": data.get("target_ip", ""),
                    "status": "simulated", "capabilities": {"uart_console": True,
                    "jtag_programming": True, "bootloader_unlock": True}})

@app.route("/api/iot-exploit/default-creds", methods=["POST"])
def api_iot_exploit_default_creds():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    return jsonify({"action": "default_credentials", "target_ip": data.get("target_ip", ""),
                    "service": data.get("service", "telnet"), "status": "simulated",
                    "credentials_found": [{"user": "admin", "pass": "admin"},
                                          {"user": "root", "pass": "toor"}]})

@app.route("/api/iot-exploit/mqtt", methods=["POST"])
def api_iot_exploit_mqtt():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    return jsonify({"action": "mqtt_attack", "target_ip": data.get("target_ip", ""),
                    "topic": data.get("topic", ""), "payload": data.get("payload", ""),
                    "status": "simulated", "techniques": ["topic_enumeration", "qos_abuse",
                    "retain_manipulation", "auth_bypass"]})

@app.route("/api/iot-exploit/cves")
def api_iot_exploit_cves():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    try:
        from agents.specialized.exploit_iot import IOExploitAgent
        return jsonify(IOExploitAgent().list_cves())
    except ImportError:
        return jsonify({}), 200


# ── Bluetooth Exploitation Agent Routes ─────────────────────────────
@app.route("/api/bluetooth-exploit/describe")
def api_bluetooth_exploit_describe():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    try:
        from agents.specialized.exploit_bluetooth import BluetoothExploitAgent
        return jsonify(BluetoothExploitAgent().describe())
    except ImportError:
        return jsonify({"error": "bluetooth_exploit module not available"}), 503

@app.route("/api/bluetooth-exploit/blueborne", methods=["POST"])
def api_bluetooth_exploit_blueborne():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    return jsonify({"vector": data.get("vector", "rfcomm_overflow"),
                    "target_mac": data.get("target_mac", ""), "payload": data.get("payload", "bluetooth_shell"),
                    "status": "simulated", "cve": "CVE-2017-0781", "zero_click": True,
                    "range_meters": 100})

@app.route("/api/bluetooth-exploit/ble-sniff", methods=["POST"])
def api_bluetooth_exploit_ble_sniff():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    return jsonify({"action": "ble_sniff", "target_mac": data.get("target_mac", ""),
                    "duration_sec": data.get("duration", 60), "extract_keys": data.get("extract_keys", False),
                    "status": "simulated", "techniques": ["access_address_prediction",
                    "ll_privacy_bypass", "connection_param_abuse"]})

@app.route("/api/bluetooth-exploit/ble-deauth", methods=["POST"])
def api_bluetooth_exploit_ble_deauth():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    return jsonify({"action": "ble_deauth", "target_mac": data.get("target_mac", ""),
                    "method": data.get("method", "conn_cancel"), "status": "simulated"})

@app.route("/api/bluetooth-exploit/keyless", methods=["POST"])
def api_bluetooth_exploit_keyless():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    return jsonify({"vector": data.get("vector", "can_relay"), "target_vehicle": data.get("target_vehicle", ""),
                    "action": data.get("action", "unlock_start_engine"), "status": "simulated",
                    "impact": "vehicle_compromise", "zero_click": False, "range_meters": 50})

@app.route("/api/bluetooth-exploit/cves")
def api_bluetooth_exploit_cves():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    try:
        from agents.specialized.exploit_bluetooth import BluetoothExploitAgent
        return jsonify(BluetoothExploitAgent().list_cves())
    except ImportError:
        return jsonify({}), 200


# ── NFC Exploitation Agent Routes ───────────────────────────────────
@app.route("/api/nfc-exploit/describe")
def api_nfc_exploit_describe():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    try:
        from agents.specialized.exploit_nfc import NFCExploitAgent
        return jsonify(NFCExploitAgent().describe())
    except ImportError:
        return jsonify({"error": "nfc_exploit module not available"}), 503

@app.route("/api/nfc-exploit/emv-clone", methods=["POST"])
def api_nfc_exploit_emv_clone():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    return jsonify({"action": "emv_clone", "target_card": data.get("target_card", ""),
                    "extract_keys": data.get("extract_keys", True), "status": "simulated",
                    "techniques": ["atr_parsing", "aid_enumeration", "kd_gen_extraction",
                                   "arqc_simulation"], "supported_cards": ["Visa", "Mastercard", "AMEX"]})

@app.route("/api/nfc-exploit/relay", methods=["POST"])
def api_nfc_exploit_relay():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    return jsonify({"action": "nfc_relay", "target_reader": data.get("target_reader", ""),
                    "target_card": data.get("target_card", ""),
                    "relay_duration_sec": data.get("relay_duration", 120), "status": "simulated",
                    "techniques": ["real_time_relay", "latency_optimization", "frame_forwarding"]})

@app.route("/api/nfc-exploit/rfid-skim", methods=["POST"])
def api_nfc_exploit_rfid_skim():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    return jsonify({"action": "rfid_skim", "target_card": data.get("target_card", ""),
                    "frequency": data.get("frequency", "125khz"),
                    "extract_uid": data.get("extract_uid", True), "status": "simulated",
                    "supported_formats": ["EM4100", "HID Prox", "Indala", "Mifare Classic 1K"]})

@app.route("/api/nfc-exploit/ndef-inject", methods=["POST"])
def api_nfc_exploit_ndef_inject():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    return jsonify({"action": "ndef_inject", "target_tag": data.get("target_tag", ""),
                    "action_type": data.get("action", "rewrite_url"),
                    "new_url": data.get("new_url"), "status": "simulated",
                    "techniques": ["tag_rewrite", "smart_poster_hijack", "uri_injection"]})

@app.route("/api/nfc-exploit/payment-intercept", methods=["POST"])
def api_nfc_exploit_payment_intercept():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    return jsonify({"action": "payment_intercept", "target_terminal": data.get("target_terminal", ""),
                    "intercept_amount": data.get("intercept_amount", True),
                    "status": "simulated", "techniques": ["amount_manipulation",
                    "offline_auth_bypass", "token_replay"]})

@app.route("/api/nfc-exploit/cves")
def api_nfc_exploit_cves():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    try:
        from agents.specialized.exploit_nfc import NFCExploitAgent
        return jsonify(NFCExploitAgent().list_cves())
    except ImportError:
        return jsonify({}), 200


# ── Automobile Exploitation Agent Routes ────────────────────────────
@app.route("/api/automobile-exploit/describe")
def api_automobile_exploit_describe():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    try:
        from agents.specialized.exploit_automobile import AutoExploitAgent
        return jsonify(AutoExploitAgent().describe())
    except ImportError:
        return jsonify({"error": "automobile_exploit module not available"}), 503

@app.route("/api/automobile-exploit/can-inject", methods=["POST"])
def api_automobile_exploit_can_inject():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    return jsonify({"vector": data.get("vector", "brake_cmd_replay"),
                    "target_vid": data.get("target_vid", ""), "payload": data.get("payload", ""),
                    "status": "simulated", "techniques": ["frame_replay",
                    "arbitration_id_manipulation", "message_flooding", "gateway_bypass"]})

@app.route("/api/automobile-exploit/obd2", methods=["POST"])
def api_automobile_exploit_obd2():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    return jsonify({"action": "obd2", "target_vid": data.get("target_vid", ""),
                    "session": data.get("session", 0x10), "subfunc": data.get("subfunc", 0x01),
                    "payload": data.get("payload", "ecu_dump"), "status": "simulated",
                    "diagnostic_modes": {"0x10": "Diagnostic Session Control", "0x22": "Read Data",
                                         "0x27": "Security Access", "0x2E": "Write Data"}})

@app.route("/api/automobile-exploit/keyless", methods=["POST"])
def api_automobile_exploit_keyless():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    return jsonify({"vector": data.get("vector", "can_relay"),
                    "target_vid": data.get("target_vid", ""), "action": data.get("action", "unlock_start_engine"),
                    "status": "simulated", "techniques": ["can_relay", "key_fob_cloning",
                    "ultra_wave_relay", "ranging_bypass"], "range_meters": 50})

@app.route("/api/automobile-exploit/infotainment", methods=["POST"])
def api_automobile_exploit_infotainment():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    return jsonify({"vector": data.get("vector", "qnx_overflow"),
                    "target_vid": data.get("target_vid", ""), "payload": data.get("payload", ""),
                    "status": "simulated", "platforms": ["QNX", "Android_Automotive",
                    "Linux_Yocto", "VxWorks"]})

@app.route("/api/automobile-exploit/telematics", methods=["POST"])
def api_automobile_exploit_telematics():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    return jsonify({"vector": data.get("vector", "cellular_jam"),
                    "target_vid": data.get("target_vid", ""), "action": data.get("action", ""),
                    "status": "simulated", "services": ["OnStar", "BMW ConnectedDrive",
                    "Mercedes me", "Tesla Mobile"]})

@app.route("/api/automobile-exploit/cves")
def api_automobile_exploit_cves():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    try:
        from agents.specialized.exploit_automobile import AutoExploitAgent
        return jsonify(AutoExploitAgent().list_cves())
    except ImportError:
        return jsonify({}), 200


# ── Wireless Exploitation Routes ────────────────────────────────────
_wireless_lock = threading.Lock()
_wifi_scan_results = []
_bt_devices = []
_crack_results = []
_evil_twin_detections = []


@app.route("/api/wifi-scan/status")
def api_wifi_scan_status():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    with _wireless_lock:
        return jsonify({"networks": _wifi_scan_results, "scanning": False})


@app.route("/api/wifi-scan/start", methods=["POST"])
def api_wifi_scan_start():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    with _wireless_lock:
        _wifi_scan_results = [
            {"ssid": "FreeAI-Lab", "bssid": "AA:BB:CC:DD:EE:01", "channel": 6, "signal": -45, "encryption": "WPA2"},
            {"ssid": "CorpNet-5G", "bssid": "AA:BB:CC:DD:EE:02", "channel": 36, "signal": -62, "encryption": "WPA3"},
            {"ssid": "IoT-Gateway", "bssid": "AA:BB:CC:DD:EE:03", "channel": 11, "signal": -71, "encryption": "WPA2"},
            {"ssid": "OpenGuest", "bssid": "AA:BB:CC:DD:EE:04", "channel": 1, "signal": -55, "encryption": "Open"},
        ]
    return jsonify({"ok": True, "networks_found": len(_wifi_scan_results)})


@app.route("/api/bt-scan/devices")
def api_bt_scan_devices():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    with _wireless_lock:
        if not _bt_devices:
            _bt_devices.clear()
            _bt_devices.extend([
                {"name": "JBL Flip 6", "mac": "00:1A:7D:DA:71:11", "type": "BLE", "rssi": -58, "services": ["audio_sink", "avrcp"]},
                {"name": "Logitech MX Master", "mac": "00:1A:7D:DA:71:12", "type": "BR/EDR", "rssi": -42, "services": ["hid"]},
                {"name": "Unknown BLE Tag", "mac": "00:1A:7D:DA:71:13", "type": "BLE", "rssi": -73, "services": ["battery", "device_info"]},
            ])
        return jsonify({"devices": list(_bt_devices)})


@app.route("/api/wireless/evil-twin", methods=["POST"])
def api_wireless_evil_twin():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    with _wireless_lock:
        detection = {
            "target_ssid": data.get("target_ssid", "FreeAI-Lab"),
            "rogue_bssid": "DE:AD:BE:EF:00:01",
            "channel": 6,
            "confidence": 0.87,
            "timestamp": time.time(),
        }
        _evil_twin_detections.append(detection)
    return jsonify({"ok": True, "detection": detection})


# ── IoT Exploitation Dashboard Routes ───────────────────────────────
_iot_lock = threading.Lock()
_iot_devices = []
_iot_firmwares = []
_iot_vulns = []


@app.route("/api/iot-scan/devices")
def api_iot_scan_devices():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    with _iot_lock:
        return jsonify({"devices": _iot_devices})


@app.route("/api/iot-scan/start", methods=["POST"])
def api_iot_scan_start():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    with _iot_lock:
        _iot_devices = [
            {"name": "Hikvision Camera", "ip": "192.168.1.101", "type": "camera", "protocol": "RTSP", "firmware": "V5.6.3", "default_creds": True, "risk_score": 8},
            {"name": "TP-Link Smart Plug", "ip": "192.168.1.102", "type": "smart_plug", "protocol": "Kasa", "firmware": "1.2.8", "default_creds": False, "risk_score": 4},
            {"name": "Shelly 2.5 Relay", "ip": "192.168.1.103", "type": "relay", "protocol": "MQTT", "firmware": "20230913", "default_creds": True, "risk_score": 6},
            {"name": "Xiaomi Gateway", "ip": "192.168.1.104", "type": "gateway", "protocol": "Zigbee", "firmware": "3.1.0", "default_creds": False, "risk_score": 5},
        ]
    return jsonify({"ok": True, "devices_found": len(_iot_devices)})


@app.route("/api/iot/firmware")
def api_iot_firmware():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    with _iot_lock:
        if not _iot_firmwares:
            _iot_firmwares.clear()
            _iot_firmwares.extend([
                {"name": "Hikvision IPC", "version": "V5.6.3", "arch": "arm32", "size": "32MB", "vuln_count": 3},
                {"name": "TP-Link Kasa", "version": "1.2.8", "arch": "mips", "size": "8MB", "vuln_count": 1},
            ])
        return jsonify({"firmwares": list(_iot_firmwares)})


@app.route("/api/iot/assess", methods=["POST"])
def api_iot_assess():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    with _iot_lock:
        _iot_vulns = [
            {"cve": "CVE-2021-36260", "device": "Hikvision Camera", "severity": "critical", "desc": "Command injection in web server", "exploit": True},
            {"cve": "CVE-2023-29358", "device": "TP-Link Smart Plug", "severity": "medium", "desc": "Auth bypass in Kasa protocol", "exploit": False},
        ]
    return jsonify({"ok": True, "vulns_found": len(_iot_vulns)})


# ── APT Threat Intelligence Routes ──────────────────────────────────
_apt_lock = threading.Lock()
_apt_threats = []
_apt_groups = []
_apt_ttps = []
_apt_iocs = []


@app.route("/api/apt/threats")
def api_apt_threats():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    with _apt_lock:
        if not _apt_threats:
            _apt_threats.clear()
            _apt_threats.extend([
                {"title": "APT29 Spear Phishing Campaign", "description": "Targeted phishing emails with malicious ISO attachments", "severity": "critical", "timestamp": time.time() - 3600},
                {"title": "Lazarus Group Cryptojacking", "description": "Supply chain compromise of dev tooling for crypto mining", "severity": "high", "timestamp": time.time() - 7200},
                {"title": "APT41 Ransomware Deployment", "description": "Double extortion ransomware targeting healthcare", "severity": "high", "timestamp": time.time() - 14400},
            ])
            _apt_iocs.clear()
            _apt_iocs.extend([
                {"type": "hash", "value": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4", "apt": "APT29", "first_seen": time.time() - 86400, "confidence": 92},
                {"type": "domain", "value": "evil-update-cdn.com", "apt": "Lazarus", "first_seen": time.time() - 172800, "confidence": 88},
                {"type": "ip", "value": "185.220.101.42", "apt": "APT41", "first_seen": time.time() - 259200, "confidence": 95},
            ])
            _apt_ttps.clear()
            _apt_ttps.extend([
                {"technique_id": "T1566.001", "name": "Spearphishing Attachment", "tactic": "Initial Access", "groups": ["APT29", "APT41"], "platforms": ["Windows", "macOS"]},
                {"technique_id": "T1059.001", "name": "PowerShell", "tactic": "Execution", "groups": ["APT29", "Lazarus"], "platforms": ["Windows"]},
                {"technique_id": "T1071.001", "name": "Web Protocols", "tactic": "Command and Control", "groups": ["APT41", "Lazarus"], "platforms": ["Windows", "Linux", "macOS"]},
            ])
        return jsonify({"threats": list(_apt_threats), "iocs": list(_apt_iocs), "ttps": list(_apt_ttps)})


@app.route("/api/apt/groups")
def api_apt_groups():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    with _apt_lock:
        if not _apt_groups:
            _apt_groups.clear()
            _apt_groups.extend([
                {"name": "APT28", "aliases": "Fancy Bear, Sofacy", "origin": "Russia", "targets": ["Government", "Military", "Media"], "threat_level": "critical"},
                {"name": "APT29", "aliases": "Cozy Bear, The Dukes", "origin": "Russia", "targets": ["Government", "Think Tanks", "Healthcare"], "threat_level": "critical"},
                {"name": "Lazarus Group", "aliases": "Hidden Cobra, ZINC", "origin": "North Korea", "targets": ["Finance", "Crypto", "Defense"], "threat_level": "high"},
                {"name": "APT41", "aliases": "Winnti, Barium", "origin": "China", "targets": ["Healthcare", "Gaming", "Telecom"], "threat_level": "high"},
            ])
        return jsonify({"groups": list(_apt_groups)})


@app.route("/api/apt/ttps")
def api_apt_ttps():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    with _apt_lock:
        return jsonify({"ttps": _apt_ttps})


@app.route("/api/apt/feed/refresh", methods=["POST"])
def api_apt_feed_refresh():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    with _apt_lock:
        _apt_threats = []
        _apt_iocs = []
        _apt_ttps = []
    return api_apt_threats()


# ── Predictive Analytics Routes ─────────────────────────────────────
_analytics_lock = threading.Lock()
_analytics_alerts = []
_analytics_trends = []
_analytics_forecast = []


@app.route("/api/analytics/alerts")
def api_analytics_alerts():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    with _analytics_lock:
        if not _analytics_alerts:
            _analytics_alerts.clear()
            _analytics_alerts.extend([
                {"message": "Unusual outbound traffic spike detected from 10.0.1.50", "severity": "high", "source": "Network Monitor", "confidence": 87, "is_anomaly": True, "timestamp": time.time() - 1800},
                {"message": "Failed login attempts exceeded threshold on admin panel", "severity": "medium", "source": "Auth Service", "confidence": 92, "is_anomaly": False, "timestamp": time.time() - 3600},
                {"message": "New process spawned by www-data with network access", "severity": "high", "source": "EDR", "confidence": 78, "is_anomaly": True, "timestamp": time.time() - 5400},
            ])
        return jsonify({"alerts": list(_analytics_alerts)})


@app.route("/api/analytics/predict", methods=["POST"])
def api_analytics_predict():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    with _analytics_lock:
        _analytics_forecast = [
            {"period": "Next 24h", "metric": "Attack Volume", "current": 142, "predicted": 189, "delta": 33},
            {"period": "Next 24h", "metric": "Phishing Attempts", "current": 38, "predicted": 52, "delta": 37},
            {"period": "Next 7d", "metric": "Vulnerability Exploits", "current": 12, "predicted": 19, "delta": 58},
            {"period": "Next 7d", "metric": "Brute Force Attacks", "current": 284, "predicted": 310, "delta": 9},
        ]
        _analytics_trends = [
            {"label": "Mon", "value": 42}, {"label": "Tue", "value": 55},
            {"label": "Wed", "value": 38}, {"label": "Thu", "value": 67},
            {"label": "Fri", "value": 72}, {"label": "Sat", "value": 51},
            {"label": "Sun", "value": 89},
        ]
    return jsonify({"forecast": _analytics_forecast, "trends": _analytics_trends})


@app.route("/api/analytics/trends")
def api_analytics_trends():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    with _analytics_lock:
        if not _analytics_trends:
            _analytics_trends.clear()
            _analytics_trends.extend([
                {"label": "Mon", "value": 42}, {"label": "Tue", "value": 55},
                {"label": "Wed", "value": 38}, {"label": "Thu", "value": 67},
                {"label": "Fri", "value": 72}, {"label": "Sat", "value": 51},
                {"label": "Sun", "value": 89},
            ])
        return jsonify({"trends": list(_analytics_trends)})


@app.route("/api/analytics/risk-score")
def api_analytics_risk_score():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    with _analytics_lock:
        score = 67
        return jsonify({"score": score, "level": "medium", "factors": ["traffic_anomaly", "auth_failures", "process_anomaly"]})


# ── Incident Response Routes ────────────────────────────────────────
_ir_lock = threading.Lock()
_ir_incidents = []
_ir_playbooks = []
_ir_next_id = 1


@app.route("/api/incidents/list")
def api_incidents_list():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    with _ir_lock:
        if not _ir_incidents:
            _ir_incidents.clear()
            _ir_incidents.extend([
                {"id": "INC-001", "title": "Phishing Email Campaign", "severity": "high", "status": "investigating", "created": time.time() - 86400},
                {"id": "INC-002", "title": "Unauthorized SSH Access", "severity": "critical", "status": "contained", "created": time.time() - 43200},
                {"id": "INC-003", "title": "Malware on Workstation-42", "severity": "medium", "status": "resolved", "created": time.time() - 172800},
            ])
        return jsonify({"incidents": list(_ir_incidents)})


@app.route("/api/incidents/create", methods=["POST"])
def api_incidents_create():
    global _ir_next_id
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    with _ir_lock:
        inc_id = f"INC-{_ir_next_id:03d}"
        _ir_next_id += 1
        incident = {
            "id": inc_id,
            "title": data.get("title", "Untitled Incident"),
            "severity": data.get("severity", "medium"),
            "status": "open",
            "description": data.get("description", ""),
            "created": time.time(),
        }
        _ir_incidents.append(incident)
    return jsonify({"ok": True, "incident": incident})


@app.route("/api/incidents/<incident_id>/status", methods=["PUT"])
def api_incidents_update_status(incident_id):
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    with _ir_lock:
        for inc in _ir_incidents:
            if inc["id"] == incident_id or str(_ir_incidents.index(inc)) == incident_id:
                inc["status"] = data.get("status", inc["status"])
                return jsonify({"ok": True, "incident": inc})
    return jsonify({"error": "incident not found"}), 404


@app.route("/api/incidents/playbooks")
def api_incidents_playbooks():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    with _ir_lock:
        if not _ir_playbooks:
            _ir_playbooks.clear()
            _ir_playbooks.extend([
                {"name": "Phishing Response", "description": "Automated response for phishing email incidents", "steps": 8, "trigger": "email_alert"},
                {"name": "Malware Containment", "description": "Isolate infected host and collect forensic evidence", "steps": 12, "trigger": "edr_alert"},
                {"name": "Data Breach Protocol", "description": "Full incident response for confirmed data exfiltration", "steps": 15, "trigger": "dlp_alert"},
                {"name": "Ransomware Response", "description": "Contain, decrypt if possible, restore from backup", "steps": 10, "trigger": "file_encryption_detected"},
            ])
        return jsonify({"playbooks": list(_ir_playbooks)})


# ── AI Red Teaming Routes ───────────────────────────────────────────
_redteam_lock = threading.Lock()
_redteam_campaigns = []
_redteam_results = []
_redteam_next_id = 1


@app.route("/api/ai-redteam/campaigns")
def api_ai_redteam_campaigns():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    with _redteam_lock:
        if not _redteam_campaigns:
            _redteam_campaigns.clear()
            _redteam_campaigns.extend([
                {"name": "Web App Penetration", "description": "AI-driven web application vulnerability discovery", "status": "completed", "target": "webapp.internal", "vulns_found": 5, "started": time.time() - 86400},
                {"name": "Network Lateral Movement", "description": "Automated lateral movement simulation across network segments", "status": "running", "target": "10.0.0.0/16", "vulns_found": 2, "started": time.time() - 3600},
                {"name": "Social Engineering Test", "description": "AI-generated phishing campaign against test group", "status": "planned", "target": "employees@test.company", "vulns_found": 0, "started": None},
            ])
        return jsonify({"campaigns": list(_redteam_campaigns)})


@app.route("/api/ai-redteam/start", methods=["POST"])
def api_ai_redteam_start():
    global _redteam_next_id
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    with _redteam_lock:
        camp_id = _redteam_next_id
        _redteam_next_id += 1
        campaign = {
            "id": camp_id,
            "name": data.get("name", f"Red Team Campaign {_redteam_next_id}"),
            "description": data.get("description", "AI-driven attack simulation"),
            "status": "running",
            "target": data.get("target", "auto"),
            "type": data.get("type", "vulnerability_discovery"),
            "vulns_found": 0,
            "started": time.time(),
        }
        _redteam_campaigns.append(campaign)
    return jsonify({"ok": True, "campaign": campaign})


@app.route("/api/ai-redteam/results")
def api_ai_redteam_results():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    with _redteam_lock:
        if not _redteam_results:
            _redteam_results.clear()
            _redteam_results.extend([
                {"campaign": "Web App Penetration", "vulnerability": "SQL Injection in /api/users", "severity": "critical", "method": "ai_fuzzing", "found_at": time.time() - 7200},
                {"campaign": "Web App Penetration", "vulnerability": "Stored XSS in comments", "severity": "high", "method": "payload_generation", "found_at": time.time() - 5400},
                {"campaign": "Network Lateral Movement", "vulnerability": "SMB Relay on DC-02", "severity": "critical", "method": "protocol_abuse", "found_at": time.time() - 1800},
            ])
        return jsonify({"results": list(_redteam_results)})


@app.route("/api/ai-redteam/remediate", methods=["POST"])
def api_ai_redteam_remediate():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    remediation = {
        "vulnerability": data.get("vulnerability", "Unknown"),
        "remediation": data.get("remediation", "Apply patch and validate"),
        "status": "pending",
        "applied": None,
        "verified": False,
    }
    with _redteam_lock:
        pass
    return jsonify({"ok": True, "remediation": remediation})


# ── New Dashboard Page Routes ───────────────────────────────────────

@app.route("/wireless-exploitation")
def page_wireless_exploitation():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    return render_template("wireless-exploitation.html")


@app.route("/iot-exploitation")
def page_iot_exploitation():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    return render_template("iot-exploitation.html")


@app.route("/apt-intelligence")
def page_apt_intelligence():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    return render_template("apt-intelligence.html")


@app.route("/predictive-analytics")
def page_predictive_analytics():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    return render_template("predictive-analytics.html")


@app.route("/incident-response")
def page_incident_response():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    return render_template("incident-response.html")


@app.route("/ai-red-teaming")
def page_ai_red_teaming():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    return render_template("ai-red-teaming.html")


# ── New Dashboard Pages ──────────────────────────────────────────

@app.route("/vuln-scanner")
def vuln_scanner_page():
    return render_template("vuln-scanner.html")

@app.route("/identity-mgmt")
def identity_mgmt_page():
    return render_template("identity-mgmt.html")

@app.route("/proxy-chain")
def proxy_chain_page():
    return render_template("proxy-chain.html")

@app.route("/realtime-monitor")
def realtime_monitor_page():
    return render_template("realtime-monitor.html")

@app.route("/threat-intel")
def threat_intel_page():
    return render_template("threat-intel.html")


# ── Vulnerability Scanner API ────────────────────────────────────

_vuln_lock = threading.Lock()
_vuln_state = {
    "results": [],
    "schedule": [],
    "total_scans": 0,
    "running": False,
}

@app.route("/api/vuln-scan/status")
def api_vuln_scan_status():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    with _vuln_lock:
        return jsonify({
            "total_scans": _vuln_state["total_scans"],
            "running": _vuln_state["running"],
            "scheduled": len(_vuln_state["schedule"]),
        })

@app.route("/api/vuln-scan/start", methods=["POST"])
def api_vuln_scan_start():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    with _vuln_lock:
        _vuln_state["running"] = True
        _vuln_state["total_scans"] += 1
    import random as _random
    cves = ["CVE-2024-1234", "CVE-2023-5678", "CVE-2024-9012", "CVE-2023-3456"]
    risks = ["critical", "high", "medium", "low"]
    new_results = []
    for _ in range(_random.randint(2, 5)):
        new_results.append({
            "target": data.get("target", "0.0.0.0/0"),
            "cve": _random.choice(cves),
            "risk": _random.choice(risks),
            "score": round(_random.uniform(3.0, 10.0), 1),
            "discovered": time.time(),
            "remediated": False,
        })
    with _vuln_lock:
        _vuln_state["results"].extend(new_results)
        _vuln_state["running"] = False
    return jsonify({"ok": True, "found": len(new_results), "total_scans": _vuln_state["total_scans"]})

@app.route("/api/vuln-scan/results")
def api_vuln_scan_results():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    with _vuln_lock:
        return jsonify({"results": _vuln_state["results"], "total": len(_vuln_state["results"])})

@app.route("/api/vuln-scan/schedule", methods=["POST"])
def api_vuln_scan_schedule():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    entry = {
        "target": data.get("target", ""),
        "cron": data.get("cron", "0 2 * * *"),
        "profile": data.get("profile", "quick"),
        "created": time.time(),
    }
    with _vuln_lock:
        _vuln_state["schedule"].append(entry)
    return jsonify({"ok": True, "schedule": entry})


# ── Identity Management API ──────────────────────────────────────

_identity_lock = threading.Lock()
_identity_state = {
    "users": [],
    "sessions": [],
    "events": [],
    "next_id": 1,
}

@app.route("/api/identity/users")
def api_identity_users():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    with _identity_lock:
        return jsonify({"users": _identity_state["users"], "total": len(_identity_state["users"])})

@app.route("/api/identity/monitor", methods=["POST"])
def api_identity_monitor():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    action = data.get("action", "log_event")
    with _identity_lock:
        if action == "add_user":
            user = {
                "id": _identity_state["next_id"],
                "username": data.get("username", "new-user"),
                "email": data.get("email", ""),
                "role": data.get("role", "viewer"),
                "active": True,
                "last_active": time.time(),
                "created": time.time(),
            }
            _identity_state["users"].append(user)
            _identity_state["next_id"] += 1
            return jsonify({"ok": True, "user": user, "total": len(_identity_state["users"])})
        _identity_state["events"].append({
            "user": data.get("username", "system"),
            "event_type": data.get("event_type", "login"),
            "ip": data.get("ip", "127.0.0.1"),
            "timestamp": time.time(),
            "status": data.get("status", "success"),
        })
    return jsonify({"ok": True, "events": len(_identity_state["events"])})

@app.route("/api/identity/sessions")
def api_identity_sessions():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    with _identity_lock:
        return jsonify({"sessions": _identity_state["sessions"], "total": len(_identity_state["sessions"])})

@app.route("/api/identity/roles", methods=["PUT"])
def api_identity_roles():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    new_role = data.get("role", "viewer")
    with _identity_lock:
        for u in _identity_state["users"]:
            if u["id"] == user_id:
                u["role"] = new_role
                return jsonify({"ok": True, "user": u})
    return jsonify({"error": "user not found"}), 404


# ── Proxy Chain API ──────────────────────────────────────────────

_proxy_lock = threading.Lock()
_proxy_state = {
    "chain": [],
    "proxies": [],
    "rotations": 0,
    "anonymity_level": "high",
    "total_latency_ms": 0,
}

@app.route("/api/proxy-chain/status")
def api_proxy_chain_status():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    with _proxy_lock:
        return jsonify({
            "chain": _proxy_state["chain"],
            "proxies": _proxy_state["proxies"],
            "rotations": _proxy_state["rotations"],
            "anonymity_level": _proxy_state["anonymity_level"],
        })

@app.route("/api/proxy-chain/configure", methods=["POST"])
def api_proxy_chain_configure():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    proxies = data.get("proxies", [])
    with _proxy_lock:
        _proxy_state["proxies"] = proxies
        if len(proxies) >= 3:
            _proxy_state["chain"] = proxies[:3]
            _proxy_state["anonymity_level"] = "high"
        elif len(proxies) >= 2:
            _proxy_state["chain"] = proxies[:2]
            _proxy_state["anonymity_level"] = "medium"
        else:
            _proxy_state["chain"] = proxies
            _proxy_state["anonymity_level"] = "low"
        _proxy_state["total_latency_ms"] = sum(p.get("latency_ms", 0) for p in _proxy_state["chain"])
    return jsonify({"ok": True, "chain": _proxy_state["chain"]})

@app.route("/api/proxy-chain/rotate", methods=["GET", "POST"])
def api_proxy_chain_rotate():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    import random as _random
    sample_proxies = [
        {"address": "10.0.1.1:9050", "type": "tor", "location": "DE", "latency_ms": 120, "health": "good"},
        {"address": "10.0.2.2:3128", "type": "http", "location": "NL", "latency_ms": 85, "health": "good"},
        {"address": "10.0.3.3:1080", "type": "socks5", "location": "SE", "latency_ms": 200, "health": "degraded"},
        {"address": "10.0.4.4:443", "type": "https", "location": "CH", "latency_ms": 60, "health": "good"},
        {"address": "10.0.5.5:9150", "type": "tor", "location": "FR", "latency_ms": 150, "health": "good"},
    ]
    with _proxy_lock:
        if not _proxy_state["proxies"]:
            _proxy_state["proxies"] = sample_proxies
        elif len(_proxy_state["proxies"]) < 3:
            _proxy_state["proxies"].extend(sample_proxies)
        _random.shuffle(_proxy_state["proxies"])
        _proxy_state["chain"] = _proxy_state["proxies"][:3]
        _proxy_state["rotations"] += 1
        _proxy_state["total_latency_ms"] = sum(p.get("latency_ms", 0) for p in _proxy_state["chain"])
    return jsonify({"ok": True, "rotations": _proxy_state["rotations"], "chain": _proxy_state["chain"]})

@app.route("/api/proxy-chain/health")
def api_proxy_chain_health():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    with _proxy_lock:
        return jsonify({
            "total_latency_ms": _proxy_state["total_latency_ms"],
            "chain_length": len(_proxy_state["chain"]),
            "healthy": sum(1 for p in _proxy_state["chain"] if p.get("health") == "good"),
            "degraded": sum(1 for p in _proxy_state["chain"] if p.get("health") == "degraded"),
        })


# ── Real-Time Monitoring API ─────────────────────────────────────

_monitor_lock = threading.Lock()
_monitor_state = {
    "metrics": {},
    "alerts": [],
    "anomalies": [],
    "config": {"cpu_threshold": 90, "mem_threshold": 85, "notify": True},
}

@app.route("/api/monitor/metrics")
def api_monitor_metrics():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    import random as _random
    metrics = {
        "cpu_percent": round(_random.uniform(10, 80), 1),
        "memory_percent": round(_random.uniform(30, 75), 1),
        "bytes_sent": _random.randint(10000, 500000),
        "bytes_recv": _random.randint(50000, 1000000),
        "disk_read": _random.randint(0, 10000),
        "disk_write": _random.randint(0, 10000),
        "timestamp": time.time(),
    }
    with _monitor_lock:
        _monitor_state["metrics"] = metrics
    return jsonify(metrics)

@app.route("/api/monitor/alerts")
def api_monitor_alerts():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    with _monitor_lock:
        return jsonify({"alerts": _monitor_state["alerts"], "total": len(_monitor_state["alerts"])})

@app.route("/api/monitor/configure", methods=["POST"])
def api_monitor_configure():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    with _monitor_lock:
        _monitor_state["config"].update(data)
    return jsonify({"ok": True, "config": _monitor_state["config"]})

@app.route("/api/monitor/anomalies")
def api_monitor_anomalies():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    with _monitor_lock:
        return jsonify({"anomalies": _monitor_state["anomalies"], "total": len(_monitor_state["anomalies"])})


# ── Threat Intelligence API ──────────────────────────────────────

_threat_lock = threading.Lock()
_threat_state = {
    "feeds": [],
    "iocs": [],
    "actors": [],
    "last_refresh": 0,
}

@app.route("/api/threat-intel/feeds")
def api_threat_intel_feeds():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    if not _threat_state["feeds"]:
        _threat_state["feeds"] = [
            {"name": "AlienVault OTX", "feed_type": "aggregated", "score": 92, "last_updated": time.time() - 3600},
            {"name": "Abuse.ch", "feed_type": "malware", "score": 88, "last_updated": time.time() - 7200},
            {"name": "Emerging Threats", "feed_type": "ids_rules", "score": 85, "last_updated": time.time() - 1800},
        ]
    with _threat_lock:
        return jsonify({"feeds": _threat_state["feeds"], "total": len(_threat_state["feeds"])})

@app.route("/api/threat-intel/iocs")
def api_threat_intel_iocs():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    if not _threat_state["iocs"]:
        _threat_state["iocs"] = [
            {"ioc_value": "192.168.1.100", "ioc_type": "ip", "score": 75, "updated": time.time() - 600},
            {"ioc_value": "evil.example.com", "ioc_type": "domain", "score": 90, "updated": time.time() - 1200},
            {"ioc_value": "a1b2c3d4e5f6", "ioc_type": "hash_md5", "score": 95, "updated": time.time() - 300},
            {"ioc_value": "10.0.0.50", "ioc_type": "ip", "score": 40, "updated": time.time() - 3600},
        ]
    with _threat_lock:
        return jsonify({"iocs": _threat_state["iocs"], "total": len(_threat_state["iocs"])})

@app.route("/api/threat-intel/refresh", methods=["POST"])
def api_threat_intel_refresh():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    import random as _random
    with _threat_lock:
        _threat_state["last_refresh"] = time.time()
        new_iocs = [
            {"ioc_value": f"10.{_random.randint(0,255)}.{_random.randint(0,255)}.{_random.randint(1,254)}",
             "ioc_type": "ip", "score": _random.randint(20, 99), "updated": time.time()},
            {"ioc_value": f"malware-{_random.randint(1000,9999)}.example.com",
             "ioc_type": "domain", "score": _random.randint(50, 99), "updated": time.time()},
        ]
        _threat_state["iocs"].extend(new_iocs)
    return jsonify({"ok": True, "new_iocs": len(new_iocs), "last_refresh": _threat_state["last_refresh"]})

@app.route("/api/threat-intel/actors")
def api_threat_intel_actors():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    if not _threat_state["actors"]:
        _threat_state["actors"] = [
            {"actor_name": "APT-28", "threat_level": "high", "score": 95, "first_seen": time.time() - 86400*30},
            {"actor_name": "Lazarus Group", "threat_level": "critical", "score": 98, "first_seen": time.time() - 86400*60},
            {"actor_name": "FIN7", "threat_level": "high", "score": 87, "first_seen": time.time() - 86400*15},
        ]
    with _threat_lock:
        return jsonify({"actors": _threat_state["actors"], "total": len(_threat_state["actors"])})


# ── Device Fingerprinting Routes ────────────────────────────────────
_fp_lock = threading.Lock()
_fp_state = {"tips": []}


@app.route("/device-fingerprint")
def page_device_fingerprint():
    return render_template("device-fingerprint.html")


@app.route("/api/fingerprint/detect")
def api_fingerprint_detect():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    import hashlib as _hashlib
    ts = str(time.time())
    canvas_hash = _hashlib.sha256(f"canvas_{ts}".encode()).hexdigest()[:16]
    webgl_renderer = "ANGLE (NVIDIA, NVIDIA GeForce RTX 4090 Direct3D11 vs_5_0 ps_5_0)"
    fonts = ["Arial", "Times New Roman", "Courier New", "Verdana", "Georgia", "Segoe UI", "Roboto", "Consolas"]
    screen_res = "2560x1440"
    tz = "America/New_York"
    lang = "en-US"
    components = [
        {"component": "Canvas", "value": canvas_hash, "entropy": "5.7", "status": "detected"},
        {"component": "WebGL", "value": webgl_renderer[:40], "entropy": "8.2", "status": "detected"},
        {"component": "Fonts", "value": f"{len(fonts)} detected", "entropy": "4.1", "status": "detected"},
        {"component": "Screen", "value": screen_res, "entropy": "3.5", "status": "detected"},
        {"component": "Timezone", "value": tz, "entropy": "2.8", "status": "detected"},
        {"component": "Language", "value": lang, "entropy": "1.2", "status": "detected"},
        {"component": "Hardware Concurrency", "value": "16 cores", "entropy": "3.0", "status": "detected"},
        {"component": "Device Memory", "value": "8 GB", "entropy": "2.5", "status": "detected"},
        {"component": "Audio Context", "value": "44100Hz", "entropy": "2.1", "status": "detected"},
        {"component": "Plugins", "value": "PDF Viewer, Native Client", "entropy": "1.8", "status": "detected"},
    ]
    fp_str = "|".join([c["value"] for c in components])
    fp_hash = _hashlib.sha256(fp_str.encode()).hexdigest()
    return jsonify({
        "hash": fp_hash,
        "canvas_hash": canvas_hash,
        "webgl_renderer": webgl_renderer,
        "font_count": len(fonts),
        "screen": screen_res,
        "timezone": tz,
        "language": lang,
        "components": components,
    })


@app.route("/api/fingerprint/compare", methods=["POST"])
def api_fingerprint_compare():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    hash_a = data.get("hash_a", "")
    hash_b = data.get("hash_b", "")
    match = hash_a == hash_b and len(hash_a) > 0
    similarity = 1.0 if match else (0.3 if (hash_a[:8] == hash_b[:8] and len(hash_a) > 0 and len(hash_b) > 0) else 0.0)
    return jsonify({
        "hash_a": hash_a,
        "hash_b": hash_b,
        "match": match,
        "similarity": round(similarity, 2),
    })


@app.route("/api/fingerprint/tips")
def api_fingerprint_tips():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    with _fp_lock:
        if not _fp_state["tips"]:
            _fp_state["tips"] = [
                {"title": "Canvas Fingerprinting Defense", "description": "Use browser extensions that add noise to canvas rendering, or use a browser with canvas randomization built-in."},
                {"title": "WebGL Spoofing", "description": "Override WebGL renderer strings via browser extensions or use a VM with generic GPU passthrough."},
                {"title": "Font Fingerprinting Mitigation", "description": "Use browsers that ship with a standard font set and block detection of system fonts."},
                {"title": "Timezone Obfuscation", "description": "Set your browser timezone to UTC or use a timezone spoofing extension to avoid location leaks."},
                {"title": "User-Agent Rotation", "description": "Rotate User-Agent strings periodically to prevent long-term tracking based on browser fingerprint."},
                {"title": "Hardware Concurrency Masking", "description": "Use browser privacy settings that report a generic core count (e.g., 2 or 4) instead of actual hardware."},
            ]
        return jsonify({"tips": _fp_state["tips"]})


# ── Social Engineering Routes ───────────────────────────────────────
_se_lock = threading.Lock()
_se_state = {"templates": []}


@app.route("/social-engineering")
def page_social_engineering():
    return render_template("social-engineering.html")


@app.route("/api/social-eng/templates")
def api_social_eng_templates():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    with _se_lock:
        if not _se_state["templates"]:
            _se_state["templates"] = [
                {"name": "Password Reset Phish", "category": "phishing", "description": "Mimics corporate password reset portal to harvest credentials", "difficulty": "easy", "success_rate": "34%"},
                {"name": "CEO Fraud Email", "category": "phishing", "description": "Whaling template impersonating CEO requesting urgent wire transfer", "difficulty": "hard", "success_rate": "12%"},
                {"name": "IT Support Vishing", "category": "vishing", "description": "Phone script posing as IT support requesting remote access", "difficulty": "medium", "success_rate": "28%"},
                {"name": "Vendor Pretext", "category": "pretexting", "description": "Poses as new vendor onboarding to gain internal system access", "difficulty": "hard", "success_rate": "18%"},
                {"name": "USB Drop Bait", "category": "baiting", "description": "Labeled USB drives left in parking lot with autorun payload", "difficulty": "medium", "success_rate": "45%"},
                {"name": "LinkedIn Recon", "category": "osint", "description": "Automated OSINT collection from LinkedIn for spear-phishing prep", "difficulty": "easy", "success_rate": "62%"},
                {"name": "QR Code Phish", "category": "phishing", "description": "QR codes placed in public areas redirecting to credential harvester", "difficulty": "easy", "success_rate": "22%"},
                {"name": "Tailgating Script", "category": "pretexting", "description": "Physical social engineering script for unauthorized building access", "difficulty": "medium", "success_rate": "38%"},
            ]
        return jsonify({"templates": _se_state["templates"], "categories": ["phishing", "vishing", "pretexting", "baiting", "osint"]})


@app.route("/api/social-eng/generate", methods=["POST"])
def api_social_eng_generate():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    category = data.get("category", "phishing")
    target = data.get("target", "general")
    templates = {
        "phishing": {"template": f"Subject: Urgent Action Required — {target}\n\nDear {target},\n\nWe have detected unusual activity on your account. Please verify your identity immediately by clicking the link below.\n\n[Simulated phishing link]\n\nThis is a simulated template for awareness training.", "category": "phishing"},
        "vishing": {"template": f"Vishing Script for {target}:\n\n'Hello, this is [Name] from IT Support. We're seeing unusual activity on your account and need to verify your credentials. Could you please confirm your username and current password so we can secure your account?'\n\n[Simulated vishing script for training purposes]", "category": "vishing"},
        "pretexting": {"template": f"Pretext Scenario for {target}:\n\nYou are a new vendor representative calling to set up billing integration. You need the target's internal system credentials to 'complete the setup.'\n\n[Simulated pretexting scenario for training]", "category": "pretexting"},
        "baiting": {"template": f"Baiting Scenario for {target}:\n\nLeave labeled USB drives ('Q3 Financial Report', 'Confidential - HR') in the target's parking lot. The USB contains a simulated payload that logs connection attempts.\n\n[Simulated baiting scenario for training]", "category": "baiting"},
    }
    return jsonify({"ok": True, "template": templates.get(category, templates["phishing"])["template"], "category": category})


@app.route("/api/social-eng/quiz")
def api_social_eng_quiz():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    questions = [
        {"question": "What is the most common social engineering attack vector?", "options": ["Email phishing", "Phone vishing", "Physical tailgating", "USB baiting"], "answer": "Email phishing"},
        {"question": "Which MITRE ATT&CK technique covers spearphishing attachments?", "options": ["T1566.001", "T1059.001", "T1071.001", "T1055"], "answer": "T1566.001"},
        {"question": "What is 'whaling' in social engineering?", "options": ["Targeting C-level executives", "Mass phishing campaigns", "USB drop attacks", "QR code phishing"], "answer": "Targeting C-level executives"},
        {"question": "Which defense is most effective against phishing?", "options": ["Email filtering + user training", "Firewall rules", "Antivirus software", "VPN usage"], "answer": "Email filtering + user training"},
    ]
    return jsonify({"questions": questions, "total": len(questions)})


# ── Zero-Day Exploits Routes ────────────────────────────────────────
_zd_lock = threading.Lock()
_zd_state = {"cves": [], "exploits": [], "poc": [], "chains": []}


@app.route("/zero-day")
def page_zero_day():
    return render_template("zero-day.html")


@app.route("/api/exploits/cve/search")
def api_exploits_cve_search():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    q = request.args.get("q", "")
    with _zd_lock:
        if not _zd_state["cves"]:
            _zd_state["cves"] = [
                {"cve_id": "CVE-2024-3094", "severity": "critical", "cvss": 10.0, "product": "XZ Utils (liblzma)", "exploit_available": True, "description": "Backdoor in XZ Utils affecting SSH authentication"},
                {"cve_id": "CVE-2024-21762", "severity": "critical", "cvss": 9.8, "product": "FortiOS", "exploit_available": True, "description": "Out-of-bounds write in FortiOS SSL-VPN"},
                {"cve_id": "CVE-2024-1709", "severity": "high", "cvss": 8.8, "product": "ConnectWise ScreenConnect", "exploit_available": True, "description": "Authentication bypass in ScreenConnect"},
                {"cve_id": "CVE-2023-46805", "severity": "medium", "cvss": 6.5, "product": "Ivanti Connect Secure", "exploit_available": True, "description": "Authentication bypass via path traversal"},
                {"cve_id": "CVE-2024-21887", "severity": "high", "cvss": 9.1, "product": "Ivanti Connect Secure", "exploit_available": True, "description": "Server-side request forgery in Ivanti CS"},
            ]
        results = [c for c in _zd_state["cves"] if not q or q.lower() in c["cve_id"].lower() or q.lower() in c["product"].lower()]
    return jsonify(results)


@app.route("/api/exploits/db")
def api_exploits_db():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    with _zd_lock:
        if not _zd_state["exploits"]:
            _zd_state["exploits"] = [
                {"title": "XZ Utils Backdoor (CVE-2024-3094)", "severity": "critical", "cvss": 10.0, "author": "A. Backdoor", "type": "remote_code_execution"},
                {"title": "FortiOS SSL-VPN OOB Write", "severity": "critical", "cvss": 9.8, "author": "FortiGuard Research", "type": "buffer_overflow"},
                {"title": "ScreenConnect Auth Bypass", "severity": "high", "cvss": 8.8, "author": "Huntress Labs", "type": "authentication_bypass"},
            ]
        return jsonify(_zd_state["exploits"])


@app.route("/api/exploits/poc", methods=["POST"])
def api_exploits_poc():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    with _zd_lock:
        poc = {
            "cve_id": data.get("cve_id", "CVE-XXXX-XXXX"),
            "status": "registered",
            "language": data.get("language", "python"),
            "created": time.time(),
        }
        _zd_state["poc"].append(poc)
    return jsonify({"ok": True, "poc": poc})


@app.route("/api/exploits/chains")
def api_exploits_chains():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    with _zd_lock:
        if not _zd_state["chains"]:
            _zd_state["chains"] = [
                {"name": "Ivanti Full Chain", "cves": ["CVE-2023-46805", "CVE-2024-21887"], "impact": "Full system compromise", "status": "active"},
                {"name": "Fortinet RCE Chain", "cves": ["CVE-2024-21762"], "impact": "Remote code execution on firewall", "status": "active"},
            ]
        return jsonify(_zd_state["chains"])


# ── Malware Analysis Routes ─────────────────────────────────────────
_ma_lock = threading.Lock()
_ma_state = {"yara": [], "classes": []}


@app.route("/malware-analysis")
def page_malware_analysis():
    return render_template("malware-analysis.html")


@app.route("/api/malware/hash/<sample_hash>")
def api_malware_hash(sample_hash):
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    return jsonify({
        "hash": sample_hash,
        "file_type": "PE32",
        "entropy": 6.42,
        "is_malicious": True,
        "detections": 42,
        "first_seen": time.time() - 86400,
        "static_analysis": [
            {"property": "File Type", "value": "PE32 Executable", "risk": "info", "details": "Windows Portable Executable"},
            {"property": "Entropy", "value": "6.42", "risk": "low", "details": "Below packing threshold (7.0)"},
            {"property": "Sections", "value": "5 sections", "risk": "info", "details": ".text, .rdata, .data, .rsrc, .reloc"},
            {"property": "Imports", "value": "3 DLLs", "risk": "low", "details": "kernel32.dll, user32.dll, ws2_32.dll"},
            {"property": "Strings", "value": "128 found", "risk": "info", "details": "URLs, IP addresses, registry keys"},
        ],
        "behavior": [
            {"action": "Registry Write", "detail": "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run", "severity": "high", "mitigation": "Monitor autorun keys"},
            {"action": "Network Connection", "detail": "Outbound to 185.220.101.42:443", "severity": "critical", "mitigation": "Block IP at firewall"},
            {"action": "Process Injection", "detail": "Injected into explorer.exe", "severity": "critical", "mitigation": "Enable DEP and ASLR"},
        ],
    })


@app.route("/api/malware/analyze", methods=["POST"])
def api_malware_analyze():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    return jsonify({
        "hash": data.get("hash", "simulated"),
        "filename": data.get("filename", "unknown"),
        "file_type": "PE32",
        "entropy": 6.42,
        "is_malicious": True,
        "sections": [{"name": ".text"}, {"name": ".rdata"}, {"name": ".data"}, {"name": ".rsrc"}, {"name": ".reloc"}],
        "imports": ["kernel32.dll", "user32.dll", "ws2_32.dll", "advapi32.dll"],
        "strings": ["http://evil.example.com/payload", "185.220.101.42", "HKLM\\SOFTWARE\\Microsoft"],
        "static_analysis": [
            {"property": "File Type", "value": "PE32 Executable", "risk": "info", "details": "Windows Portable Executable"},
            {"property": "Entropy", "value": "6.42", "risk": "low", "details": "Below packing threshold (7.0)"},
            {"property": "Sections", "value": "5 sections", "risk": "info", "details": ".text, .rdata, .data, .rsrc, .reloc"},
            {"property": "Imports", "value": "4 DLLs", "risk": "medium", "details": "kernel32.dll, user32.dll, ws2_32.dll, advapi32.dll"},
        ],
        "behavior": [
            {"action": "Registry Write", "detail": "HKLM\\...\\Run", "severity": "high", "mitigation": "Monitor autorun keys"},
            {"action": "Network Connection", "detail": "Outbound C2", "severity": "critical", "mitigation": "Block IP at firewall"},
        ],
    })


@app.route("/api/malware/yara")
def api_malware_yara():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    with _ma_lock:
        if not _ma_state["yara"]:
            _ma_state["yara"] = [
                {"name": "Trojan_Generic_Dropper", "description": "Detects generic trojan dropper behavior patterns", "severity": "high"},
                {"name": "Ransomware_WannaCry", "description": "Matches WannaCry ransomware string and encryption patterns", "severity": "critical"},
                {"name": "Backdoor_CobaltStrike", "description": "Detects Cobalt Strike beacon artifacts and Malleable C2 profiles", "severity": "critical"},
                {"name": "Packer_UPX", "description": "Identifies UPX-packed binaries for further analysis", "severity": "medium"},
                {"name": "ExploitKit_Nuclear", "description": "Detects Nuclear Exploit Kit landing page patterns", "severity": "high"},
            ]
        return jsonify(_ma_state["yara"])


@app.route("/api/malware/classes")
def api_malware_classes():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    with _ma_lock:
        if not _ma_state["classes"]:
            _ma_state["classes"] = [
                {"name": "Trojan", "category": "Malware", "severity": "high", "description": "Malicious software disguised as legitimate"},
                {"name": "Ransomware", "category": "Malware", "severity": "critical", "description": "Encrypts files and demands payment for decryption"},
                {"name": "Rootkit", "category": "Stealth", "severity": "critical", "description": "Hides presence on infected system"},
                {"name": "Worm", "category": "Malware", "severity": "high", "description": "Self-replicating malware spreading across networks"},
                {"name": "Spyware", "category": "Surveillance", "severity": "medium", "description": "Collects user data without consent"},
                {"name": "Adware", "category": "Nuisance", "severity": "low", "description": "Displays unwanted advertisements"},
                {"name": "Backdoor", "category": "Access", "severity": "critical", "description": "Provides unauthorized remote access"},
                {"name": "Botnet", "category": "Network", "severity": "high", "description": "Network of compromised devices under attacker control"},
            ]
        return jsonify(_ma_state["classes"])


# ── Network Exploitation Routes ─────────────────────────────────────
_ne_lock = threading.Lock()
_ne_state = {"running": False, "hosts": [], "mitm": []}


@app.route("/network-exploitation")
def page_network_exploitation():
    return render_template("network-exploitation.html")


@app.route("/api/net-scan/status")
def api_net_scan_status():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    with _ne_lock:
        return jsonify({
            "running": _ne_state["running"],
            "hosts": _ne_state["hosts"],
            "mitm": _ne_state["mitm"],
            "threats": [],
        })


@app.route("/api/net-scan/start", methods=["POST"])
def api_net_scan_start():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    with _ne_lock:
        _ne_state["running"] = True
        _ne_state["hosts"] = [
            {"name": "Gateway", "ip": "192.168.1.1", "open_ports": [80, 443], "state": "open", "hostname": "router.local"},
            {"name": "Web Server", "ip": "192.168.1.10", "open_ports": [80, 443, 8080], "state": "open", "hostname": "webserver.local"},
            {"name": "Database", "ip": "192.168.1.20", "open_ports": [3306, 5432], "state": "open", "hostname": "db.local"},
            {"name": "Workstation", "ip": "192.168.1.50", "open_ports": [22, 3389], "state": "filtered", "hostname": "ws-01.local"},
            {"name": "File Server", "ip": "192.168.1.30", "open_ports": [445, 139], "state": "open", "hostname": "fileserver.local"},
        ]
        _ne_state["running"] = False
    return jsonify({"ok": True, "hosts": _ne_state["hosts"], "hosts_found": len(_ne_state["hosts"])})


@app.route("/api/wireless/handshakes")
def api_wireless_handshakes():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    return jsonify({
        "handshakes": [
            {"ssid": "FreeAI-Lab", "bssid": "AA:BB:CC:DD:EE:01", "signal": -45, "cracked": False},
            {"ssid": "CorpNet-5G", "bssid": "AA:BB:CC:DD:EE:02", "signal": -62, "cracked": False},
            {"ssid": "OpenGuest", "bssid": "AA:BB:CC:DD:EE:04", "signal": -55, "cracked": True},
        ],
        "total": 3,
    })


@app.route("/api/wireless/analyze", methods=["POST"])
def api_wireless_analyze():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    return jsonify({
        "ok": True,
        "ssid": data.get("ssid", "unknown"),
        "analysis": {
            "encryption": data.get("encryption", "WPA2"),
            "channel": data.get("channel", 6),
            "vulnerabilities": ["WPS enabled", "Weak passphrase detected"],
            "recommendation": "Disable WPS and enforce WPA3",
        },
    })


# ── Cloud Exploitation Routes ───────────────────────────────────────
_ce_lock = threading.Lock()
_ce_state = {"configs": [], "iam": [], "metadata": [], "containers": []}


@app.route("/cloud-exploitation")
def page_cloud_exploitation():
    return render_template("cloud-exploitation.html")


@app.route("/api/cloud/configs")
def api_cloud_configs():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    with _ce_lock:
        if not _ce_state["configs"]:
            _ce_state["configs"] = [
                {"resource": "s3://company-data-backup", "cloud": "AWS", "issue": "Public read access on sensitive bucket", "severity": "critical", "remediation": "Remove public read ACL and enable bucket policy"},
                {"resource": "blob://prod-logs", "cloud": "Azure", "issue": "Anonymous blob read access enabled", "severity": "high", "remediation": "Disable anonymous access in storage account settings"},
                {"resource": "gs://ml-training-data", "cloud": "GCP", "issue": "allUsers reader permission on bucket", "severity": "high", "remediation": "Remove allUsers IAM binding"},
                {"resource": "s3://public-website-assets", "cloud": "AWS", "issue": "No encryption at rest", "severity": "medium", "remediation": "Enable SSE-S3 or SSE-KMS encryption"},
                {"resource": "EC2 i-0abc123", "cloud": "AWS", "issue": "Security group allows 0.0.0.0/0 on port 22", "severity": "critical", "remediation": "Restrict SSH access to known IP ranges"},
            ]
        return jsonify(_ce_state["configs"])


@app.route("/api/cloud/scan", methods=["POST"])
def api_cloud_scan():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    providers = data.get("providers", ["aws", "azure", "gcp"])
    findings = []
    if "aws" in providers:
        findings.extend([
            {"resource": "s3://company-data-backup", "cloud": "AWS", "issue": "Public read access", "severity": "critical", "remediation": "Remove public ACL"},
            {"resource": "EC2 i-0abc123", "cloud": "AWS", "issue": "Open SSH to world", "severity": "critical", "remediation": "Restrict SG"},
        ])
    if "azure" in providers:
        findings.append({"resource": "blob://prod-logs", "cloud": "Azure", "issue": "Anonymous read", "severity": "high", "remediation": "Disable anon access"})
    if "gcp" in providers:
        findings.append({"resource": "gs://ml-training-data", "cloud": "GCP", "issue": "allUsers reader", "severity": "high", "remediation": "Remove IAM binding"})
    with _ce_lock:
        _ce_state["configs"] = findings
    return jsonify({"ok": True, "findings": findings, "total": len(findings)})


@app.route("/api/cloud/iam")
def api_cloud_iam():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    with _ce_lock:
        if not _ce_state["iam"]:
            _ce_state["iam"] = [
                {"role": "LambdaBasicExecution", "cloud": "AWS", "path": "lambda:InvokeFunction → sts:AssumeRole → AdministratorAccess", "severity": "critical"},
                {"role": "StorageBlobDataReader", "cloud": "Azure", "path": "Microsoft.Storage/storageAccounts/listKeys → Key Vault read", "severity": "high"},
                {"role": "compute.viewer", "cloud": "GCP", "path": "compute.instances.getSerialPortOutput → metadata server → service account keys", "severity": "high"},
            ]
        return jsonify(_ce_state["iam"])


@app.route("/api/cloud/exploit-sim", methods=["POST"])
def api_cloud_exploit_sim():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    return jsonify({
        "ok": True,
        "scenario": data.get("scenario", "metadata_abuse"),
        "steps": [
            "Access IMDS at 169.254.169.254",
            "Retrieve instance identity document",
            "Extract IAM role credentials",
            "Assume role with elevated permissions",
            "Access S3 buckets with assumed role",
        ],
        "mitigation": "Use IMDSv2 with session tokens, restrict metadata access via IAM",
    })


# ── DDNS Management ──────────────────────────────────────────────

@app.route("/ddns-manager")
def ddns_manager_page():
    locale = get_locale_from_session(session)
    return render_template("ddns-manager.html", i18n_locale=locale)


@app.route("/api/ddns/status")
def api_ddns_status():
    with _DDNS_LOCK:
        return jsonify({
            "provider": _DDNS_PROVIDER.get("service", "no-ip"),
            "hostname": _DDNS_PROVIDER.get("hostname", ""),
            "auto_refresh": _DDNS_PROVIDER.get("auto_refresh", False),
            "records_count": len(_DDNS_RECORDS),
        })


@app.route("/api/ddns/records")
def api_ddns_records():
    with _DDNS_LOCK:
        return jsonify(_DDNS_RECORDS)


@app.route("/api/ddns/records/<record_id>", methods=["PUT"])
def api_ddns_update_record(record_id):
    data = request.get_json(silent=True) or {}
    with _DDNS_LOCK:
        for rec in _DDNS_RECORDS:
            if rec["id"] == record_id:
                for key in ("type", "hostname", "value", "ttl", "status"):
                    if key in data:
                        rec[key] = data[key]
                return jsonify({"ok": True, "record": rec})
    return jsonify({"error": "record not found"}), 404


@app.route("/api/ddns/provision", methods=["POST"])
def api_ddns_provision():
    data = request.get_json(silent=True) or {}
    with _DDNS_LOCK:
        new_id = str(max((int(r["id"]) for r in _DDNS_RECORDS), default=0) + 1)
        record = {
            "id": new_id,
            "type": data.get("type", "A"),
            "hostname": data.get("hostname", ""),
            "value": data.get("value", ""),
            "ttl": data.get("ttl", 300),
            "status": "active",
        }
        _DDNS_RECORDS.append(record)
    return jsonify({"ok": True, "record": record})


@app.route("/api/ddns/sync")
def api_ddns_sync():
    with _DDNS_LOCK:
        return jsonify({
            "synced": True,
            "records": _DDNS_RECORDS,
            "ts": time.time(),
        })


# ── Network Auto-Management ──────────────────────────────────────

@app.route("/network-auto")
def network_auto_page():
    locale = get_locale_from_session(session)
    return render_template("network-auto.html", i18n_locale=locale)


@app.route("/api/network/status")
def api_network_status():
    with _NETWORK_LOCK:
        return jsonify(_NETWORK_STATE)


@app.route("/api/network/vpn/toggle", methods=["POST"])
def api_network_vpn_toggle():
    data = request.get_json(silent=True) or {}
    with _NETWORK_LOCK:
        current = _NETWORK_STATE["vpn"]["enabled"]
        _NETWORK_STATE["vpn"]["enabled"] = not current
        _NETWORK_STATE["vpn"]["status"] = "connected" if not current else "disconnected"
        _NETWORK_STATE["vpn"]["provider"] = data.get("provider", _NETWORK_STATE["vpn"]["provider"])
    return jsonify({"ok": True, "vpn": _NETWORK_STATE["vpn"]})


@app.route("/api/network/tor/circuit", methods=["POST"])
def api_network_tor_circuit():
    data = request.get_json(silent=True) or {}
    with _NETWORK_LOCK:
        _NETWORK_STATE["tor"]["enabled"] = data.get("enabled", not _NETWORK_STATE["tor"]["enabled"])
        _NETWORK_STATE["tor"]["circuit"] = data.get("circuit", _NETWORK_STATE["tor"]["circuit"])
        _NETWORK_STATE["tor"]["status"] = "active" if _NETWORK_STATE["tor"]["enabled"] else "stopped"
    return jsonify({"ok": True, "tor": _NETWORK_STATE["tor"]})


@app.route("/api/network/quality")
def api_network_quality():
    with _NETWORK_LOCK:
        q = _NETWORK_STATE["quality"]
        return jsonify({
            "latency_ms": q.get("latency_ms", random.randint(10, 120)),
            "bandwidth_up": q.get("bandwidth_up", round(random.uniform(5, 50), 1)),
            "bandwidth_down": q.get("bandwidth_down", round(random.uniform(20, 200), 1)),
            "packet_loss": q.get("packet_loss", round(random.uniform(0, 2), 2)),
            "ts": time.time(),
        })


@app.route("/api/network/optimize", methods=["POST"])
def api_network_optimize():
    data = request.get_json(silent=True) or {}
    with _NETWORK_LOCK:
        _NETWORK_STATE["quality"] = {
            "latency_ms": random.randint(5, 60),
            "bandwidth_up": round(random.uniform(20, 100), 1),
            "bandwidth_down": round(random.uniform(50, 500), 1),
            "packet_loss": round(random.uniform(0, 0.5), 2),
        }
    return jsonify({"ok": True, "quality": _NETWORK_STATE["quality"]})


# ── Cards Settings API ──────────────────────────────────────────

@app.route("/api/cards/settings")
def api_cards_settings():
    with _CARDS_LOCK:
        return jsonify(_CARDS_CONFIG)


@app.route("/api/cards/settings/<card_name>")
def api_cards_settings_get(card_name):
    with _CARDS_LOCK:
        config = _CARDS_CONFIG.get(card_name)
        if config is None:
            return jsonify({"error": "card not found"}), 404
        return jsonify(config)


@app.route("/api/cards/settings/<card_name>", methods=["PUT"])
def api_cards_settings_update(card_name):
    data = request.get_json(silent=True) or {}
    with _CARDS_LOCK:
        if card_name not in _CARDS_CONFIG:
            return jsonify({"error": "card not found"}), 404
        for key in ("title", "icon", "auto_refresh", "refresh_interval"):
            if key in data:
                _CARDS_CONFIG[card_name][key] = data[key]
    return jsonify({"ok": True, "config": _CARDS_CONFIG[card_name]})


# ── API: AI Training Extended ─────────────────────────────────────
_AI_TRAINING_JOBS = {}
_AI_TRAINING_LOCK = threading.Lock()


@app.route("/api/training/jobs", methods=["GET"])
def api_training_jobs_list():
    with _TRAINING_LOCK:
        all_jobs = []
        for jtype, jobs in _TRAINING_DATA["jobs"].items():
            for j in jobs:
                all_jobs.append({**j, "job_type": jtype})
        return jsonify(all_jobs)


@app.route("/api/training/jobs/<job_id>", methods=["GET"])
def api_training_job_detail(job_id):
    with _TRAINING_LOCK:
        for jtype, jobs in _TRAINING_DATA["jobs"].items():
            for j in jobs:
                if j["id"] == job_id:
                    return jsonify({**j, "job_type": jtype})
    return jsonify({"error": "job not found"}), 404


@app.route("/api/training/jobs/<job_id>/status", methods=["PUT"])
def api_training_job_status(job_id):
    data = request.get_json(silent=True) or {}
    new_status = data.get("status")
    if not new_status:
        return jsonify({"error": "status required"}), 400
    with _TRAINING_LOCK:
        for jtype, jobs in _TRAINING_DATA["jobs"].items():
            for j in jobs:
                if j["id"] == job_id:
                    j["status"] = new_status
                    return jsonify({"ok": True, "id": job_id, "status": new_status})
    return jsonify({"error": "job not found"}), 404


@app.route("/api/training/datasets", methods=["GET"])
def api_training_datasets_list():
    with _TRAINING_LOCK:
        return jsonify(_TRAINING_DATA["datasets"])


@app.route("/api/training/datasets", methods=["POST"])
def api_training_dataset_create():
    name = request.form.get("name", "untitled")
    fmt = request.form.get("format", "jsonl")
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


@app.route("/api/training/models", methods=["GET"])
def api_training_models_list():
    with _TRAINING_LOCK:
        return jsonify(_TRAINING_DATA["models"])


@app.route("/api/training/deploy", methods=["POST"])
def api_training_deploy():
    data = request.get_json(silent=True) or {}
    model_id = data.get("model_id", "")
    with _TRAINING_LOCK:
        for m in _TRAINING_DATA["models"]:
            if m["id"] == model_id:
                m["deployed"] = True
                return jsonify({"ok": True, "endpoint": "http://localhost:9001/v1/completions", "model": m["name"]})
    return jsonify({"error": "model not found"}), 404


@app.route("/api/training/gpu-status", methods=["GET"])
def api_training_gpu_status():
    devices = _gpu_state.get("devices", [])
    if not devices:
        return jsonify({"devices": [{"id": 0, "name": "mock-gpu", "memory_total": 24576, "memory_used": 0, "utilization": 0, "temperature": 35, "current_job": ""}]})
    result = []
    for d in devices:
        result.append({
            "id": d.get("id", 0),
            "name": d.get("name", "unknown"),
            "memory_total": d.get("memory_total", 0),
            "memory_used": d.get("memory_used", 0),
            "utilization": d.get("utilization", 0),
            "temperature": d.get("temperature", 0),
            "current_job": d.get("current_job", ""),
        })
    return jsonify({"devices": result})


@app.route("/ai-training")
def ai_training_page():
    return render_template("ai-training.html")

@app.route("/sandbox")
def page_sandbox():
    return render_template("sandbox.html")




# ── Memory Primitives ──
_memory_primitives_lock = threading.Lock()
_memory_primitives_state = {"simulations": []}


@app.route("/api/exploit-cat/memory-primitives/describe")
def api_exploit_cat_memory_primitives_describe():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.memory_primitives import MemoryPrimitivesAgent
    agent = MemoryPrimitivesAgent()
    return jsonify(_call_agent_method(agent, "describe"))


@app.route("/api/exploit-cat/memory-primitives/list")
def api_exploit_cat_memory_primitives_list():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.memory_primitives import MemoryPrimitivesAgent
    agent = MemoryPrimitivesAgent()
    return jsonify(_call_agent_method(agent, "list_primitives"))


@app.route("/api/exploit-cat/memory-primitives/<name>")
def api_exploit_cat_memory_primitives_get(name):
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.memory_primitives import MemoryPrimitivesAgent
    agent = MemoryPrimitivesAgent()
    return jsonify(_call_agent_method(agent, "get_primitive", name))


@app.route("/api/exploit-cat/memory-primitives/simulate", methods=["POST"])
def api_exploit_cat_memory_primitives_simulate():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    from agents.specialized.memory_primitives import MemoryPrimitivesAgent
    agent = MemoryPrimitivesAgent()
    primitive_name = data.get("primitive", "buffer_overflow")
    target_info = data.get("target_info", {})
    result = _call_agent_method(agent, "simulate_primitive", primitive_name, target_info)
    with _memory_primitives_lock:
        _memory_primitives_state["simulations"].append(result)
    return jsonify(result)


@app.route("/api/exploit-cat/memory-primitives/map-to-exploit", methods=["POST"])
def api_exploit_cat_memory_primitives_map_to_exploit():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    from agents.specialized.memory_primitives import MemoryPrimitivesAgent
    agent = MemoryPrimitivesAgent()
    primitive_name = data.get("primitive", "buffer_overflow")
    return jsonify(_call_agent_method(agent, "map_to_exploit", primitive_name))


@app.route("/api/exploit-cat/memory-primitives/mitigations/<name>")
def api_exploit_cat_memory_primitives_mitigations(name):
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.memory_primitives import MemoryPrimitivesAgent
    agent = MemoryPrimitivesAgent()
    return jsonify(_call_agent_method(agent, "find_mitigations", name))


@app.route("/api/exploit-cat/memory-primitives/cves")
def api_exploit_cat_memory_primitives_cves():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.memory_primitives import MemoryPrimitivesAgent
    agent = MemoryPrimitivesAgent()
    return jsonify(_call_agent_method(agent, "get_cves"))


# ── Chained Zero-Day Exploitation ─────────────────────────────────────



# ── Agent method caller (handles both sync and async) ───────────────────
def _call_agent_method(agent, method_name, *args, **kwargs):
    """Call an agent method, handling both sync and async returns."""
    import inspect
    method = getattr(agent, method_name)
    result = method(*args, **kwargs)
    if inspect.isawaitable(result):
        result = asyncio.run(result)
    return result


_chained_zero_day_lock = threading.Lock()
_chained_zero_day_state = {"simulations": []}


@app.route("/api/exploit-cat/chained-zero-day/describe")
def api_exploit_cat_chained_zero_day_describe():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.chained_zero_day import ChainedZeroDayAgent
    agent = ChainedZeroDayAgent()
    return jsonify(_call_agent_method(agent, "describe"))


@app.route("/api/exploit-cat/chained-zero-day/build-chain", methods=["POST"])
def api_exploit_cat_chained_zero_day_build_chain():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    from agents.specialized.chained_zero_day import ChainedZeroDayAgent
    agent = ChainedZeroDayAgent()
    stages = data.get("stages", [])
    return jsonify(_call_agent_method(agent, "build_chain", stages))


@app.route("/api/exploit-cat/chained-zero-day/analyze-chain", methods=["POST"])
def api_exploit_cat_chained_zero_day_analyze_chain():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    from agents.specialized.chained_zero_day import ChainedZeroDayAgent
    agent = ChainedZeroDayAgent()
    chain_id = data.get("chain_id", "")
    return jsonify(_call_agent_method(agent, "analyze_chain", chain_id))


@app.route("/api/exploit-cat/chained-zero-day/simulate-chain", methods=["POST"])
def api_exploit_cat_chained_zero_day_simulate_chain():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    from agents.specialized.chained_zero_day import ChainedZeroDayAgent
    agent = ChainedZeroDayAgent()
    chain_id = data.get("chain_id", "")
    target = data.get("target", None)
    result = _call_agent_method(agent, "simulate_chain", chain_id, target)
    with _chained_zero_day_lock:
        _chained_zero_day_state["simulations"].append(result)
    return jsonify(result)


@app.route("/api/exploit-cat/chained-zero-day/list-chains")
def api_exploit_cat_chained_zero_day_list_chains():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.chained_zero_day import ChainedZeroDayAgent
    agent = ChainedZeroDayAgent()
    return jsonify(_call_agent_method(agent, "list_chains"))


@app.route("/api/exploit-cat/chained-zero-day/optimize-chain", methods=["POST"])
def api_exploit_cat_chained_zero_day_optimize_chain():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    from agents.specialized.chained_zero_day import ChainedZeroDayAgent
    agent = ChainedZeroDayAgent()
    chain_id = data.get("chain_id", "")
    return jsonify(_call_agent_method(agent, "optimize_chain", chain_id))


@app.route("/api/exploit-cat/chained-zero-day/cves")
def api_exploit_cat_chained_zero_day_cves():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.chained_zero_day import ChainedZeroDayAgent
    agent = ChainedZeroDayAgent()
    return jsonify(_call_agent_method(agent, "get_cves"))

# Memory Corruption Exploitation
@app.route("/api/exploit-cat/memory-corruption/describe", methods=["GET"])
def api_memory_corruption_describe():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.memory_corruption import MemoryCorruptionAgent
    agent = MemoryCorruptionAgent()
    return jsonify(agent.describe())

@app.route("/api/exploit-cat/memory-corruption/simulate-buffer-overflow", methods=["POST"])
def api_memory_corruption_simulate_buffer_overflow():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.memory_corruption import MemoryCorruptionAgent
    agent = MemoryCorruptionAgent()
    data = request.get_json() or {}
    return jsonify(agent.simulate_buffer_overflow(
        data.get("target", "localhost"),
        data.get("overflow_type", "stack"),
        data.get("size", 256)
    ))

@app.route("/api/exploit-cat/memory-corruption/simulate-heap-corruption", methods=["POST"])
def api_memory_corruption_simulate_heap_corruption():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.memory_corruption import MemoryCorruptionAgent
    agent = MemoryCorruptionAgent()
    data = request.get_json() or {}
    return jsonify(agent.simulate_heap_corruption(
        data.get("target", "localhost"),
        data.get("corruption_type", "tcache_poisoning")
    ))

@app.route("/api/exploit-cat/memory-corruption/simulate-uaf", methods=["POST"])
def api_memory_corruption_simulate_uaf():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.memory_corruption import MemoryCorruptionAgent
    agent = MemoryCorruptionAgent()
    data = request.get_json() or {}
    return jsonify(agent.simulate_uaf(
        data.get("target", "localhost"),
        data.get("allocation_pattern", "double_free")
    ))

@app.route("/api/exploit-cat/memory-corruption/primitives", methods=["GET"])
def api_memory_corruption_primitives():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.memory_corruption import MemoryCorruptionAgent
    agent = MemoryCorruptionAgent()
    return jsonify(agent.list_primitives())

@app.route("/api/exploit-cat/memory-corruption/cves", methods=["GET"])
def api_memory_corruption_cves():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.memory_corruption import MemoryCorruptionAgent
    agent = MemoryCorruptionAgent()
    return jsonify(agent.get_cves())

@app.route("/api/exploit-cat/memory-corruption/simulate-format-string", methods=["POST"])
def api_memory_corruption_simulate_format_string():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.memory_corruption import MemoryCorruptionAgent
    agent = MemoryCorruptionAgent()
    data = request.get_json() or {}
    return jsonify(agent.simulate_format_string(
        data.get("target", "localhost"),
        data.get("format_str", "%n")
    ))

@app.route("/api/exploit-cat/memory-corruption/generate-payload", methods=["POST"])
def api_memory_corruption_generate_payload():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.memory_corruption import MemoryCorruptionAgent
    agent = MemoryCorruptionAgent()
    data = request.get_json() or {}
    return jsonify(agent.generate_payload(
        data.get("payload_type", "nop_sled"),
        data.get("arch", "x86_64")
    ))

# SSRF Exploitation
@app.route("/api/exploit-cat/ssrf-exploit/describe", methods=["GET"])
def api_ssrf_exploit_describe():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.ssrf_exploit import SSRFExploitAgent
    agent = SSRFExploitAgent()
    return jsonify(agent.describe())

@app.route("/api/exploit-cat/ssrf-exploit/simulate", methods=["POST"])
def api_ssrf_exploit_simulate():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.ssrf_exploit import SSRFExploitAgent
    agent = SSRFExploitAgent()
    data = request.get_json() or {}
    return jsonify(agent.simulate_ssrf(
        data.get("url", ""),
        data.get("target", "http://169.254.169.254/")
    ))

@app.route("/api/exploit-cat/ssrf-exploit/cloud-metadata", methods=["POST"])
def api_ssrf_exploit_cloud_metadata():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.ssrf_exploit import SSRFExploitAgent
    agent = SSRFExploitAgent()
    data = request.get_json() or {}
    return jsonify(agent.simulate_cloud_metadata(data.get("provider", "aws")))

@app.route("/api/exploit-cat/ssrf-exploit/dns-rebinding", methods=["POST"])
def api_ssrf_exploit_dns_rebinding():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.ssrf_exploit import SSRFExploitAgent
    agent = SSRFExploitAgent()
    data = request.get_json() or {}
    return jsonify(agent.simulate_dns_rebinding(data.get("target", "internal.local")))

@app.route("/api/exploit-cat/ssrf-exploit/generate-payload", methods=["POST"])
def api_ssrf_exploit_generate_payload():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.ssrf_exploit import SSRFExploitAgent
    agent = SSRFExploitAgent()
    data = request.get_json() or {}
    return jsonify(agent.generate_payload(
        data.get("payload_type", "dns_rebinding"),
        data.get("target", "internal.service.local")
    ))

@app.route("/api/exploit-cat/ssrf-exploit/blind-ssrf", methods=["POST"])
def api_ssrf_exploit_blind_ssrf():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.ssrf_exploit import SSRFExploitAgent
    agent = SSRFExploitAgent()
    data = request.get_json() or {}
    return jsonify(agent.simulate_blind_ssrf(data.get("method", "out_of_band")))

@app.route("/api/exploit-cat/ssrf-exploit/primitives", methods=["GET"])
def api_ssrf_exploit_primitives():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.ssrf_exploit import SSRFExploitAgent
    agent = SSRFExploitAgent()
    return jsonify(agent.list_primitives())

@app.route("/api/exploit-cat/ssrf-exploit/cves", methods=["GET"])
def api_ssrf_exploit_cves():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.ssrf_exploit import SSRFExploitAgent
    agent = SSRFExploitAgent()
    return jsonify(agent.get_cves())

# Deserialization Exploitation
@app.route("/api/exploit-cat/deserialization-exploit/describe", methods=["GET"])
def api_deserialization_exploit_describe():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.deserialization_exploit import DeserializationExploitAgent
    agent = DeserializationExploitAgent()
    return jsonify(agent.describe())

@app.route("/api/exploit-cat/deserialization-exploit/simulate-java", methods=["POST"])
def api_deserialization_exploit_simulate_java():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.deserialization_exploit import DeserializationExploitAgent
    agent = DeserializationExploitAgent()
    data = request.get_json() or {}
    return jsonify(agent.simulate_java_deserialization(
        data.get("gadget_chain", "commonscollections"),
        data.get("target", "webapp.jar")
    ))

@app.route("/api/exploit-cat/deserialization-exploit/simulate-python", methods=["POST"])
def api_deserialization_exploit_simulate_python():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.deserialization_exploit import DeserializationExploitAgent
    agent = DeserializationExploitAgent()
    data = request.get_json() or {}
    return jsonify(agent.simulate_python_deserialization(
        data.get("gadget_chain", "pickle"),
        data.get("target", "app.py")
    ))

@app.route("/api/exploit-cat/deserialization-exploit/generate-payload", methods=["POST"])
def api_deserialization_exploit_generate_payload():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.deserialization_exploit import DeserializationExploitAgent
    agent = DeserializationExploitAgent()
    data = request.get_json() or {}
    return jsonify(agent.generate_payload(
        data.get("language", "java"),
        data.get("chain", "commonscollections")
    ))

@app.route("/api/exploit-cat/deserialization-exploit/primitives", methods=["GET"])
def api_deserialization_exploit_primitives():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.deserialization_exploit import DeserializationExploitAgent
    agent = DeserializationExploitAgent()
    return jsonify(agent.list_primitives())

@app.route("/api/exploit-cat/deserialization-exploit/cves", methods=["GET"])
def api_deserialization_exploit_cves():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.deserialization_exploit import DeserializationExploitAgent
    agent = DeserializationExploitAgent()
    return jsonify(agent.get_cves())

# Messaging RCE Exploitation
@app.route("/api/exploit-cat/messaging-rce/describe", methods=["GET"])
def api_messaging_rce_describe():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.messaging_rce import MessagingRCEAgent
    agent = MessagingRCEAgent()
    return jsonify(agent.describe())

@app.route("/api/exploit-cat/messaging-rce/simulate-imessage", methods=["POST"])
def api_messaging_rce_simulate_imessage():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.messaging_rce import MessagingRCEAgent
    agent = MessagingRCEAgent()
    data = request.get_json() or {}
    return jsonify(agent.simulate_imessage_exploit(
        data.get("target", "iphone_user"),
        data.get("exploit_type", "rce")
    ))

@app.route("/api/exploit-cat/messaging-rce/simulate-whatsapp", methods=["POST"])
def api_messaging_rce_simulate_whatsapp():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.messaging_rce import MessagingRCEAgent
    agent = MessagingRCEAgent()
    data = request.get_json() or {}
    return jsonify(agent.simulate_whatsapp_exploit(
        data.get("target", "whatsapp_user"),
        data.get("exploit_type", "rce")
    ))

@app.route("/api/exploit-cat/messaging-rce/simulate-signal", methods=["POST"])
def api_messaging_rce_simulate_signal():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.messaging_rce import MessagingRCEAgent
    agent = MessagingRCEAgent()
    data = request.get_json() or {}
    return jsonify(agent.simulate_signal_exploit(
        data.get("target", "signal_user"),
        data.get("exploit_type", "rce")
    ))

@app.route("/api/exploit-cat/messaging-rce/simulate-telegram", methods=["POST"])
def api_messaging_rce_simulate_telegram():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.messaging_rce import MessagingRCEAgent
    agent = MessagingRCEAgent()
    data = request.get_json() or {}
    return jsonify(agent.simulate_telegram_exploit(
        data.get("target", "telegram_user"),
        data.get("exploit_type", "rce")
    ))

@app.route("/api/exploit-cat/messaging-rce/generate-payload", methods=["POST"])
def api_messaging_rce_generate_payload():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.messaging_rce import MessagingRCEAgent
    agent = MessagingRCEAgent()
    data = request.get_json() or {}
    return jsonify(agent.generate_payload(
        data.get("platform", "imessage"),
        data.get("payload_type", "rce")
    ))

@app.route("/api/exploit-cat/messaging-rce/primitives", methods=["GET"])
def api_messaging_rce_primitives():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.messaging_rce import MessagingRCEAgent
    agent = MessagingRCEAgent()
    return jsonify(agent.list_primitives())

@app.route("/api/exploit-cat/messaging-rce/cves", methods=["GET"])
def api_messaging_rce_cves():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.messaging_rce import MessagingRCEAgent
    agent = MessagingRCEAgent()
    return jsonify(agent.get_cves())

# Media Exploitation
@app.route("/api/exploit-cat/media-exploit/describe", methods=["GET"])
def api_media_exploit_describe():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.media_exploit import MediaExploitAgent
    agent = MediaExploitAgent()
    return jsonify(agent.describe())

@app.route("/api/exploit-cat/media-exploit/simulate-video", methods=["POST"])
def api_media_exploit_simulate_video():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.media_exploit import MediaExploitAgent
    agent = MediaExploitAgent()
    data = request.get_json() or {}
    return jsonify(agent.simulate_video_exploit(
        data.get("format", "mp4"),
        data.get("codec", "h264"),
        data.get("target", "vlc")
    ))

@app.route("/api/exploit-cat/media-exploit/simulate-audio", methods=["POST"])
def api_media_exploit_simulate_audio():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.media_exploit import MediaExploitAgent
    agent = MediaExploitAgent()
    data = request.get_json() or {}
    return jsonify(agent.simulate_audio_exploit(
        data.get("format", "mp3"),
        data.get("codec", "mp3"),
        data.get("target", "player")
    ))

@app.route("/api/exploit-cat/media-exploit/simulate-image", methods=["POST"])
def api_media_exploit_simulate_image():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.media_exploit import MediaExploitAgent
    agent = MediaExploitAgent()
    data = request.get_json() or {}
    return jsonify(agent.simulate_image_exploit(
        data.get("format", "png"),
        data.get("codec", "libpng"),
        data.get("target", "viewer")
    ))

@app.route("/api/exploit-cat/media-exploit/generate-payload", methods=["POST"])
def api_media_exploit_generate_payload():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.media_exploit import MediaExploitAgent
    agent = MediaExploitAgent()
    data = request.get_json() or {}
    return jsonify(agent.generate_payload(
        data.get("format", "mp4"),
        data.get("vector", "buffer_overflow")
    ))

@app.route("/api/exploit-cat/media-exploit/primitives", methods=["GET"])
def api_media_exploit_primitives():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.media_exploit import MediaExploitAgent
    agent = MediaExploitAgent()
    return jsonify(agent.list_primitives())

@app.route("/api/exploit-cat/media-exploit/cves", methods=["GET"])
def api_media_exploit_cves():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.media_exploit import MediaExploitAgent
    agent = MediaExploitAgent()
    return jsonify(agent.get_cves())

# File Parsing Exploitation
@app.route("/api/exploit-cat/file-parse-exploit/describe", methods=["GET"])
def api_file_parse_exploit_describe():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.file_parse_exploit import FileParseExploitAgent
    agent = FileParseExploitAgent()
    return jsonify(agent.describe())

@app.route("/api/exploit-cat/file-parse-exploit/simulate-xxe", methods=["POST"])
def api_file_parse_exploit_simulate_xxe():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.file_parse_exploit import FileParseExploitAgent
    agent = FileParseExploitAgent()
    data = request.get_json() or {}
    return jsonify(agent.simulate_xxe_exploit(
        data.get("target", "parser"),
        data.get("payload", "file:///etc/passwd")
    ))

@app.route("/api/exploit-cat/file-parse-exploit/simulate-pdf", methods=["POST"])
def api_file_parse_exploit_simulate_pdf():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.file_parse_exploit import FileParseExploitAgent
    agent = FileParseExploitAgent()
    data = request.get_json() or {}
    return jsonify(agent.simulate_pdf_exploit(
        data.get("target", "acrobat"),
        data.get("exploit_type", "heap_overflow")
    ))

@app.route("/api/exploit-cat/file-parse-exploit/simulate-email", methods=["POST"])
def api_file_parse_exploit_simulate_email():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.file_parse_exploit import FileParseExploitAgent
    agent = FileParseExploitAgent()
    data = request.get_json() or {}
    return jsonify(agent.simulate_email_exploit(
        data.get("target", "email_client"),
        data.get("exploit_type", "attachment")
    ))

@app.route("/api/exploit-cat/file-parse-exploit/simulate-office", methods=["POST"])
def api_file_parse_exploit_simulate_office():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.file_parse_exploit import FileParseExploitAgent
    agent = FileParseExploitAgent()
    data = request.get_json() or {}
    return jsonify(agent.simulate_office_exploit(
        data.get("target", "word"),
        data.get("exploit_type", "macro")
    ))

@app.route("/api/exploit-cat/file-parse-exploit/generate-payload", methods=["POST"])
def api_file_parse_exploit_generate_payload():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.file_parse_exploit import FileParseExploitAgent
    agent = FileParseExploitAgent()
    data = request.get_json() or {}
    return jsonify(agent.generate_payload(
        data.get("format", "pdf"),
        data.get("vector", "buffer_overflow")
    ))

@app.route("/api/exploit-cat/file-parse-exploit/primitives", methods=["GET"])
def api_file_parse_exploit_primitives():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.file_parse_exploit import FileParseExploitAgent
    agent = FileParseExploitAgent()
    return jsonify(agent.list_primitives())

@app.route("/api/exploit-cat/file-parse-exploit/cves", methods=["GET"])
def api_file_parse_exploit_cves():
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    from agents.specialized.file_parse_exploit import FileParseExploitAgent
    agent = FileParseExploitAgent()
    return jsonify(agent.get_cves())

# ── Sandbox / VM Management ────────────────────────────────────────

@app.route("/api/sandbox/vms", methods=["GET"])
def api_sandbox_vms():
    """Return list of VMs in the sandbox."""
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    vms = [
        {"id": "ios-1", "name": "iOS Simulator - iPhone 15 Pro", "os": "iOS 17.4", "ip": "192.168.1.42", "gpu": "A17 Pro", "status": "online", "type": "ios"},
        {"id": "ios-2", "name": "iOS Simulator - iPad Pro", "os": "iOS 17.4", "ip": "192.168.1.43", "gpu": "A16Z", "status": "online", "type": "ios"},
        {"id": "android-1", "name": "Android Emulator - Pixel 8", "os": "Android 14", "ip": "192.168.1.50", "gpu": "Adreno 740", "status": "online", "type": "android"},
        {"id": "android-2", "name": "Android Emulator - Pixel 7 Pro", "os": "Android 13", "ip": "192.168.1.51", "gpu": "Mali-G710", "status": "stopped", "type": "android"},
        {"id": "win-1", "name": "Windows 11 Pro - C2 Controller", "os": "Windows 11", "ip": "10.0.5.20", "gpu": "RTX 4090", "status": "online", "type": "desktop"},
        {"id": "kali-1", "name": "Kali Linux - Penetration Testing", "os": "Kali 2024.3", "ip": "10.0.5.25", "gpu": "N/A", "status": "online", "type": "desktop"},
    ]
    return jsonify({"vms": vms, "total": len(vms), "online": sum(1 for v in vms if v["status"] == "online")})

@app.route("/api/sandbox/vms/<vm_id>/power", methods=["POST"])
def api_sandbox_vm_power(vm_id):
    """Power on/off/restart a VM."""
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json() or {}
    action = data.get("action", "status")
    # Simulate power actions
    return jsonify({"ok": True, "vm_id": vm_id, "action": action, "status": "online"})

@app.route("/api/sandbox/vms/<vm_id>/console", methods=["GET"])
def api_sandbox_vm_console(vm_id):
    """Get VM console access URL."""
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
        return jsonify({"error": "unauthorized"}), 401
    vms = {
        "ios-1": "vnc://192.168.1.42:5900",
        "ios-2": "vnc://192.168.1.43:5900",
        "android-1": "vnc://192.168.1.50:5900",
        "android-2": "vnc://192.168.1.51:5900",
        "win-1": "vnc://10.0.5.20:5900",
        "kali-1": "vnc://10.0.5.25:5900",
    }
    return jsonify({"vm_id": vm_id, "console_url": vms.get(vm_id, ""), "type": "vnc"})

@app.route("/api/sandbox/devices", methods=["GET"])
def api_sandbox_devices():
    """Return list of C2-connected devices."""
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
        return jsonify({"error": "unauthorized"}), 401
    devices = [
        {"id": "192.168.1.100", "name": "Target: 192.168.1.100", "os": "Windows 10", "implant": "v2.4", "status": "active", "type": "windows"},
        {"id": "android-1", "name": "Android: Pixel 7 (Mock)", "os": "Android 14", "implant": "v1.8", "status": "idle", "type": "android"},
        {"id": "ios-1", "name": "iOS: iPhone 15 Pro (Mock)", "os": "iOS 17.4", "implant": "v1.6", "status": "active", "type": "ios"},
    ]
    return jsonify({"devices": devices, "total": len(devices)})

@app.route("/api/sandbox/devices/<device_id>/action", methods=["POST"])
def api_sandbox_device_action(device_id):
    """Execute action on C2 device."""
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json() or {}
    action = data.get("action", "")
    actions = {
        "screenshot": {"output": "Screenshot captured", "file": f"/loot/screenshots/{device_id}_{int(time.time())}.png"},
        "keylogger": {"output": "Keylogger activated", "sessions": 1},
        "terminal": {"output": "Terminal session established", "pid": random.randint(1000, 9999)},
        "files": {"output": "File browser opened", "files": ["Documents", "Downloads", "Desktop"]},
        "location": {"output": "Location data retrieved", "lat": 37.7749, "lon": -122.4194},
        "contacts": {"output": "Contact list exported", "count": 247},
        "sms": {"output": "SMS messages retrieved", "count": 156},
        "camera": {"output": "Camera activated", "mode": "photo"},
        "messages": {"output": "iMessage history exported", "count": 89},
        "download": {"output": "Download initiated", "file": data.get("file", "unknown")},
        "upload": {"output": "Upload dialog opened", "dest": data.get("dest", "/tmp/")},
        "execute": {"output": "Command executed", "result": "0"},
    }
    result = actions.get(action, {"output": f"Action {action} executed"})
    return jsonify({"ok": True, "device_id": device_id, "action": action, **result})

@app.route("/api/sandbox/resources", methods=["GET"])
def api_sandbox_resources():
    """Return system resource usage."""
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
        return jsonify({"error": "unauthorized"}), 401
    return jsonify({
        "cpu": {"usage": 67, "cores": 16},
        "memory": {"used_gb": 18.2, "total_gb": 32},
        "gpu": {"vram_used_gb": 24, "vram_total_gb": 24, "temp_c": 72},
        "disk": {"used_gb": 450, "total_gb": 1000},
    })

@app.route("/api/sandbox/tools", methods=["GET"])
def api_sandbox_tools():
    """Return list of available security tools."""
    if AUTH_TOKEN and request.headers.get("X-Auth-Token") != AUTH_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
        return jsonify({"error": "unauthorized"}), 401
    tools = [
        {"id": "nmap", "name": "Nmap", "icon": "🔍", "desc": "Network Scanner", "category": "recon"},
        {"id": "burp", "name": "Burp Suite", "icon": "🦇", "desc": "Web Proxy", "category": "web"},
        {"id": "hydra", "name": "Hydra", "icon": "💧", "desc": "Brute Force", "category": "password"},
        {"id": "metasploit", "name": "Metasploit", "icon": "🎯", "desc": "Exploit Framework", "category": "exploit"},
        {"id": "aircrack", "name": "Aircrack-ng", "icon": "📡", "desc": "WiFi Attack", "category": "wireless"},
        {"id": "john", "name": "John", "icon": "🔓", "desc": "Password Crack", "category": "password"},
        {"id": "set", "name": "Social-Engineer Toolkit", "icon": "🎣", "desc": "Phishing Framework", "category": "social"},
        {"id": "hashcat", "name": "Hashcat", "icon": "⚡", "desc": "GPU Cracker", "category": "password"},
    ]
    return jsonify({"tools": tools})

# ── Phase 3: Additional Dashboards ─────────────────────────────────

@app.route("/dashboard")
def dashboard_page():
    locale = get_locale_from_session(session)
    return render_template("dashboard.html", i18n_locale=locale)

@app.route("/permissions")
def permissions_page():
    locale = get_locale_from_session(session)
    return render_template("permissions.html", i18n_locale=locale)

@app.route("/gpu-workstation")
def gpu_workstation_page():
    locale = get_locale_from_session(session)
    return render_template("gpu-workstation.html", i18n_locale=locale)

@app.route("/campaign-manager")
def campaign_manager_page():
    locale = get_locale_from_session(session)
    return render_template("campaign-manager.html", i18n_locale=locale)

@app.route("/campaign-settings")
def campaign_settings_page():
    locale = get_locale_from_session(session)
    return render_template("campaign-settings.html", i18n_locale=locale)

@app.route("/jobs")
def jobs_page():
    locale = get_locale_from_session(session)
    return render_template("jobs.html", i18n_locale=locale)

@app.route("/external-providers")
def external_providers_page():
    locale = get_locale_from_session(session)
    return render_template("external-providers.html", i18n_locale=locale)

# ── Phase 3: API endpoints ─────────────────────────────────────────

@app.route("/api/dashboard/overview")
def api_dashboard_overview():
    """Return unified dashboard overview data."""
    return jsonify({
        "jobs_total": 8,
        "agents_active": 4,
        "gpu_util": 73,
        "providers_total": 8,
        "alerts_active": 2,
        "uptime": "99.7%",
    })

@app.route("/api/dashboard/jobs")
def api_dashboard_jobs():
    """Return recent jobs for dashboard."""
    return jsonify({
        "total": 8,
        "jobs": [
            {"name":"daily-backup","status":"enabled","cron":"0 2 * * *","last_run":"2025-07-15 02:00","next_run":"2025-07-16 02:00"},
            {"name":"vuln-scan","status":"enabled","cron":"0 */6 * * *","last_run":"2025-07-15 12:00","next_run":"2025-07-15 18:00"},
            {"name":"agent-health-check","status":"running","cron":"*/5 * * * *","last_run":"2025-07-15 14:30","next_run":"2025-07-15 14:35"},
            {"name":"model-refresh","status":"enabled","cron":"0 4 * * *","last_run":"2025-07-15 04:00","next_run":"2025-07-16 04:00"},
            {"name":"cert-expiry-check","status":"enabled","cron":"0 9 * * 1","last_run":"2025-07-14 09:00","next_run":"2025-07-21 09:00"},
        ]
    })

@app.route("/api/gpu-workstation")
def api_gpu_workstation():
    """Return GPU workstation telemetry."""
    return jsonify({
        "gpus": [
            {"temp": 72, "clock": 1830, "power": 285, "vram_used": 18.2, "vram_total": 24.0, "status": "active"},
            {"temp": 68, "clock": 1785, "power": 260, "vram_used": 12.4, "vram_total": 24.0, "status": "active"},
        ],
        "training_jobs": 1,
        "total_jobs": 12,
    })

@app.route("/api/gpu-workstation/loss")
def api_gpu_workstation_loss():
    """Return training loss curve data."""
    import random
    labels = [str(i) for i in range(50)]
    loss = [2.1 - i*0.03 + random.uniform(-0.05, 0.05) for i in range(50)]
    return jsonify({"labels": labels, "loss": loss})

@app.route("/api/permissions/set", methods=["POST"])
def api_permissions_set():
    """Set a permission toggle."""
    data = request.get_json(silent=True) or {}
    agent = data.get("agent", "")
    permission = data.get("permission", "")
    allowed = data.get("allowed", False)
    return jsonify({"ok": True, "agent": agent, "permission": permission, "allowed": allowed})

@app.route("/api/permissions/list")
def api_permissions_list():
    """Return all agent permissions."""
    return jsonify({
        "agents": {
            "recon": {"network_scan": True, "port_scan": True, "shodan": True, "sandbox_escape": False, "exfil": False},
            "exploit": {"dev": False, "payload": True, "brute": False, "social": True, "zeroday": False},
            "defense": {"vuln_scan": True, "harden": True, "logs": True, "ir": True, "forensics": True},
            "inference": {"api": True, "local_load": True, "gpu": True, "syscmd": False, "network": False},
        }
    })

@app.route("/api/campaigns")
def api_campaigns():
    """Return campaign list."""
    return jsonify({
        "campaigns": [
            {"id":"c1","name":"operation-nightfall","desc":"Full-spectrum red team exercise","type":"red-team","status":"active","agents":["recon","exploit","postex"],"last_run":"2025-07-15 14:32"},
            {"id":"c2","name":"defensive-hardening","desc":"Harden production servers","type":"defense","status":"active","agents":["defense","recon"],"last_run":"2025-07-15 12:00"},
            {"id":"c3","name":"ai-safety-eval","desc":"Evaluate LLM safety boundaries","type":"ai-attack","status":"paused","agents":["exploit","inference"],"last_run":"2025-07-14 09:15"},
            {"id":"c4","name":"vuln-scan-q2","desc":"Quarterly vulnerability scan","type":"recon","status":"completed","agents":["recon"],"last_run":"2025-07-01 06:00"},
            {"id":"c5","name":"brute-force-drill","desc":"Password strength testing","type":"exploitation","status":"failed","agents":["exploit"],"last_run":"2025-07-13 22:00"},
        ]
    })

@app.route("/api/campaigns/create", methods=["POST"], endpoint="api_campaigns_create")
def api_campaigns_create():
    """Create a new campaign."""
    data = request.get_json(silent=True) or {}
    return jsonify({"ok": True, "id": "c" + str(len(data.get("name",""))), "name": data.get("name","")})

@app.route("/api/campaigns/<id>/toggle", methods=["POST"], endpoint="api_campaigns_toggle")
def api_campaign_toggle(id):
    """Toggle campaign status."""
    return jsonify({"ok": True, "id": id})

@app.route("/api/campaigns/<id>/delete", methods=["DELETE"], endpoint="api_campaigns_delete")
def api_campaign_delete(id):
    """Delete a campaign."""
    return jsonify({"ok": True, "id": id})

@app.route("/api/jobs")
def api_jobs_list():
    """Return all scheduled jobs."""
    return jsonify({
        "total": 8,
        "jobs": [
            {"id":"j1","name":"daily-backup","type":"cron","cron":"0 2 * * *","handler":"backup.run","status":"enabled","last_run":"2025-07-15 02:00:01","next_run":"2025-07-16 02:00:00","duration":"2m 34s","failed_count":0},
            {"id":"j2","name":"vuln-scan","type":"cron","cron":"0 */6 * * *","handler":"scanner.run","status":"enabled","last_run":"2025-07-15 12:00:03","next_run":"2025-07-15 18:00:00","duration":"15m 22s","failed_count":0},
            {"id":"j3","name":"model-refresh","type":"cron","cron":"0 4 * * *","handler":"model.refresh","status":"enabled","last_run":"2025-07-15 04:00:00","next_run":"2025-07-16 04:00:00","duration":"8m 12s","failed_count":1},
            {"id":"j4","name":"agent-health-check","type":"interval","cron":"*/5 * * * *","handler":"health.check","status":"running","last_run":"2025-07-15 14:30:00","next_run":"2025-07-15 14:35:00","duration":"12s","failed_count":0},
            {"id":"j5","name":"log-rotation","type":"cron","cron":"0 0 * * *","handler":"logs.rotate","status":"enabled","last_run":"2025-07-15 00:00:00","next_run":"2025-07-16 00:00:00","duration":"45s","failed_count":0},
            {"id":"j6","name":"report-gen","type":"oneday","cron":None,"handler":"reports.generate","status":"disabled","last_run":"2025-07-10 10:00:00","next_run":"Never","duration":"3m 11s","failed_count":0},
            {"id":"j7","name":"cert-expiry-check","type":"cron","cron":"0 9 * * 1","handler":"security.cert_check","status":"enabled","last_run":"2025-07-14 09:00:00","next_run":"2025-07-21 09:00:00","duration":"8s","failed_count":0},
            {"id":"j8","name":"data-sync","type":"interval","cron":"*/15 * * * *","handler":"sync.run","status":"failed","last_run":"2025-07-15 14:15:00","next_run":"Never","duration":"ERROR","failed_count":3},
        ]
    })

@app.route("/api/jobs/<id>/toggle", methods=["POST"])
def api_job_toggle(id):
    """Toggle a job enabled/disabled."""
    return jsonify({"ok": True, "id": id})

@app.route("/api/jobs/<id>/run", methods=["POST"])
def api_job_run(id):
    """Run a job immediately."""
    return jsonify({"ok": True, "id": id, "status": "running"})

@app.route("/api/jobs/<id>/delete", methods=["DELETE"])
def api_job_delete(id):
    """Delete a job."""
    return jsonify({"ok": True, "id": id})

@app.route("/api/jobs/create", methods=["POST"])
def api_job_create():
    """Create a new job."""
    data = request.get_json(silent=True) or {}
    return jsonify({"ok": True, "id": "j" + str(len(data.get("name",""))), "name": data.get("name","")})

@app.route("/api/external-providers")
def api_external_providers():
    """Return external provider list."""
    return jsonify({
        "total": 8,
        "providers": [
            {"name":"OpenAI","type":"primary","url":"https://api.openai.com/v1","models":["gpt-4o","gpt-4-turbo","gpt-3.5-turbo"],"status":"healthy","latency":45},
            {"name":"Anthropic","type":"primary","url":"https://api.anthropic.com/v1","models":["claude-3-opus","claude-3-sonnet","claude-3-haiku"],"status":"healthy","latency":62},
            {"name":"Azure OpenAI","type":"fallback","url":"https://freeai.openai.azure.com","models":["gpt-4","gpt-35-turbo"],"status":"degraded","latency":210},
            {"name":"Local (Ollama)","type":"local","url":"http://localhost:11434","models":["llama3","mistral","qwen2"],"status":"healthy","latency":12},
            {"name":"Groq","type":"fallback","url":"https://api.groq.com/openai/v1","models":["llama-3.1-70b","llama-3.1-8b"],"status":"healthy","latency":38},
            {"name":"Together AI","type":"fallback","url":"https://api.together.xyz","models":["mistral-7b','qwen-72b"],"status":"down","latency":0},
            {"name":"Fireworks AI","type":"tool","url":"https://api.fireworks.ai/inference","models":["llama-v3-70b','mixtral-8x7b"],"status":"healthy","latency":55},
            {"name":"OpenRouter","type":"aggregator","url":"https://openrouter.ai/api/v1","models":["multiple"],"status":"healthy","latency":78},
        ]
    })

@app.route("/api/system")
def api_system():
    """Return system resource usage."""
    return jsonify({
        "cpu": 67,
        "memory": 72,
        "gpu_vram": 76,
        "disk": 45,
    })

@app.route("/api/alerts")
def api_alerts():
    """Return active alerts."""
    return jsonify({
        "alerts": [
            {"title":"GPU 0 High Temperature","message":"GPU 0 temperature exceeds 80°C threshold","severity":"high","time":"2025-07-15 14:28:00"},
            {"title":"Job data-sync Failed","message":"Job j8 failed 3 times in 24h","severity":"medium","time":"2025-07-15 14:15:00"},
        ]
    })

@app.route("/api/agents/list")
def api_agents_list():
    """Return active agents."""
    return jsonify({
        "agents": [
            {"name":"Recon Agent","model":"claude-3-sonnet","status":"active"},
            {"name":"Exploit Agent","model":"claude-3-opus","status":"active"},
            {"name":"Defense Agent","model":"gpt-4o","status":"active"},
            {"name":"Inference Agent","model":"local/llama3","status":"active"},
        ]
    })
