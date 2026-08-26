"""Versioning, scheduling, pause/resume (ROADMAP 4)."""
import json, pathlib, time, threading

REGISTRY = pathlib.Path(__file__).parent / "registry.json"
VERSIONS = pathlib.Path(__file__).parent / "versions"

def save_version(name, definition):
    VERSIONS.mkdir(exist_ok=True)
    ts = int(time.time())
    path = VERSIONS / f"{name}@{ts}.json"
    path.write_text(json.dumps(definition, indent=2), encoding="utf-8")
    return str(path)

def list_versions(name):
    if not VERSIONS.exists(): return []
    return sorted([p.name for p in VERSIONS.glob(f"{name}@*.json")])

# Scheduling: simple threading.Timer-based (K8s CronJob for prod)
_jobs = {}
def schedule_workflow(name, cron_or_delay_s, payload=None):
    """For MVP, cron_or_delay_s is seconds (int). Use K8s CronJob for real cron."""
    delay = int(cron_or_delay_s) if str(cron_or_delay_s).isdigit() else 60
    def _fire():
        from workflow.engine import run_workflow
        run_workflow(name, payload or {})
    t = threading.Timer(delay, _fire)
    t.daemon = True
    t.start()
    _jobs[name] = t
    return {"scheduled": name, "delay_s": delay}

def pause_workflow(name): 
    t=_jobs.get(name)
    if t: t.cancel()
    return {"paused": name}
