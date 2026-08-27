"""Centralized error tracker for FreeAI services.

Logs unhandled exceptions to config/errors.jsonl with deduplication,
writes crash reports to config/crashes/, and auto-alerts on critical errors.
"""
import hashlib
import json
import os
import sys
import threading
import time
import traceback
from collections import defaultdict
from pathlib import Path

CONFIG_DIR = Path(__file__).parent.parent / "config"
ERRORS_LOG = CONFIG_DIR / "errors.jsonl"
CRASHES_DIR = CONFIG_DIR / "crashes"
ACK_FILE = CONFIG_DIR / "errors_ack.json"

CRITICAL_TYPES = {
    "ServiceCrash", "DatabaseError", "RuntimeError", "MemoryError",
    "OSError", "ConnectionError", "TimeoutError", "KeyError",
}

_lock = threading.Lock()
_dedup = {}
_acknowledged = set()

SERVICE_NAME = os.environ.get("FREEAI_SERVICE", "unknown")


def _hash_msg(msg):
    return hashlib.md5(msg.encode("utf-8")).hexdigest()[:12]


def _load_ack():
    global _acknowledged
    if ACK_FILE.exists():
        try:
            data = json.loads(ACK_FILE.read_text(encoding="utf-8"))
            _acknowledged = set(data.get("acknowledged", []))
        except (json.JSONDecodeError, OSError):
            pass


def _save_ack():
    ACK_FILE.parent.mkdir(parents=True, exist_ok=True)
    ACK_FILE.write_text(
        json.dumps({"acknowledged": list(_acknowledged), "updated_at": time.time()}, indent=2),
        encoding="utf-8",
    )


def _auto_alert(error_id, entry):
    kind = entry.get("kind", "")
    msg = entry.get("message", "")
    if kind == "crash" or entry.get("exception_type") in CRITICAL_TYPES:
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        alert_line = (
            f"[ALERT] {ts} — {entry.get('service', 'unknown')}: "
            f"{entry.get('exception_type', 'Error')}: {msg[:120]}\n"
        )
        try:
            alert_file = CONFIG_DIR / "alerts.log"
            alert_file.parent.mkdir(parents=True, exist_ok=True)
            with open(alert_file, "a", encoding="utf-8") as f:
                f.write(alert_line)
        except OSError:
            pass


def record(service, exc_type, exc_msg, traceback_str=None, request_info=None, kind="error"):
    """Log an error entry with deduplication."""
    with _lock:
        _load_ack()

    ts = int(time.time())
    err_id = f"{_hash_msg(f'{exc_type}:{exc_msg}')}:{ts}"
    dedup_key = f"{exc_type}:{_hash_msg(exc_msg)}"

    with _lock:
        if dedup_key in _dedup:
            _dedup[dedup_key]["count"] += 1
            _dedup[dedup_key]["last_seen"] = ts
            updated = _dedup[dedup_key]
        else:
            updated = {
                "id": err_id,
                "dedup_key": dedup_key,
                "count": 1,
                "first_seen": ts,
                "last_seen": ts,
                "service": service,
                "exception_type": exc_type,
                "message": exc_msg,
                "traceback": traceback_str or "",
                "request_info": request_info or {},
                "kind": kind,
                "acknowledged": False,
            }
            _dedup[dedup_key] = updated

    entry = dict(updated)
    entry["ts"] = ts

    ERRORS_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(ERRORS_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    if kind == "crash":
        _write_crash_report(service, exc_type, exc_msg, traceback_str or "")

    _auto_alert(err_id, entry)
    return entry


def _write_crash_report(service, exc_type, exc_msg, tb_str):
    """Write a detailed crash report to config/crashes/."""
    CRASHES_DIR.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    safe_svc = "".join(c if c.isalnum() else "_" for c in service)[:30]
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "unix_ts": int(time.time()),
        "service": service,
        "python_version": sys.version,
        "platform": sys.platform,
        "exception_type": exc_type,
        "exception_message": exc_msg,
        "traceback": tb_str,
        "environment": {
            "cwd": os.getcwd(),
            "pid": os.getpid(),
            "args": sys.argv[:5],
            "env_keys": sorted(k for k in os.environ if k.isupper() and len(k) > 3)[:50],
        },
    }
    crash_file = CRASHES_DIR / f"{safe_svc}_{ts}_{exc_type.replace('.','_')}.json"
    crash_file.parent.mkdir(parents=True, exist_ok=True)
    try:
        crash_file.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass


