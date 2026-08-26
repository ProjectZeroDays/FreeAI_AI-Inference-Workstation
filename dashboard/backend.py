#!/usr/bin/env python3
"""FreeAI Dashboard — GPU telemetry, service health, alerts."""
import json
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request

from flask import Flask, jsonify, request, send_from_directory, Response

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)

AUTH_TOKEN = os.environ.get("DASHBOARD_AUTH_TOKEN", "").strip()
UPLOAD_DIR = os.environ.get(
    "UPLOAD_DIR", os.path.join(ROOT_DIR, "uploads"))
UPLOAD_MAX_MB = int(os.environ.get("UPLOAD_MAX_MB", "100"))
SAFE_NAME = re.compile(r"[^A-Za-z0-9._-]")


def _read_version():
    try:
        with open(os.path.join(ROOT_DIR, "VERSION")) as f:
            return f.read().strip()
    except OSError:
        return "dev"


APP_VERSION = _read_version()

# bumped on every settings/preset write; SSE clients watch this
_SETTINGS_VERSION = {"v": 1}


def bump_settings_version():
    _SETTINGS_VERSION["v"] += 1

sys.path.insert(0, ROOT_DIR)
try:
    from agents.resource_optimizer import (
        SETTINGS_DEFAULTS, load_settings as _load_opt_settings,
        save_settings as _save_opt_settings, SETTINGS_PATH as OPT_SETTINGS_PATH,
        BUILTIN_PRESETS, get_builtin_preset,
    )
except Exception:  # pragma: no cover - standalone fallback
    SETTINGS_DEFAULTS = {
        "auto_management": True, "forced_mode": "balanced",
        "power_limit_w": 240, "locked_clock_mhz": 2520,
        "eco_power_w": 200, "eco_clock_mhz": 2400,
        "repeat_penalty": 1.05, "repeat_last_n": 64, "llama_ctx": 4096,
        "max_concurrent_runs": 3,
    }
    OPT_SETTINGS_PATH = os.path.join(ROOT_DIR, "config",
                                     "runtime-settings.json")
    BUILTIN_PRESETS, get_builtin_preset = [], lambda n: None

    def _load_opt_settings():
        return dict(SETTINGS_DEFAULTS)

    def _save_opt_settings(s):
        os.makedirs(os.path.dirname(OPT_SETTINGS_PATH), exist_ok=True)
        with open(OPT_SETTINGS_PATH, "w") as f:
            json.dump(s, f, indent=2)

VALID_MODES = ("performance", "balanced", "eco")
LLAMA_ENV_PATH = os.path.join(ROOT_DIR, "config", "llama.env")
GPU_TUNE_SCRIPT = os.path.join(ROOT_DIR, "hardware", "gpu-power-tune.sh")
PRESETS_PATH = os.path.join(ROOT_DIR, "config", "presets.json")
ROUTER_PORT = int(os.environ.get("ROUTER_PORT", "8010"))
AUTON_PORT = int(os.environ.get("AUTONOMOUS_PORT", "8050"))

# field -> (low, high) inclusive bounds; repeat_penalty handled apart
FIELD_BOUNDS = {"power_limit_w": (150, 350),
                "locked_clock_mhz": (2000, 2900),
                "eco_power_w": (120, 350),
                "eco_clock_mhz": (1800, 2900),
                "repeat_last_n": (8, 2048),
                "llama_ctx": (512, 32768),
                "max_concurrent_runs": (1, 16)}

# keys a preset is allowed to carry
PRESET_KEYS = ("auto_management", "forced_mode",
               *FIELD_BOUNDS.keys(), "repeat_penalty")

try:
    from settings import load_config
    _CFG = load_config().get("dashboard", {})
except ImportError:
    _CFG = {}

PORT = int(_CFG.get("port", os.environ.get("DASHBOARD_PORT", 8030)))
GPU_TEMP_ALERT_C = int(_CFG.get("gpu_temp_alert_c", 85))
GPU_UTIL_ALERT_PCT = int(_CFG.get("gpu_util_alert_pct", 90))

