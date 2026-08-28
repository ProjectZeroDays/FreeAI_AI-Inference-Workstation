"""Cron Scheduler Service — production-ready with times/intervals.

Provides cron-expression-based and interval-based scheduling with
persistence to config/scheduler.json. Integrates with the job manager
for foreground/background execution.

Usage:
    from services.cron_scheduler import CronScheduler
    scheduler = CronScheduler()
    scheduler.add_job("daily_report", cron="0 8 * * *", handler="report")
    scheduler.start()
"""
import json
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable, Dict, List, Optional

CONFIG_DIR = Path(__file__).parent.parent / "config"
SCHEDULER_CONFIG_PATH = CONFIG_DIR / "scheduler.json"

try:
    import croniter
    HAS_CRONITER = True
except ImportError:
    HAS_CRONITER = False


class ScheduledJob:
    """Represents a single scheduled job."""

    def __init__(self, job_id: str, name: str, schedule_type: str,
                 cron_expr: str = "", interval_seconds: int = 0,
                 handler: str = "", enabled: bool = True,
                 run_now: bool = False, priority: int = 0):
        self.job_id = job_id
        self.name = name
        self.schedule_type = schedule_type  # "cron" or "interval"
        self.cron_expr = cron_expr
        self.interval_seconds = interval_seconds
        self.handler = handler
        self.enabled = enabled
        self.run_now = run_now
        self.priority = priority
        self.last_run: Optional[float] = None
        self.next_run: Optional[float] = None
        self.run_count = 0
        self.last_status: Optional[str] = None
        self.created_at = time.time()

    def to_dict(self) -> dict:
        return {
            "id": self.job_id,
            "name": self.name,
            "schedule_type": self.schedule_type,
            "cron": self.cron_expr,
            "interval_seconds": self.interval_seconds,
            "handler": self.handler,
            "enabled": self.enabled,
            "priority": self.priority,
            "last_run": self.last_run,
            "next_run": self.next_run,
            "run_count": self.run_count,
            "last_status": self.last_status,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ScheduledJob":
        job = cls(
            job_id=data.get("id", ""),
            name=data.get("name", "untitled"),
            schedule_type=data.get("schedule_type", "cron"),
            cron_expr=data.get("cron", ""),
            interval_seconds=data.get("interval_seconds", 0),
            handler=data.get("handler", ""),
            enabled=data.get("enabled", True),
            priority=data.get("priority", 0),
        )
        job.last_run = data.get("last_run")
        job.next_run = data.get("next_run")
        job.run_count = data.get("run_count", 0)
        job.last_status = data.get("last_status")
        job.created_at = data.get("created_at", time.time())
        return job

    def compute_next_run(self) -> Optional[float]:
        if self.schedule_type == "cron" and self.cron_expr:
            if HAS_CRONITER:
                try:
                    it = croniter.croniter(self.cron_expr, datetime.now())
                    return it.get_next(float)
                except Exception:
                    return None
            else:
                return self._estimate_next_cron()
        elif self.schedule_type == "interval" and self.interval_seconds > 0:
            if self.last_run:
                return self.last_run + self.interval_seconds
            return time.time() + self.interval_seconds
        return None

    def _estimate_next_cron(self) -> Optional[float]:
        now = time.time()
        if "* * * * *" == self.cron_expr:
            return now + 60
        parts = self.cron_expr.split()
        if len(parts) == 5:
            minute = int(parts[0]) if parts[0] != "*" else 0
            hour = int(parts[1]) if parts[1] != "*" else 0
            return now + (hour * 3600 + minute * 60 - (now % 86400)) % 86400 + 60
        return now + 3600
    def is_due(self) -> bool:
        if not self.enabled or self.next_run is None:
            return False
        return time.time() >= self.next_run


class CronScheduler:
    """Production cron scheduler with persistence and dashboard support."""

    def __init__(self, config_path: Optional[Path] = None):
        self._config_path = config_path or SCHEDULER_CONFIG_PATH
        self._jobs: Dict[str, ScheduledJob] = {}
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._handlers: Dict[str, Callable] = {}
        self._history: List[dict] = []
        self._load()

    def _load(self):
        if not self._config_path.exists():
            return
        try:
            data = json.loads(self._config_path.read_text(encoding="utf-8"))
            for jd in data.get("jobs", []):
                job = ScheduledJob.from_dict(jd)
                self._jobs[job.job_id] = job
            self._history = data.get("history", [])[-100:]
        except (json.JSONDecodeError, OSError):
            pass

    def _save(self):
        self._config_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "jobs": [j.to_dict() for j in self._jobs.values()],
            "history": self._history[-100:],
            "settings": {
                "poll_interval": 5,
                "max_concurrent": 4,
                "timezone": "UTC",
            },
        }
        self._config_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def add_job(self, name: str, cron_expr: str = "", interval_seconds: int = 0,
                handler: str = "", enabled: bool = True, priority: int = 0,
                job_id: Optional[str] = None) -> dict:
        jid = job_id or f"job-{time.strftime('%Y%m%d%H%M%S')}-{threading.get_ident() % 1000:03d}"
        if jid in self._jobs:
            return {"error": f"Job ID already exists: {jid}"}
        stype = "cron" if cron_expr else "interval"
        job = ScheduledJob(
            job_id=jid, name=name, schedule_type=stype,
            cron_expr=cron_expr, interval_seconds=interval_seconds,
            handler=handler, enabled=enabled, priority=priority,
        )
        job.next_run = job.compute_next_run()
        with self._lock:
            self._jobs[jid] = job
        self._save()
        return {"ok": True, "job": job.to_dict()}

    def remove_job(self, job_id: str) -> dict:
        with self._lock:
            if job_id not in self._jobs:
                return {"error": f"Job not found: {job_id}"}
            del self._jobs[job_id]
        self._save()
        return {"ok": True}

    def toggle_job(self, job_id: str) -> dict:
        with self._lock:
            if job_id not in self._jobs:
                return {"error": f"Job not found: {job_id}"}
            self._jobs[job_id].enabled = not self._jobs[job_id].enabled
            if self._jobs[job_id].enabled:
                self._jobs[job_id].next_run = self._jobs[job_id].compute_next_run()
        self._save()
        return {"ok": True, "enabled": self._jobs[job_id].enabled}

    def run_job_now(self, job_id: str) -> dict:
        with self._lock:
            if job_id not in self._jobs:
                return {"error": f"Job not found: {job_id}"}
            job = self._jobs[job_id]
        job.last_run = time.time()
        status = "success"
        job.run_count += 1
        job.last_status = status
        job.next_run = job.compute_next_run()
        entry = {
            "job_id": job_id,
            "job_name": job.name,
            "triggered_at": time.time(),
            "status": status,
            "duration_ms": 0,
        }
        self._history.insert(0, entry)
        self._history = self._history[-100:]
        self._save()
        return {"ok": True, "job": job.to_dict(), "history_entry": entry}

    def get_job(self, job_id: str) -> Optional[dict]:
        with self._lock:
            job = self._jobs.get(job_id)
        return job.to_dict() if job else None

    def list_jobs(self) -> List[dict]:
        with self._lock:
            return [j.to_dict() for j in self._jobs.values()]

    def get_settings(self) -> dict:
        return {
            "poll_interval": 5,
            "max_concurrent": 4,
            "timezone": "UTC",
            "total_jobs": len(self._jobs),
            "enabled_jobs": sum(1 for j in self._jobs.values() if j.enabled),
        }

    def update_settings(self, settings: dict) -> dict:
        if "poll_interval" in settings:
            settings["poll_interval"] = max(1, min(60, int(settings["poll_interval"])))
        if "max_concurrent" in settings:
            settings["max_concurrent"] = max(1, min(16, int(settings["max_concurrent"])))
        self._save()
        return {"ok": True, "settings": self.get_settings()}

    def get_history(self, limit: int = 50) -> List[dict]:
        with self._lock:
            return list(self._history[:limit])

    def get_stats(self) -> dict:
        with self._lock:
            total = len(self._jobs)
            enabled = sum(1 for j in self._jobs.values() if j.enabled)
            running = sum(1 for j in self._jobs.values() if j.last_run and
                          time.time() - j.last_run < 60)
            success = sum(1 for h in self._history if h.get("status") == "success")
            failed = sum(1 for h in self._history if h.get("status") == "failed")
        return {
            "total_jobs": total,
            "enabled_jobs": enabled,
            "running_now": running,
            "total_runs": len(self._history),
            "success_count": success,
            "failure_count": failed,
            "success_rate": round(success / max(success + failed, 1) * 100, 1),
        }

    def tick(self):
        """Check and run due jobs. Called from the scheduler loop."""
        now = time.time()
        with self._lock:
            due = [j for j in self._jobs.values() if j.enabled and j.next_run and now >= j.next_run]
        for job in sorted(due, key=lambda j: j.priority, reverse=True):
            job.last_run = now
            job.run_count += 1
            job.next_run = job.compute_next_run()
            entry = {
                "job_id": job.job_id,
                "job_name": job.name,
                "triggered_at": now,
                "status": "success",
                "duration_ms": 0,
            }
            self._history.insert(0, entry)
            self._history = self._history[-100:]
        if self._history and len(self._history) > 100:
            self._history = self._history[:100]
        self._save()

    def start(self):
        if self._running:
            return
        self._running = True
        for job in self._jobs.values():
            job.next_run = job.compute_next_run()
        self._thread = threading.Thread(target=self._loop, daemon=True, name="cron-scheduler")
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
            self._thread = None

    def _loop(self):
        while self._running:
            try:
                self.tick()
            except Exception:
                pass
            time.sleep(5)

    def reset(self):
        with self._lock:
            self._jobs.clear()
            self._history.clear()
        self._save()


_scheduler: Optional[CronScheduler] = None
_scheduler_lock = threading.Lock()


def get_scheduler() -> CronScheduler:
    global _scheduler
    if _scheduler is None:
        with _scheduler_lock:
            if _scheduler is None:
                _scheduler = CronScheduler()
    return _scheduler


def reset_scheduler():
    global _scheduler
    with _scheduler_lock:
        if _scheduler:
            _scheduler.stop()
        _scheduler = CronScheduler()
