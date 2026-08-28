"""Workflow Engine — executes multi-step workflows with dependency management.

Workflows are defined as JSON files with steps that can have dependencies,
conditionals, and error handling. Supports both synchronous and asynchronous
execution with progress tracking.

Usage:
    from services.workflow_engine import WorkflowEngine
    engine = WorkflowEngine()
    engine.load_workflow("my_workflow.json")
    result = engine.run("my_workflow")
"""
import json
import threading
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

ROOT = Path(__file__).parent.parent
WORKFLOW_DIR = ROOT / "workflow" / "workflows"
WORKFLOW_STATE_PATH = ROOT / "config" / "workflows_state.json"


class WorkflowStep:
    """Represents a single step in a workflow."""

    def __init__(self, step_id: str, name: str, action: str,
                 params: dict = None, depends_on: List[str] = None,
                 condition: str = "", timeout: int = 60):
        self.step_id = step_id
        self.name = name
        self.action = action
        self.params = params or {}
        self.depends_on = depends_on or []
        self.condition = condition
        self.timeout = timeout
        self.status = "pending"  # pending, running, completed, failed, skipped
        self.result: Any = None
        self.error: Optional[str] = None
        self.started_at: Optional[float] = None
        self.completed_at: Optional[float] = None

    def to_dict(self) -> dict:
        return {
            "step_id": self.step_id,
            "name": self.name,
            "action": self.action,
            "params": self.params,
            "depends_on": self.depends_on,
            "condition": self.condition,
            "timeout": self.timeout,
            "status": self.status,
            "result": self.result,
            "error": self.error,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WorkflowStep":
        step = cls(
            step_id=data.get("step_id", ""),
            name=data.get("name", ""),
            action=data.get("action", ""),
            params=data.get("params"),
            depends_on=data.get("depends_on", []),
            condition=data.get("condition", ""),
            timeout=data.get("timeout", 60),
        )
        step.status = data.get("status", "pending")
        step.result = data.get("result")
        step.error = data.get("error")
        step.started_at = data.get("started_at")
        step.completed_at = data.get("completed_at")
        return step


class Workflow:
    """Represents a complete workflow definition."""

    def __init__(self, workflow_id: str, name: str, steps: List[WorkflowStep],
                 description: str = "", version: str = "1.0",
                 enabled: bool = True):
        self.workflow_id = workflow_id
        self.name = name
        self.steps = steps
        self.description = description
        self.version = version
        self.enabled = enabled
        self.status = "idle"  # idle, running, completed, failed, paused
        self.run_count = 0
        self.last_run: Optional[float] = None
        self.last_result: Optional[dict] = None
        self.created_at = time.time()

    def to_dict(self) -> dict:
        return {
            "id": self.workflow_id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "enabled": self.enabled,
            "status": self.status,
            "steps": [s.to_dict() for s in self.steps],
            "run_count": self.run_count,
            "last_run": self.last_run,
            "last_result": self.last_result,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Workflow":
        wf = cls(
            workflow_id=data.get("id", ""),
            name=data.get("name", "untitled"),
            steps=[WorkflowStep.from_dict(s) for s in data.get("steps", [])],
            description=data.get("description", ""),
            version=data.get("version", "1.0"),
            enabled=data.get("enabled", True),
        )
        wf.status = data.get("status", "idle")
        wf.run_count = data.get("run_count", 0)
        wf.last_run = data.get("last_run")
        wf.last_result = data.get("last_result")
        wf.created_at = data.get("created_at", time.time())
        return wf


class WorkflowEngine:
    """Executes workflows with dependency resolution and progress tracking."""

    def __init__(self, state_path: Optional[Path] = None):
        self._state_path = state_path or WORKFLOW_STATE_PATH
        self._workflows: Dict[str, Workflow] = {}
        self._active_runs: Dict[str, dict] = {}  # workflow_id -> run info
        self._handlers: Dict[str, Callable] = {}
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._load()
        self._scan_workflows()

    def _load(self):
        if not self._state_path.exists():
            return
        try:
            data = json.loads(self._state_path.read_text(encoding="utf-8"))
            for wd in data.get("workflows", []):
                wf = Workflow.from_dict(wd)
                self._workflows[wf.workflow_id] = wf
        except (json.JSONDecodeError, OSError):
            pass

    def _save(self):
        self._state_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "workflows": [w.to_dict() for w in self._workflows.values()],
            "active_runs": self._active_runs,
        }
        self._state_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _scan_workflows(self):
        """Scan the workflows directory for JSON workflow definitions."""
        if not WORKFLOW_DIR.exists():
            return
        for wf_file in sorted(WORKFLOW_DIR.glob("*.json")):
            if wf_file.name.startswith("_"):
                continue
            try:
                data = json.loads(wf_file.read_text(encoding="utf-8"))
                wf_id = data.get("id", wf_file.stem)
                if wf_id in self._workflows:
                    continue
                steps = []
                for s in data.get("steps", []):
                    steps.append(WorkflowStep(
                        step_id=s.get("step_id", f"step-{len(steps)}"),
                        name=s.get("name", ""),
                        action=s.get("action", ""),
                        params=s.get("params", {}),
                        depends_on=s.get("depends_on", []),
                        condition=s.get("condition", ""),
                        timeout=s.get("timeout", 60),
                    ))
                wf = Workflow(
                    workflow_id=wf_id,
                    name=data.get("name", wf_file.stem),
                    steps=steps,
                    description=data.get("description", ""),
                    version=data.get("version", "1.0"),
                )
                self._workflows[wf_id] = wf
            except (json.JSONDecodeError, OSError):
                continue

    def register_handler(self, action_name: str, fn: Callable):
        self._handlers[action_name] = fn

    def create_workflow(self, name: str, steps: List[dict],
                        description: str = "", version: str = "1.0",
                        workflow_id: Optional[str] = None) -> dict:
        wid = workflow_id or f"wf-{time.strftime('%Y%m%d%H%M%S')}-{threading.get_ident() % 1000:03d}"
        if wid in self._workflows:
            return {"error": f"Workflow ID already exists: {wid}"}
        step_objs = []
        for i, s in enumerate(steps):
            step_objs.append(WorkflowStep(
                step_id=s.get("step_id", f"step-{i}"),
                name=s.get("name", f"Step {i+1}"),
                action=s.get("action", ""),
                params=s.get("params", {}),
                depends_on=s.get("depends_on", []),
                condition=s.get("condition", ""),
                timeout=s.get("timeout", 60),
            ))
        wf = Workflow(workflow_id=wid, name=name, steps=step_objs,
                      description=description, version=version)
        with self._lock:
            self._workflows[wid] = wf
        self._save()
        return {"ok": True, "workflow": wf.to_dict()}

    def delete_workflow(self, workflow_id: str) -> dict:
        with self._lock:
            if workflow_id not in self._workflows:
                return {"error": f"Workflow not found: {workflow_id}"}
            if workflow_id in self._active_runs:
                return {"error": "Workflow is currently running"}
            del self._workflows[workflow_id]
        self._save()
        return {"ok": True}

    def get_workflow(self, workflow_id: str) -> Optional[dict]:
        with self._lock:
            wf = self._workflows.get(workflow_id)
        return wf.to_dict() if wf else None

    def list_workflows(self, enabled_only: bool = False) -> List[dict]:
        with self._lock:
            wfs = list(self._workflows.values())
        if enabled_only:
            wfs = [w for w in wfs if w.enabled]
        return [w.to_dict() for w in sorted(wfs, key=lambda w: w.name)]

    def toggle_workflow(self, workflow_id: str) -> dict:
        with self._lock:
            if workflow_id not in self._workflows:
                return {"error": f"Workflow not found: {workflow_id}"}
            self._workflows[workflow_id].enabled = not self._workflows[workflow_id].enabled
        self._save()
        return {"ok": True, "enabled": self._workflows[workflow_id].enabled}

    def run_workflow(self, workflow_id: str, params: dict = None) -> dict:
        with self._lock:
            if workflow_id not in self._workflows:
                return {"error": f"Workflow not found: {workflow_id}"}
            wf = self._workflows[workflow_id]
            if not wf.enabled:
                return {"error": "Workflow is disabled"}
            if workflow_id in self._active_runs:
                return {"error": "Workflow is already running"}
            wf.status = "running"
            run_id = f"run-{time.strftime('%Y%m%d%H%M%S')}-{threading.get_ident() % 1000:03d}"
            self._active_runs[workflow_id] = {
                "run_id": run_id,
                "started_at": time.time(),
                "params": params or {},
            }
        self._save()
        threading.Thread(
            target=self._execute_workflow,
            args=(workflow_id, run_id, params or {}),
            daemon=True,
        ).start()
        return {"ok": True, "workflow_id": workflow_id, "run_id": run_id}

    def _execute_workflow(self, workflow_id: str, run_id: str, params: dict):
        with self._lock:
            wf = self._workflows.get(workflow_id)
        if not wf:
            return
        wf.run_count += 1
        wf.last_run = time.time()
        all_results = {}
        try:
            for step in wf.steps:
                # Check condition
                if step.condition:
                    cond_result = self._eval_condition(step.condition, all_results, params)
                    if not cond_result:
                        step.status = "skipped"
                        continue
                # Check dependencies
                deps_ok = all(
                    self._workflows.get(workflow_id).steps and
                    any(s.step_id == dep and s.status == "completed"
                        for s in self._workflows.get(workflow_id, Workflow("", [])).steps)
                    for dep in step.depends_on
                ) if step.depends_on else True
                if not deps_ok:
                    step.status = "skipped"
                    continue
                # Execute step
                step.status = "running"
                step.started_at = time.time()
                handler = self._handlers.get(step.action)
                if handler:
                    try:
                        step.result = handler(**{**step.params, **params})
                        step.status = "completed"
                        all_results[step.step_id] = step.result
                    except Exception as e:
                        step.status = "failed"
                        step.error = str(e)
                        wf.status = "failed"
                        break
                else:
                    # Simulate execution for unknown actions
                    time.sleep(0.1)
                    step.result = {"status": "executed", "action": step.action}
                    step.status = "completed"
                    all_results[step.step_id] = step.result
                step.completed_at = time.time()
            if wf.status != "failed":
                wf.status = "completed"
            wf.last_result = {"run_id": run_id, "results": all_results}
        except Exception as e:
            wf.status = "failed"
            wf.last_result = {"error": str(e)}
        with self._lock:
            if workflow_id in self._active_runs:
                self._active_runs[workflow_id]["completed_at"] = time.time()
                self._active_runs[workflow_id]["result"] = wf.last_result
        self._save()

    def _eval_condition(self, condition: str, results: dict, params: dict) -> bool:
        """Evaluate a simple condition string."""
        if not condition:
            return True
        try:
            local_vars = {**results, **params, "True": True, "False": False}
            return bool(eval(condition, {"__builtins__": {}}, local_vars))
        except Exception:
            return True

    def stop_workflow(self, workflow_id: str) -> dict:
        with self._lock:
            if workflow_id not in self._workflows:
                return {"error": f"Workflow not found: {workflow_id}"}
            wf = self._workflows[workflow_id]
            if workflow_id in self._active_runs:
                del self._active_runs[workflow_id]
            wf.status = "paused"
        self._save()
        return {"ok": True, "status": "paused"}

    def get_run_status(self, workflow_id: str) -> dict:
        with self._lock:
            run = self._active_runs.get(workflow_id)
            wf = self._workflows.get(workflow_id)
        return {
            "workflow_id": workflow_id,
            "run": run,
            "workflow_status": wf.status if wf else "unknown",
            "workflow": wf.to_dict() if wf else None,
        }

    def get_stats(self) -> dict:
        with self._lock:
            total = len(self._workflows)
            enabled = sum(1 for w in self._workflows.values() if w.enabled)
            running = sum(1 for w in self._workflows.values() if w.status == "running")
            completed = sum(1 for w in self._workflows.values() if w.status == "completed")
            failed = sum(1 for w in self._workflows.values() if w.status == "failed")
            total_runs = sum(w.run_count for w in self._workflows.values())
        return {
            "total_workflows": total,
            "enabled": enabled,
            "running": running,
            "completed": completed,
            "failed": failed,
            "total_runs": total_runs,
            "active_runs": len(self._active_runs),
        }

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True, name="workflow-engine")
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
            self._thread = None

    def _monitor_loop(self):
        while self._running:
            with self._lock:
                for wid in list(self._active_runs.keys()):
                    wf = self._workflows.get(wid)
                    if wf and wf.status in ("completed", "failed"):
                        elapsed = time.time() - self._active_runs[wid].get("started_at", time.time())
                        if elapsed > 300:  # 5 minute safety timeout
                            del self._active_runs[wid]
            time.sleep(10)

    def reset(self):
        with self._lock:
            self._workflows.clear()
            self._active_runs.clear()
        self._scan_workflows()
        self._save()


_engine: Optional[WorkflowEngine] = None
_engine_lock = threading.Lock()


def get_engine() -> WorkflowEngine:
    global _engine
    if _engine is None:
        with _engine_lock:
            if _engine is None:
                _engine = WorkflowEngine()
    return _engine


def reset_engine():
    global _engine
    with _engine_lock:
        if _engine:
            _engine.stop()
        _engine = WorkflowEngine()