app = Flask(__name__,
            static_folder=os.path.join(BASE_DIR, "static"),
            template_folder=os.path.join(BASE_DIR, "templates"))


@app.after_request
def security_headers(resp):
    resp.headers.setdefault("X-Content-Type-Options", "nosniff")
    resp.headers.setdefault("X-Frame-Options", "DENY")
    resp.headers.setdefault("Referrer-Policy", "same-origin")
    return resp


# ------------------------------------------------------- auth + uploads
WRITE_PATHS = ("/api/settings", "/api/presets",
               "/api/settings/llama-restart")


@app.before_request
def auth_gate():
    """Token-gate all writes (POST/DELETE/PUT) when DASHBOARD_AUTH_TOKEN
    is set. Reads stay open for LAN dashboards; SSE stays open so live
    panels keep working for viewers."""
    if not AUTH_TOKEN:
        return None
    if request.method in ("POST", "DELETE", "PUT"):
        if request.headers.get("X-Auth-Token") != AUTH_TOKEN:
            return jsonify({"error": "unauthorized"}), 401
    return None


@app.route("/api/upload", methods=["POST"])
def upload():
    f = request.files.get("file")
    if f is None:
        return jsonify({"error": "multipart file field required"}), 400
    name = SAFE_NAME.sub("_", os.path.basename(f.filename)) or "upload.bin"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    dest = os.path.join(UPLOAD_DIR, name)
    f.save(dest)
    size = os.path.getsize(dest)
    if size > UPLOAD_MAX_MB * 1024 * 1024:
        os.remove(dest)
        return jsonify({"error": f"exceeds {UPLOAD_MAX_MB}MB"}), 413
    return jsonify({"status": "saved", "name": name, "bytes": size})


@app.route("/api/uploads")
def uploads():
    out = []
    if os.path.isdir(UPLOAD_DIR):
        for n in sorted(os.listdir(UPLOAD_DIR)):
            p = os.path.join(UPLOAD_DIR, n)
            if os.path.isfile(p):
                out.append({"name": n, "bytes": os.path.getsize(p)})
    return jsonify({"uploads": out})


@app.route("/api/runs")
def sdlc_runs():
    """Proxy autonomous SDLC run list (graceful when service is down)."""
    try:
        with urllib.request.urlopen(
                f"http://127.0.0.1:{AUTON_PORT}/auto/runs",
                timeout=3) as resp:
            data = json.loads(resp.read().decode())
        return jsonify(data)
    except Exception as exc:
        return jsonify({"runs": [], "offline": str(exc)[:120]})


@app.route("/api/clients")
def clients():
    """Client switchboard: mimocode/clients.json (+ desktop.json)."""
    entries = []
    base = os.path.join(ROOT_DIR, "mimocode")
    for fname, key in (("clients.json", "clients"),
                       ("desktop.json", None)):
        try:
            with open(os.path.join(base, fname)) as f:
                data = json.load(f)
            items = data.get(key) if key else [data]
            for c in items or []:
                entries.append({
                    "id": c.get("id"), "name": c.get("name"),
                    "port": c.get("port"), "enabled": c.get("enabled", True),
                    "url": c.get("url"),
                })
        except (OSError, ValueError):
            continue
    return jsonify({"clients": entries})


# ---------------------------------------------------- external providers
def _list_providers():
    sys.path.insert(0, ROOT_DIR)
    from router.providers import load_providers, is_keyed
    rows = []
    for name, cfg in load_providers().items():
        if not cfg.get("enabled"):
            continue
        rows.append({
            "name": name,
            "style": cfg.get("style", "openai"),
            "base_url": cfg.get("base_url", ""),
            "description": cfg.get("description", ""),
            "models": cfg.get("models", []),
            "keyed": is_keyed(name, cfg),
            "fallback": bool(cfg.get("fallback")),
            "key_env": cfg.get("key_env"),
        })
    return rows


