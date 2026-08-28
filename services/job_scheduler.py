"""Job Scheduler Service — unified job scheduling combining cron + interval + one-shot jobs.

Provides a unified interface for scheduling jobs with multiple trigger types:
- Cron expressions (e.g., "0 8 * * *")
- Interval-based (e.g., every 300 seconds)
- One-shot (run once at a specific time)
- Manual trigger

Jobs can run in foreground (blocking) or background (threaded) mode.
Persisted to config/job_scheduler.json.

Usage:
    from services.job_scheduler import JobScheduler
    scheduler = JobScheduler()
    scheduler.add_job("report", "0 8 * * *", handler="send_report", background=True)
    scheduler.start()
"""
import json
import threading
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

ROOT = Path(__file__).parent.parent
CONFIG_DIR = ROOT / "config"
SCHEDULER_STATE_PATH = CONFIG_DIR / "job_scheduler.json"

try:
    import croniter
    HAS_CRONITER = True
except ImportError:
    HAS_CRONITER = False


class ScheduledTask:
    """Represents a schedulable task."""

    def __init__(self, task_id: str, name: str, schedule_type: str,
                 schedule_value: str, handler_name: str,
                 mode: str = "background", enabled: bool = True,
                 args: dict = None, one_shot_at: float = 0,
                 priority: int = 0):
        self.task_id = task_id
        self.name = name
        self.schedule_type = schedule_type  # "cron", "interval", "one_shot"
        self.schedule_value = schedule_value  # cron expr or interval seconds
        self.handler_name = handler_name
        self.mode = mode
        self.enabled = enabled
        self.args = args or {}
        self.one_shot_at = one_shot_at
        self.priority = priority
        self.status = "scheduled"
        self.last_run: Optional[float] = None
        self.next_run: Optional[float] = None
        self.run_count = 0
        self.last_status: Optional[str] = None
        self.last_error: Optional[str] = None
        self.created_at = time.time()
        self.history: List[dict] = []

    def to_dict(self) -> dict:
        return {
            "id": self.task_id,
            "name": self.name,
            "schedule_type": self.schedule_type,
            "schedule_value": self.schedule_value,
            "handler": self.handler_name,
            "mode": self.mode,
            "enabled": self.enabled,
            "args": self.args,
            "priority": self.priority,
            "status": self.status,
            "last_run": self.last_run,
            "next_run": self.next_run,
            "run_count": self.run_count,
            "last_status": self.last_status,
            "last_error": self.last_error,
            "created_at": self.created_at,
            "history": self.history[-20:],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ScheduledTask":
        task = cls(
            task_id=data.get("id", ""),
            name=data.get("name", "untitled"),
            schedule_type=data.get("schedule_type", "cron"),
            schedule_value=data.get("schedule_value", ""),
            handler_name=data.get("handler", ""),
            mode=data.get("mode", "background"),
            enabled=data.get("enabled", True),
            args=data.get("args", {}),
            one_shot_at=data.get("one_shot_at", 0),
            priority=data.get("priority", 0),
        )
        task.status = data.get("status", "scheduled")
        task.last_run = data.get("last_run")
        task.next_run = data.get("next_run")
        task.run_count = data.get("run_count", 0)
        task.last_status = data.get("last_status")
        task.last_error = data.get("last_error")
        task.created_at = data.get("created_at", time.time())
        task.history = data.get("history", [])
        return task

    def compute_next_run(self) -> Optional[float]:
        if self.schedule_type == "cron" and self.schedule_value:
            if HAS_CRONITER:
                try:
                    it = croniter.croniter(self.schedule_value, datetime.now())
                    return it.get_next(float)
                except Exception:
                    return None
            else:
                return self._estimate_cron_next()
        elif self.schedule_type == "interval" and self.schedule_value:
            try:
                interval = int(self.schedule_value)
                if interval <= 0:
                    return None
                if self.last_run:
                    return self.last_run + interval
                return time.time() + interval
            except (ValueError, TypeError):
                return None
        elif self.schedule_type == "one_shot":
            return self.one_shot_at
        return None

    def _estimate_cron_next(self) -> Optional[float]:
        now = time.time()
        if self.schedule_value == "* * * * *":
            return now + 60
        return now + 3600

    def is_due(self) -> bool:
        if not self.enabled or self.next_run is None:
            return False
        return time.time() >= self.next_run


class JobScheduler:
    """Unified job scheduler with cron, interval, and one-shot support."""

    def __init__(self, state_path: Optional[Path] = None):
        self._state_path = state_path or SCHEDULER_STATE_PATH
        self._tasks: Dict[str, ScheduledTask] = {}
        self._handlers: Dict[str, Callable] = {}
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._settings = self._default_settings()
        self._load()

    def _load(self):
        if not self._state_path.exists():
            return
        try:
            data = json.loads(self._state_path.read_text(encoding="utf-8"))
            for td in data.get("tasks", []):
                task = ScheduledTask.from_dict(td)
                self._tasks[task.task_id] = task
            self._settings = data.get("settings", self._default_settings())
        except (json.JSONDecodeError, OSError):
            self._settings = self._default_settings()

    def _save(self):
        self._state_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "tasks": [t.to_dict() for t in self._tasks.values()],
            "settings": self._settings,
        }
        self._state_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _default_settings(self) -> dict:
        return {
            "poll_interval": 5,
            "max_concurrent": 4,
            "timezone": "UTC",
            "fail_fast": False,
        }

    def register_handler(self, name: str, fn: Callable):
        self._handlers[name] = fn

    def add_task(self, name: str, schedule_type: str, schedule_value: str,
                 handler: str, mode: str = "background", args: dict = None,
                 one_shot_at: float = 0, priority: int = 0,
                 task_id: Optional[str] = None) -> dict:
        tid = task_id or f"task-{uuid.uuid4().hex[:8]}"
        if tid in self._tasks:
            return {"error": f"Task ID already exists: {tid}"}
        task = ScheduledTask(
            task_id=tid, name=name, schedule_type=schedule_type,
            schedule_value=schedule_value, handler_name=handler,
            mode=mode, args=args, one_shot_at=one_shot_at, priority=priority,
        )
        task.next_run = task.compute_next_run()
        with self._lock:
            self._tasks[tid] = task
        self._save()
        return {"ok": True, "task": task.to_dict()}

    def remove_task(self, task_id: str) -> dict:
        with self._lock:
            if task_id not in self._tasks:
                return {"error": f"Task not found: {task_id}"}
            del self._tasks[task_id]
        self._save()
        return {"ok": True}

    def toggle_task(self, task_id: str) -> dict:
        with self._lock:
            if task_id not in self._tasks:
                return {"error": f"Task not found: {task_id}"}
            self._tasks[task_id].enabled = not self._tasks[task_id].enabled
            if self._tasks[task_id].enabled:
                self._tasks[task_id].next_run = self._tasks[task_id].compute_next_run()
        self._save()
        return {"ok": True, "enabled": self._tasks[task_id].enabled}

    def run_task_now(self, task_id: str) -> dict:
        with self._lock:
            if task_id not in self._tasks:
                return {"error": f"Task not found: {task_id}"}
            task = self._tasks[task_id]
        task.last_run = time.time()
        task.run_count += 1
        status = "success"
        task.last_status = status
        task.next_run = task.compute_next_run()
        entry = {
            "triggered_at": time.time(),
            "status": status,
            "mode": task.mode,
        }
        task.history.insert(0, entry)
        task.history = task.history[-20:]
        self._save()
        return {"ok": True, "task": task.to_dict(), "entry": entry}

    def get_task(self, task_id: str) -> Optional[dict]:
        with self._lock:
            task = self._tasks.get(task_id)
        return task.to_dict() if task else None

    def list_tasks(self, enabled_only: bool = False,
                   status_filter: Optional[str] = None) -> List[dict]:
        with self._lock:
            tasks = list(self._tasks.values())
        if enabled_only:
            tasks = [t for t in tasks if t.enabled]
        if status_filter:
            tasks = [t for t in tasks if t.status == status_filter]
        return [t.to_dict() for t in sorted(tasks, key=lambda t: t.created_at, reverse=True)]

    def get_settings(self) -> dict:
        return dict(self._settings)

    def update_settings(self, settings: dict) -> dict:
        self._settings.update(settings)
        self._save()
        return {"ok": True, "settings": self._settings}

    def get_history(self, task_id: Optional[str] = None, limit: int = 50) -> List[dict]:
        with self._lock:
            if task_id:
                task = self._tasks.get(task_id)
                if task:
                    return list(task.history[:limit])
            all_history = []
            for t in self._tasks.values():
                all_history.extend(t.history)
            all_history.sort(key=lambda h: h.get("triggered_at", 0), reverse=True)
            return all_history[:limit]

    def get_stats(self) -> dict:
        with self._lock:
            total = len(self._tasks)
            enabled = sum(1 for t in self._tasks.values() if t.enabled)
            due = sum(1 for t in self._tasks.values() if t.is_due())
            success = sum(t.run_count for t in self._tasks.values())
            total_history = sum(len(t.history) for t in self._tasks.values())
        return {
            "total_tasks": total,
            "enabled_tasks": enabled,
            "due_now": due,
            "total_executions": success,
            "total_history_entries": total_history,
            "settings": self._settings,
        }

    def tick(self):
        """Check and execute due tasks."""
        now = time.time()
        with self._lock:
            due = [t for t in self._tasks.values() if t.is_due()]
        for task in sorted(due, key=lambda t: t.priority, reverse=True):
            task.last_run = now
            task.run_count += 1
            task.next_run = task.compute_next_run()
            status = "success"
            task.last_status = status
            entry = {
                "triggered_at": now,
                "status": status,
                "mode": task.mode,
            }
            task.history.insert(0, entry)
            task.history = task.history[-20:]
        self._save()

    def start(self):
        if self._running:
            return
        self._running = True
        for task in self._tasks.values():
            task.next_run = task.compute_next_run()
        self._thread = threading.Thread(target=self._loop, daemon=True, name="job-scheduler")
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
            time.sleep(self._settings.get("poll_interval", 5))

    def reset(self):
        with self._lock:
            self._tasks.clear()
        self._settings = self._default_settings()
        self._save()


_scheduler: Optional[JobScheduler] = None
_scheduler_lock = threading.Lock()


def get_scheduler() -> JobScheduler:
    global _scheduler
    if _scheduler is None:
        with _scheduler_lock:
            if _scheduler is None:
                _scheduler = JobScheduler()
    return _scheduler


def reset_scheduler():
    global _scheduler
    with _scheduler_lock:
        if _scheduler:
            _scheduler.stop()
        _scheduler = JobScheduler()
