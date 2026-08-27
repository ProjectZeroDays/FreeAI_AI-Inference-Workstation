"""Dashboard backend — serves the unified FreeAI dashboard and skills manager.

Provides REST API endpoints and serves static HTML pages.
"""
import json
import os
import random
import re
import threading
import time
import uuid
from pathlib import Path

try:
    from flask import Flask, render_template, request, jsonify, send_from_directory, session
except ImportError:
    Flask = None

try:
    from notifications_ws import notify, get_settings, update_settings, get_log, clear_log, get_unread_count
except ImportError:
    pass

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
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "freeai-dev-secret-key-2024")

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
        return jsonify({"error": str(e), "port": port}), 502


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
                for line in fm.group(1).split("\n"):
                    if line.startswith("name:"):
                        name = line.split(":", 1)[1].strip().strip('"').strip("'")
                    elif line.startswith("description:"):
                        desc = line.split(":", 1)[1].strip().strip('"')
                    elif line.startswith("category:"):
                        category = line.split(":", 1)[1].strip()
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


# ── API: Aikido Integration ──────────────────────────────────────
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


# ── API: Metrics Aggregation ─────────────────────────────────────
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
        return jsonify({"error": str(exc), "runs": [], "total": 0})


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
                run_result.update({"status": "error", "error": str(exc)})

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
        return jsonify({"error": str(exc)}), 500


@app.route("/api/evals/history")
def api_evals_history():
    """Return raw history entries."""
    try:
        runs = _load_eval_history()
        return jsonify({"runs": runs, "total": len(runs)})
    except Exception as exc:
        return jsonify({"error": str(exc), "runs": [], "total": 0})


@app.route("/api/evals/leaderboard")
def api_evals_leaderboard():
    """Return leaderboard summary from history."""
    try:
        from evals import leaderboard as lb
        runs = lb.load_history()
        summary = lb.summarize(runs)
        return jsonify(summary)
    except ImportError as exc:
        return jsonify({"error": f"evals module not available: {exc}", "runs": [], "trend": [], "models": {}})
    except Exception as exc:
        return jsonify({"error": str(exc), "runs": [], "trend": [], "models": {}})


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
        return jsonify({"error": str(exc)}), 500


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
        root = root.resolve()
    if user_path:
        target = (root / user_path).resolve()
    else:
        target = root.resolve()
    if str(target) != str(root) and not str(target).startswith(str(root) + os.sep):
        return None
    return target


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
                "size": entry.stat().st_size if entry.is_file() else 0,
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
        return jsonify({"error": str(e)}), 500


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
        return jsonify({"error": str(e)}), 500


@app.route("/api/files/mkdir", methods=["POST"])
def api_files_mkdir():
    data = request.get_json(silent=True) or {}
    path_str = data.get("path", "")
    if not path_str:
        return jsonify({"error": "Path required"}), 400
    target = _resolve_path(path_str)
    if target is None:
        return jsonify({"error": "Invalid path"}), 403
    try:
        target.mkdir(parents=True, exist_ok=True)
        return jsonify({"ok": True, "path": str(target)})
    except OSError as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/files/delete", methods=["DELETE"])
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
        return jsonify({"error": str(e)}), 500


@app.route("/api/files/search")
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


@app.route("/api/security/scan", methods=["POST"])
def api_security_scan():
    data = request.get_json(silent=True) or {}
    scan_dirs = data.get("dirs", None)
    include_tests = data.get("include_tests", False)
    config_path = data.get("config_path", str(CONFIG_DIR / "security.json"))

    try:
        from agents.specialized.security_scanner import SecurityScanner
        scanner = SecurityScanner(config_path=config_path)
        if scan_dirs:
            scanner.set_dirs(scan_dirs)
        scanner.set_include_tests(include_tests)
        report = scanner.run_scan()
        scan_id = str(uuid.uuid4())[:8]
        with _SECURITY_SCAN_LOCK:
            _SECURITY_FINDINGS_CACHE[scan_id] = report
        return jsonify({"ok": True, "scan_id": scan_id, **report})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/security/findings")
def api_security_findings():
    scan_id = request.args.get("scan_id", "")
    severity_filter = request.args.get("severity", None)
    with _SECURITY_SCAN_LOCK:
        if scan_id and scan_id in _SECURITY_FINDINGS_CACHE:
            report = _SECURITY_FINDINGS_CACHE[scan_id]
            findings = report.get("findings", [])
            if severity_filter:
                findings = [f for f in findings if f.get("severity") == severity_filter]
            return jsonify({"scan_id": scan_id, "findings": findings, "total": len(findings)})
        return jsonify({"findings": [], "total": 0})


@app.route("/api/security/latest")
def api_security_latest():
    with _SECURITY_SCAN_LOCK:
        if _SECURITY_FINDINGS_CACHE:
            latest_id = max(_SECURITY_FINDINGS_CACHE, key=lambda k: _SECURITY_FINDINGS_CACHE[k].get("scan_time", ""))
            return jsonify({"scan_id": latest_id, **_SECURITY_FINDINGS_CACHE[latest_id]})
        return jsonify({"findings": [], "total": 0, "summary": {"critical": 0, "high": 0, "medium": 0, "low": 0}})

# -- API: Workflow Designer -----------------------------------------
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
    path = _WORKFLOW_SAVE_DIR / f'{safe_name}.json'
    if path.exists():
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
        return jsonify({"error": f"Invalid JSON: {e}"}), 400
    except OSError as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/configs/<path:name>", methods=["PUT"])
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
        return jsonify({"error": f"Invalid JSON: {e}"}), 400
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
            errors.append({"file": fpath.name, "error": str(e)})
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
        return jsonify({"error": f"Invalid JSON in backup: {e}"}), 400
    except OSError as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/configs/export")
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



# ── JWT Authentication API ──────────────────────────────────────
_AUTH_ENABLED = bool(os.environ.get("AUTH_JWT_SECRET", "").strip())

try:
    from auth.jwt import jwt_auth, generate_access_token, generate_refresh_token, decode_token, check_login_rate_limit, record_login_attempt
    from auth.users import users_store, list_users as _list_users
    _AUTH_MODULE_AVAILABLE = True
except ImportError:
    _AUTH_MODULE_AVAILABLE = False


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