@app.route("/api/providers")
def providers_list():
    return jsonify({"providers": _list_providers()})


@app.route("/api/providers/test", methods=["POST"])
def providers_test():
    body = request.get_json(silent=True) or {}
    name = body.get("name", "")
    sys.path.insert(0, ROOT_DIR)
    from router.providers import load_providers, is_keyed, call_provider
    cfg = load_providers().get(name)
    if not cfg:
        return jsonify({"error": "unknown provider"}), 404
    if not is_keyed(name, cfg):
        return jsonify({"error": f"no API key ({cfg.get('key_env')})"}), 400
    model = (cfg.get("models") or ["gpt-4o-mini"])[0]
    started = time.time()
    try:
        result = call_provider(name, cfg, model,
                               "Reply with the single word: pong",
                               max_tokens=8, temperature=0.0, timeout=30)
        return jsonify({"ok": True, "model": model,
                        "latency_ms": int((time.time() - started) * 1000),
                        "reply": (result.get("content") or "")[:80]})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)[:300]}), 502

_GPU_FIELDS = ("utilization.gpu,memory.used,memory.total,"
               "temperature.gpu,power.draw,clocks.current.sm")


def get_gpu_stats():
    try:
        out = subprocess.check_output(
            ["nvidia-smi", f"--query-gpu={_GPU_FIELDS}",
             "--format=csv,noheader,nounits"],
            stderr=subprocess.DEVNULL,
        ).decode().strip()
        parts = [x.strip() for x in out.split(",")]
        util, used, total, temp, power, clock = (
            parts + ["0"] * 6)[:6]

        def _num(v):
            try:
                return float(v)
            except ValueError:
                return 0.0

        return {
            "utilization": int(float(util)),
            "memory_used": int(float(used)),
            "memory_total": int(float(total)),
            "temperature": int(float(temp)),
            "power_watts": round(_num(power), 1),
            "clock_mhz": int(float(clock)),
        }
    except Exception:
        return {"utilization": 0, "memory_used": 0, "memory_total": 0,
                "temperature": 0, "power_watts": 0.0, "clock_mhz": 0}


def listening_ports():
    try:
        out = subprocess.check_output(
            ["ss", "-tuln"], stderr=subprocess.DEVNULL).decode()
    except Exception:
        out = ""

    def up(port):
        return f":{port}" in out

    base = {
        "router": up(8010),
        "agents": up(8020),
        "dashboard": up(PORT),
        "workflow": up(8040),
        "llama": up(9001),
        "vllm": up(9002),
    }
    # optional edge services — reported but not alert-critical unless enabled
    base.update({
        "autonomous": up(8050),
        "freetoken": up(9100),
        "lollms": up(9600),
        "jupyter": up(8888),
        "opencode": up(3000),
        "zcode": up(5000),
    })
    return base


_CORE_SERVICES = {"router", "agents", "dashboard", "workflow", "llama"}


def build_alerts(services, gpu):
    alerts = []
    down = [name for name, ok in services.items()
            if not ok and name in _CORE_SERVICES]
    if down:
        alerts.append({"level": "critical",
                       "message": f"services down: {', '.join(down)}"})
    if gpu.get("utilization", 0) >= GPU_UTIL_ALERT_PCT:
        alerts.append({"level": "warning",
                       "message": f"GPU utilization "
                                  f"{gpu['utilization']}% >= "
                                  f"{GPU_UTIL_ALERT_PCT}%"})
    if gpu.get("temperature", 0) >= GPU_TEMP_ALERT_C:
        alerts.append({"level": "critical",
                       "message": f"GPU temperature "
                                  f"{gpu['temperature']}C >= "
                                  f"{GPU_TEMP_ALERT_C}C"})
    return alerts


