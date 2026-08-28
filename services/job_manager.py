"""Job Manager — manages foreground/background job execution with dashboard state.

Provides job lifecycle management (create, run, pause, resume, cancel)
with support for both foreground (blocking) and background (threaded)
execution modes. Integrates with the cron scheduler for scheduled jobs.

Usage:
    from services.job_manager import JobManager
    mgr = JobManager()
    mgr.create_job("scan", "network_scan", args={"target": "192.168.1.1"}, background=True)
    mgr.start()
"""
import json
import threading
import time
import uuid
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

CONFIG_DIR = Path(__file__).parent.parent / "config"
JOBS_STATE_PATH = CONFIG_DIR / "job_manager.json"


class ManagedJob:
    """Represents a single managed job."""

    def __init__(self, job_id: str, name: str, handler_name: str,
                 args: dict, mode: str = "background", enabled: bool = True,
                 priority: int = 0):
        self.job_id = job_id
        self.name = name
        self.handler_name = handler_name
        self.args = args
        self.mode = mode  # "foreground" or "background"
        self.enabled = enabled
        self.priority = priority
        self.status = "queued"  # queued, running, paused, completed, failed, cancelled
        self.result: Any = None
        self.error: Optional[str] = None
        self.created_at = time.time()
        self.started_at: Optional[float] = None
        self.completed_at: Optional[float] = None
        self.run_count = 0
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    def to_dict(self) -> dict:
        return {
            "id": self.job_id,
            "name": self.name,
            "handler": self.handler_name,
            "args": self.args,
            "mode": self.mode,
            "enabled": self.enabled,
            "priority": self.priority,
            "status": self.status,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "run_count": self.run_count,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ManagedJob":
        job = cls(
            job_id=data.get("id", ""),
            name=data.get("name", "untitled"),
            handler_name=data.get("handler", ""),
            args=data.get("args", {}),
            mode=data.get("mode", "background"),
            enabled=data.get("enabled", True),
            priority=data.get("priority", 0),
        )
        job.status = data.get("status", "queued")
        job.result = data.get("result")
        job.error = data.get("error")
        job.created_at = data.get("created_at", time.time())
        job.started_at = data.get("started_at")
        job.completed_at = data.get("completed_at")
        job.run_count = data.get("run_count", 0)
        return job


class JobManager:
    """Manages job lifecycle with foreground/background execution support."""

    def __init__(self, config_path: Optional[Path] = None):
        self._config_path = config_path or JOBS_STATE_PATH
        self._jobs: Dict[str, ManagedJob] = {}
        self._handlers: Dict[str, Callable] = {}
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._load()

    def _load(self):
        if not self._config_path.exists():
            return
        try:
            data = json.loads(self._config_path.read_text(encoding="utf-8"))
            for jd in data.get("jobs", []):
                job = ManagedJob.from_dict(jd)
                self._jobs[job.job_id] = job
        except (json.JSONDecodeError, OSError):
            pass

    def _save(self):
        self._config_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "jobs": [j.to_dict() for j in self._jobs.values()],
            "settings": self._get_settings(),
        }
        self._config_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _get_settings(self) -> dict:
        return {
            "max_concurrent": 4,
            "default_mode": "background",
            "timeout_seconds": 300,
            "auto_retry": True,
            "max_retries": 3,
        }

    def register_handler(self, name: str, fn: Callable):
        self._handlers[name] = fn

    def create_job(self, name: str, handler: str, args: Optional[dict] = None,
                   mode: str = "background", priority: int = 0,
                   job_id: Optional[str] = None) -> dict:
        jid = job_id or f"job-{uuid.uuid4().hex[:8]}"
        if jid in self._jobs:
            return {"error": f"Job ID already exists: {jid}"}
        job = ManagedJob(
            job_id=jid, name=name, handler_name=handler,
            args=args or {}, mode=mode, priority=priority,
        )
        with self._lock:
            self._jobs[jid] = job
        self._save()
        return {"ok": True, "job": job.to_dict()}

    def list_jobs(self, status_filter: Optional[str] = None) -> List[dict]:
        with self._lock:
            jobs = list(self._jobs.values())
        if status_filter:
            jobs = [j for j in jobs if j.status == status_filter]
        return [j.to_dict() for j in sorted(jobs, key=lambda j: j.created_at, reverse=True)]

    def get_job(self, job_id: str) -> Optional[dict]:
        with self._lock:
            job = self._jobs.get(job_id)
        return job.to_dict() if job else None

    def start_job(self, job_id: str) -> dict:
        with self._lock:
            if job_id not in self._jobs:
                return {"error": f"Job not found: {job_id}"}
            job = self._jobs[job_id]
            if job.status == "running":
                return {"error": "Job is already running"}
            job.status = "running"
            job.started_at = time.time()
            job.run_count += 1
        self._save()
        if job.mode == "foreground":
            return self._run_foreground(job)
        else:
            return self._run_background(job)

    def _run_foreground(self, job: ManagedJob) -> dict:
        handler = self._handlers.get(job.handler_name)
        if not handler:
            with self._lock:
                job.status = "failed"
                job.error = f"Handler not found: {job.handler_name}"
                job.completed_at = time.time()
            self._save()
            return {"error": f"Handler not found: {job.handler_name}"}
        try:
            result = handler(**job.args)
            with self._lock:
                job.status = "completed"
                job.result = result
                job.completed_at = time.time()
            self._save()
            return {"ok": True, "job": job.to_dict(), "result": result}
        except Exception as e:
            with self._lock:
                job.status = "failed"
                job.error = str(e)
                job.completed_at = time.time()
            self._save()
            return {"error": str(e)}

    def _run_background(self, job: ManagedJob) -> dict:
        handler = self._handlers.get(job.handler_name)
        if not handler:
            with self._lock:
                job.status = "failed"
                job.error = f"Handler not found: {job.handler_name}"
                job.completed_at = time.time()
            self._save()
            return {"error": f"Handler not found: {job.handler_name}"}
        job._stop_event.clear()
        t = threading.Thread(
            target=self._bg_run, args=(job, handler),
            daemon=True, name=f"job-{job.job_id}",
        )
        job._thread = t
        t.start()
        return {"ok": True, "job": job.to_dict(), "thread_id": t.ident}

    def _bg_run(self, job: ManagedJob, handler: Callable):
        try:
            result = handler(**job.args)
            with self._lock:
                if job._stop_event.is_set():
                    job.status = "cancelled"
                else:
                    job.status = "completed"
                    job.result = result
                job.completed_at = time.time()
        except Exception as e:
            with self._lock:
                job.status = "failed"
                job.error = str(e)
                job.completed_at = time.time()
        self._save()

    def pause_job(self, job_id: str) -> dict:
        with self._lock:
            if job_id not in self._jobs:
                return {"error": f"Job not found: {job_id}"}
            job = self._jobs[job_id]
            if job.status == "running":
                job._stop_event.set()
            job.status = "paused"
        self._save()
        return {"ok": True, "status": "paused"}

    def resume_job(self, job_id: str) -> dict:
        with self._lock:
            if job_id not in self._jobs:
                return {"error": f"Job not found: {job_id}"}
            job = self._jobs[job_id]
            job._stop_event.clear()
            job.status = "queued"
        self._save()
        return self.start_job(job_id)

    def cancel_job(self, job_id: str) -> dict:
        with self._lock:
            if job_id not in self._jobs:
                return {"error": f"Job not found: {job_id}"}
            job = self._jobs[job_id]
            job._stop_event.set()
            job.status = "cancelled"
            job.completed_at = time.time()
        self._save()
        return {"ok": True, "status": "cancelled"}

    def delete_job(self, job_id: str) -> dict:
        with self._lock:
            if job_id not in self._jobs:
                return {"error": f"Job not found: {job_id}"}
            job = self._jobs.pop(job_id)
            job._stop_event.set()
        self._save()
        return {"ok": True}

    def get_settings(self) -> dict:
        return self._get_settings()

    def update_settings(self, settings: dict) -> dict:
        current = self._get_settings()
        current.update(settings)
        self._save()
        return {"ok": True, "settings": current}

    def get_stats(self) -> dict:
        with self._lock:
            total = len(self._jobs)
            by_status = {}
            for j in self._jobs.values():
                by_status[j.status] = by_status.get(j.status, 0) + 1
        return {
            "total_jobs": total,
            "by_status": by_status,
            "handlers_registered": len(self._handlers),
            "settings": self._get_settings(),
        }

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._poll_loop, daemon=True, name="job-manager")
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
            self._thread = None

    def _poll_loop(self):
        while self._running:
            with self._lock:
                queued = [j for j in self._jobs.values()
                          if j.status == "queued" and j.enabled]
            for job in sorted(queued, key=lambda j: j.priority, reverse=True):
                if not self._running:
                    break
                self.start_job(job.job_id)
            time.sleep(2)

    def reset(self):
        with self._lock:
            self._jobs.clear()
        self._save()


_manager: Optional[JobManager] = None
_manager_lock = threading.Lock()


def get_job_manager() -> JobManager:
    global _manager
    if _manager is None:
        with _manager_lock:
            if _manager is None:
                _manager = JobManager()
    return _manager


def reset_job_manager():
    global _manager
    with _manager_lock:
        if _manager:
            _manager.stop()
        _manager = JobManager()