def _prune_old_crashes(days=7):
    """Remove crash reports older than `days` days."""
    if not CRASHES_DIR.exists():
        return
    cutoff = time.time() - days * 86400
    removed = 0
    for f in CRASHES_DIR.iterdir():
        try:
            if f.stat().st_mtime < cutoff:
                f.unlink()
                removed += 1
        except OSError:
            pass
    return removed


def get_errors(service=None, exc_type=None, since=None, limit=200, acknowledged_only=False):
    """Read and filter errors from the log file."""
    if not ERRORS_LOG.exists():
        return []
    entries = []
    with _lock:
        _load_ack()
    cutoff = since or 0
    with open(ERRORS_LOG, encoding="utf-8") as f:
        for line in f:
            try:
                e = json.loads(line.strip())
            except (json.JSONDecodeError, OSError):
                continue
            if e.get("ts", 0) < cutoff:
                continue
            if service and e.get("service") != service:
                continue
            if exc_type and e.get("exception_type") != exc_type:
                continue
            if acknowledged_only and not e.get("acknowledged", False):
                continue
            e["acknowledged"] = e["id"] in _acknowledged or e.get("acknowledged", False)
            entries.append(e)
    entries.sort(key=lambda x: x.get("ts", 0), reverse=True)
    return entries[:limit]


def acknowledge_error(err_id):
    """Mark an error as acknowledged."""
    with _lock:
        _load_ack()
        if err_id not in _acknowledged:
            _acknowledged.add(err_id)
            _save_ack()
            return True
    return False


def resolve_error(err_id):
    """Mark an error as resolved (acknowledged + flagged)."""
    with _lock:
        _load_ack()
        if err_id not in _acknowledged:
            _acknowledged.add(err_id)
            _save_ack()
            return True
    return False


def service_stats():
    """Return per-service error counts and badge data."""
    errors = get_errors(limit=10000)
    by_service = defaultdict(lambda: {"total": 0, "errors": 0, "crashes": 0, "unacked": 0})
    for e in errors:
        svc = e.get("service", "unknown")
        by_service[svc]["total"] += 1
        if e.get("kind") == "crash":
            by_service[svc]["crashes"] += 1
        elif e.get("exception_type") in CRITICAL_TYPES:
            by_service[svc]["errors"] += 1
        if not (e["id"] in _acknowledged or e.get("acknowledged", False)):
            by_service[svc]["unacked"] += 1
    return dict(by_service)


def export_errors(service=None, exc_type=None, since=None):
    """Return all matching errors as a JSON-serializable list."""
    return get_errors(service=service, exc_type=exc_type, since=since)


def catch_and_record(func):
    """Decorator to wrap a function and record any unhandled exception."""
    import functools

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            tb = traceback.format_exc()
            record(
                service=SERVICE_NAME,
                exc_type=type(exc).__name__,
                exc_msg=str(exc),
                traceback_str=tb,
                kind="error",
            )
            raise
    return wrapper


def install_unhandled_hook(service=None):
    """Install sys.excepthook to catch all unhandled exceptions."""
    global SERVICE_NAME
    if service:
        SERVICE_NAME = service

    def _hook(exc_type, exc_value, exc_tb):
        tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        record(
            service=SERVICE_NAME,
            exc_type=exc_type.__name__,
            exc_msg=str(exc_value),
            traceback_str=tb_str,
            kind="crash",
        )

    sys.excepthook = _hook


def install_flask_error_handler(app):
    """Register a Flask error handler that logs all unhandled exceptions."""
    from flask import request, jsonify

    @app.errorhandler(Exception)
    def _handle_exception(exc):
        tb = traceback.format_exc()
        record(
            service="dashboard",
            exc_type=type(exc).__name__,
            exc_msg=str(exc),
            traceback_str=tb,
            request_info={
                "path": request.url if hasattr(request, 'url') else "",
                "method": request.method if hasattr(request, 'method') else "",
            },
            kind="error",
        )
        return jsonify({"error": type(exc).__name__, "message": str(exc)}), 500

    @app.errorhandler(404)
    def _handle_404(exc):
        record(
            service="dashboard",
            exc_type="NotFound",
            exc_msg=str(exc),
            kind="error",
        )
        return jsonify({"error": "not_found", "message": str(exc)}), 404

    @app.errorhandler(500)
    def _handle_500(exc):
        tb = traceback.format_exc()
        record(
            service="dashboard",
            exc_type="InternalServerError",
            exc_msg=str(exc),
            traceback_str=tb,
            kind="crash",
        )
        return jsonify({"error": "internal_server_error", "message": str(exc)}), 500