@app.route("/api/status")
def status():
    gpu = get_gpu_stats()
    services = listening_ports()
    body = {
        "timestamp": int(time.time()),
        "version": APP_VERSION,
        "gpu": gpu,
        "services": services,
        "alerts": build_alerts(services, gpu),
        "router_metrics": _fetch_router_metrics(),
    }
    state_path = os.path.join(ROOT_DIR,
                              "config", "runtime-state.json")
    try:
        with open(state_path) as f:
            body["power_mode"] = json.load(f).get("mode", "balanced")
    except (OSError, ValueError):
        body["power_mode"] = "balanced"
    return jsonify(body)


def _fetch_router_metrics():
    try:
        with urllib.request.urlopen(
                f"http://127.0.0.1:{ROUTER_PORT}/metrics",
                timeout=2) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return None


@app.route("/api/models-status")
def models_status():
    """Registry models vs what is actually on disk + free space."""
    registry = os.path.join(ROOT_DIR, "registry", "registry.json")
    models_dir = os.path.join(ROOT_DIR, "models")
    entries = []
    try:
        with open(registry) as f:
            models = json.load(f).get("models", [])
        on_disk = {}
        if os.path.isdir(models_dir):
            for name in os.listdir(models_dir):
                if name.endswith(".gguf"):
                    p = os.path.join(models_dir, name)
                    on_disk[name] = os.path.getsize(p)
        for m in models:
            fname = os.path.basename(m.get("gguf", ""))
            size = on_disk.pop(fname, None)
            entries.append({"id": m.get("key") or m.get("id"),
                            "name": m.get("name"),
                            "gguf": fname or None,
                            "present": size is not None,
                            "size_bytes": size})
    except (OSError, ValueError) as exc:
        return jsonify({"error": str(exc), "models": entries})
    extra = [{"id": n, "name": n, "gguf": n, "present": True,
              "size_bytes": s} for n, s in sorted(on_disk.items())]
    free_gb = 0
    if os.path.isdir(models_dir):
        free_gb = round(shutil.disk_usage(models_dir).free / 1e9, 1)
    return jsonify({"models": entries + extra, "disk_free_gb": free_gb,
                    "version": APP_VERSION})


@app.route("/api/events")
def events():
    """SSE: pushes a settings-changed event whenever the version bumps."""
    def gen():
        last = _SETTINGS_VERSION["v"]
        yield f"data: {json.dumps({'v': last, 'type': 'hello'})}\n\n"
        deadline = time.time() + 300          # client auto-reconnects
        while time.time() < deadline:
            time.sleep(1)
            if _SETTINGS_VERSION["v"] != last:
                last = _SETTINGS_VERSION["v"]
                yield f"data: {json.dumps({'type': 'settings-changed', 'v': last})}\n\n"
                deadline = time.time() + 300
        yield f"data: {json.dumps({'type': 'refresh'})}\n\n"

    return Response(gen(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache",
                             "X-Accel-Buffering": "no"})


# ----------------------------------------------------------- settings API

def _validate_and_merge(base, body):
    """Merge validated preset/settings fields from body onto base.
    Returns (merged, error_response_or_None)."""
    merged = dict(base)
    if "auto_management" in body:
        merged["auto_management"] = bool(body["auto_management"])
    if "forced_mode" in body:
        if body["forced_mode"] not in VALID_MODES:
            return None, ({"error": "invalid forced_mode"}, 400)
        merged["forced_mode"] = body["forced_mode"]
    for field, (lo, hi) in FIELD_BOUNDS.items():
        if field in body:
            try:
                val = int(body[field])
            except (TypeError, ValueError):
                return None, ({"error": f"{field} must be numeric"}, 400)
            if not lo <= val <= hi:
                return None, (
                    {"error": f"{field} must be {lo}-{hi}"}, 400)
            merged[field] = val
    if "repeat_penalty" in body:
        try:
            val = float(body["repeat_penalty"])
        except (TypeError, ValueError):
            return None, ({"error": "repeat_penalty must be numeric"}, 400)
        if not 1.0 <= val <= 2.0:
            return None, ({"error": "repeat_penalty must be 1.0-2.0"}, 400)
        merged["repeat_penalty"] = val
    return merged, None


def _load_custom_presets():
    try:
        with open(PRESETS_PATH) as f:
            data = json.load(f)
        return data.get("presets", []) if isinstance(data, dict) else []
    except (OSError, ValueError):
        return []


def _save_custom_presets(presets):
    os.makedirs(os.path.dirname(PRESETS_PATH), exist_ok=True)
    with open(PRESETS_PATH, "w") as f:
        json.dump({"presets": presets}, f, indent=2)


@app.route("/api/presets")
def list_presets():
    return jsonify({
        "builtins": BUILTIN_PRESETS,
        "customs": _load_custom_presets(),
    })


@app.route("/api/presets", methods=["POST"])
def create_preset():
    body = request.get_json(silent=True) or {}
    name = str(body.get("name", "")).strip()
    if not name or len(name) > 48 or "/" in name:
        return jsonify({"error": "name required (max 48 chars)"}), 400
    if get_builtin_preset(name):
        return jsonify({"error": "cannot shadow a built-in preset"}), 400

    merged, err = _validate_and_merge(
        {k: SETTINGS_DEFAULTS[k] for k in PRESET_KEYS},
        body.get("settings", {}))
    if err:
        return jsonify(err[0]), err[1]

    presets = [p for p in _load_custom_presets()
               if p.get("name") != name]
    presets.append({"name": name, "builtin": False,
                    "description": str(body.get("description", "")
                                       )[:200],
                    "settings": merged})
    _save_custom_presets(presets)
    return jsonify({"status": "saved", "preset":
                    presets[-1]}), 201


@app.route("/api/presets/<path:name>", methods=["DELETE"])
def delete_preset(name):
    presets = _load_custom_presets()
    remaining = [p for p in presets if p.get("name") != name]
    if len(remaining) == len(presets):
        return jsonify({"error": "custom preset not found"}), 404
    _save_custom_presets(remaining)
    return jsonify({"status": "deleted"})


@app.route("/api/presets/<path:name>/apply", methods=["POST"])
def apply_preset(name):
    body = request.get_json(silent=True) or {}
    duration_min = body.get("duration_min")
    preset = get_builtin_preset(name)
    if preset is None:
        preset = next((p for p in _load_custom_presets()
                       if p.get("name") == name), None)
    if preset is None:
        return jsonify({"error": "preset not found"}), 404

    current = _load_opt_settings()
    new_settings = dict(current)

    if duration_min is not None:
        # timed idle: snapshot current settings, activate window
        try:
            minutes = max(1, min(int(duration_min), 7 * 24 * 60))
        except (TypeError, ValueError):
            return jsonify({"error": "duration_min must be int"}), 400
        restore = {k: v for k, v in current.items() if k != "idle"}
        block = {
            "active": True,
            "until_epoch": time.time() + minutes * 60,
            "preset": name,
        }
        new_settings.update({k: v for k, v in
                             preset["settings"].items()})
        new_settings["idle"] = {"active": True,
                                "until_epoch": block["until_epoch"],
                                "restore": restore}
        applied_profile = "eco"
    else:
        new_settings.update({k: v for k, v in
                             preset["settings"].items()})
        new_settings.pop("idle", None)
        applied_profile = ("performance" if not new_settings.get(
            "auto_management", True)
            else new_settings.get("forced_mode", "balanced"))

    _save_opt_settings(new_settings)
    bump_settings_version()

    gpu_applied, gpu_err = True, ""
    if not new_settings.get("auto_management", True) \
            or duration_min is not None:
        tune = dict(new_settings)
        if duration_min is not None:
            tune["power_limit_w"] = preset["settings"].get(
                "eco_power_w", 200)
            tune["locked_clock_mhz"] = preset["settings"].get(
                "eco_clock_mhz", 2400)
        gpu_applied, gpu_err = _apply_gpu_tune(tune)

    resp = {"status": "applied", "preset": name,
            "gpu_applied": gpu_applied, "gpu_error": gpu_err}
    if duration_min is not None:
        resp["idle_minutes"] = duration_min
        resp["revert_at_epoch"] = new_settings["idle"]["until_epoch"]
    return jsonify(resp)


def _apply_gpu_tune(settings):
    """Apply power/clock caps via the tune script (patchable in tests)."""
    if not os.path.exists(GPU_TUNE_SCRIPT):
        return False, "gpu-power-tune.sh not found"
    env = dict(os.environ,
               GPU_POWER_LIMIT_W=str(settings["power_limit_w"]),
               GPU_LOCKED_CLOCK_MHZ=str(settings["locked_clock_mhz"]))
    try:
        proc = subprocess.run(["bash", GPU_TUNE_SCRIPT, "apply"],
                              env=env, capture_output=True,
                              text=True, timeout=30)
        return proc.returncode == 0, \
            ((proc.stderr or proc.stdout) or "")[-300:]
    except Exception as exc:
        return False, str(exc)


def _write_llama_env(settings):
    os.makedirs(os.path.dirname(LLAMA_ENV_PATH), exist_ok=True)
    lines = [
        f"LLAMA_CTX={int(settings['llama_ctx'])}",
        f"REPEAT_PENALTY={float(settings['repeat_penalty'])}",
        f"REPEAT_LAST_N={int(settings['repeat_last_n'])}",
    ]
    with open(LLAMA_ENV_PATH, "w") as f:
        f.write("\n".join(lines) + "\n")


def _restart_llama():
    """Prefer systemd; fall back to pkill (supervisor restarts it)."""
    try:
        proc = subprocess.run(
            ["systemctl", "restart", "freeai-stack.service"],
            capture_output=True, text=True, timeout=30)
        if proc.returncode == 0:
            return "systemd"
    except Exception:
        pass
    subprocess.run(["pkill", "-f", "llama-server"], capture_output=True)
    return "pkill"


@app.route("/api/settings")
def get_settings():
    mode_path = os.path.join(ROOT_DIR, "config", "runtime-state.json")
    current_mode = "balanced"
    try:
        with open(mode_path) as f:
            current_mode = json.load(f).get("mode", current_mode)
    except (OSError, ValueError):
        pass
    return jsonify({
        "settings": _load_opt_settings(),
        "defaults": SETTINGS_DEFAULTS,
        "current_power_mode": current_mode,
        "llama_restart_pending": os.path.exists(LLAMA_ENV_PATH),
        "version": APP_VERSION,
    })


@app.route("/api/settings", methods=["POST"])
def post_settings():
    body = request.get_json(silent=True) or {}
    settings, err = _validate_and_merge(_load_opt_settings(), body)
    if err:
        return jsonify(err[0]), err[1]

    _save_opt_settings(settings)
    bump_settings_version()

    # With auto-management ON the optimizer owns the GPU profile and
    # re-reads these caps next loop; OFF means apply right now.
    applied, gpu_err = True, ""
    if not settings["auto_management"]:
        applied, gpu_err = _apply_gpu_tune(settings)
    return jsonify({"status": "saved", "gpu_applied": applied,
                    "gpu_error": gpu_err})


@app.route("/api/settings/llama-restart", methods=["POST"])
def llama_restart():
    settings = _load_opt_settings()
    _write_llama_env(settings)
    method = _restart_llama()
    try:
        os.remove(LLAMA_ENV_PATH)   # consumed; clears pending flag
    except OSError:
        pass
    return jsonify({"status": "restarting", "method": method})


@app.route("/")
def index():
    return send_from_directory(app.template_folder, "index.html")


@app.route("/static/<path:path>")
def static_files(path):
    return send_from_directory(app.static_folder, path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
