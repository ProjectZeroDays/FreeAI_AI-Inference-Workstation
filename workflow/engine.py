#!/usr/bin/env python3
"""FreeAI Workflow Engine — chaining, retries, parallelism, validation,
audit logging, inline (imported) workflow execution, scheduling, and
pause/resume."""
import concurrent.futures
import json
import os
import threading
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

import requests
try:
    from croniter import croniter
except ImportError:
    croniter = None

try:
    from settings import load_config
    _CFG = load_config().get("workflow", {})
except ImportError:
    _CFG = {}

AGENT_API = _CFG.get("agent_api",
                      os.environ.get("AGENT_API", "http://localhost:8120"))
STEP_RETRIES = int(_CFG.get("step_retries", 3))
RETRY_DELAY_S = float(_CFG.get("retry_delay_s", 2))
_VERSIONING_ENABLED = bool(_CFG.get("versioning", {}).get("enabled", True))
_SCHEDULE_ENABLED = bool(_CFG.get("schedule", {}).get("enabled", False))


try:
    from workflow.audit import log_execution as _log_execution
    from workflow.validator import validate_workflow
except ImportError:
    from audit import log_execution as _log_execution
    from validator import validate_workflow


KNOWN_KEYS = {"workflow", "workflow_id", "status", "steps", "error"}

# ---------------------------
# Pause / Resume state
# ---------------------------
_PAUSED: set = set()
_PAUSED_LOCK = threading.Lock()


def pause_workflow(name: str) -> bool:
    with _PAUSED_LOCK:
        _PAUSED.add(name)
    return True


def resume_workflow(name: str) -> bool:
    with _PAUSED_LOCK:
        _PAUSED.discard(name)
    return True


def is_paused(name: str) -> bool:
    with _PAUSED_LOCK:
        return name in _PAUSED


def get_pause_status(name: str) -> Dict[str, Any]:
    with _PAUSED_LOCK:
        return {"name": name, "paused": name in _PAUSED}


# ---------------------------
# Version cache (in-memory)
# ---------------------------
_VERSIONS: Dict[str, List[Dict[str, Any]]] = {}
_VERSIONS_LOCK = threading.Lock()


def version_workflow(name: str, definition: Dict[str, Any]) -> Dict[str, Any]:
    """Create an in-memory version snapshot and persist via versioning module."""
    try:
        from workflow.versioning import create_version as _cv
    except ImportError:
        from versioning import create_version as _cv
    result = _cv(name, definition)
    ver = result.get("version")
    if ver:
        with _VERSIONS_LOCK:
            _VERSIONS.setdefault(name, []).append({
                "version": ver,
                "timestamp": time.time(),
                "definition": definition,
            })
    return result


def get_versions(name: str) -> List[Dict[str, Any]]:
    """Return in-memory version list for a workflow."""
    with _VERSIONS_LOCK:
        return list(_VERSIONS.get(name, []))


def clear_versions(name: str) -> None:
    with _VERSIONS_LOCK:
        _VERSIONS.pop(name, None)


# ---------------------------
# Scheduler state
# ---------------------------
_scheduled_workflows: Dict[str, Dict[str, Any]] = {}
_scheduler_lock = threading.Lock()
_scheduler_running = 0
_scheduler_thread: Optional[threading.Thread] = None


def set_schedule(name: str, cron_expr: str) -> None:
    with _scheduler_lock:
        _scheduled_workflows[name] = {"cron": cron_expr}


def clear_schedule(name: str) -> None:
    with _scheduler_lock:
        _scheduled_workflows.pop(name, None)


def get_schedule(name: str) -> Optional[Dict[str, str]]:
    with _scheduler_lock:
        entry = _scheduled_workflows.get(name)
        return dict(entry) if entry else None


def running_count() -> int:
    return _scheduler_running


def start_scheduler_thread() -> None:
    global _scheduler_thread
    if _scheduler_thread and _scheduler_thread.is_alive():
        return
    _scheduler_thread = threading.Thread(
        target=_scheduler_loop, daemon=True, name="workflow-scheduler"
    )
    _scheduler_thread.start()


def _scheduler_loop() -> None:
    global _scheduler_running
    while True:
        time.sleep(30)
        if not _SCHEDULE_ENABLED:
            continue
        now = time.time()
        with _scheduler_lock:
            to_run = []
            for name, entry in list(_scheduled_workflows.items()):
                cron_expr = entry.get("cron", "")
                if not cron_expr or not croniter:
                    continue
                try:
                    ci = croniter(cron_expr, datetime.now())
                    next_run = ci.get_next(float)
                    if next_run <= now + 60:
                        to_run.append(name)
                except Exception:
                    pass
        for name in to_run:
            _scheduler_running += 1
            t = threading.Thread(
                target=_run_scheduled, args=(name,), daemon=True
            )
            t.start()


def _run_scheduled(name: str) -> None:
    global _scheduler_running
    try:
        wf = get_workflow(name)
        if wf:
            wf.execute({})
    finally:
        with _scheduler_lock:
            _scheduler_running -= 1


def _audit(event: dict):
    """Backward-compatible wrapper: accepts either a flat dict (old style)
    or keyword args (new structured style via log_execution)."""
    known = KNOWN_KEYS & set(event)
    extra = {k: v for k, v in event.items() if k not in KNOWN_KEYS}
    return _log_execution(
        workflow=event.get("workflow"),
        workflow_id=event.get("workflow_id"),
        status=event.get("status"),
        steps=event.get("steps"),
        error=event.get("error"),
        extra=extra if extra else None,
    )


def _extract_text(result: Dict[str, Any]) -> str:
    """Pull generated text out of a router/agent response."""
    if not isinstance(result, dict):
        return ""
    response = result.get("response", result)
    choices = (response or {}).get("choices")
    if choices:
        choice = choices[0] or {}
        message = choice.get("message") or {}
        text = message.get("content") or choice.get("text")
        if text:
            return text
    content = (response or {}).get("content")
    if content:
        return content
    return ""


class Step:
    def __init__(
        self,
        name: str,
        agent: str,
        prompt_builder: Callable[[Dict[str, Any]], Dict[str, Any]],
        consumes: List[str] = None,
        produces: List[str] = None,
    ):
        self.name = name
        self.agent = agent
        self.prompt_builder = prompt_builder
        self.consumes = consumes or []
        self.produces = produces or []

    def run(self, context: Dict[str, Any], workflow_id: str = "-"):
        payload = self.prompt_builder(context)
        url = f"{AGENT_API}/agent/{self.agent}"

        for attempt in range(1, STEP_RETRIES + 1):
            try:
                r = requests.post(url, json=payload, timeout=660)
                r.raise_for_status()
                result = r.json()
                _audit({"workflow_id": workflow_id, "step": self.name,
                        "agent": self.agent, "status": "ok",
                        "attempt": attempt})
                return {self.name: result}
            except Exception as exc:
                _audit({"workflow_id": workflow_id, "step": self.name,
                        "agent": self.agent,
                        "status": "retry" if attempt < STEP_RETRIES
                        else "failed",
                        "attempt": attempt, "error": str(exc)})
                if attempt == STEP_RETRIES:
                    raise
                time.sleep(RETRY_DELAY_S)


class InlineStep(Step):
    """Step whose payload is supplied verbatim (JSON import / designer)."""

    def __init__(self, name: str, agent: str,
                 payload: Dict[str, Any], consumes: List[str] = None):
        super().__init__(name, agent, lambda ctx: dict(payload), consumes)


def run_parallel(steps, context):
    results = {}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_map = {
            executor.submit(step.run, context): step.name
            for step in steps
        }
        for future in concurrent.futures.as_completed(future_map):
            name = future_map[future]
            results[name] = future.result()[name]
    return results


def validate_workflow(steps: List[Step],
                      initial_keys: List[str] = None) -> List[str]:
    """Return warnings for steps consuming outputs that no earlier step
    produces and that are absent from the initial context."""
    warnings = []
    available = set(initial_keys or [])
    for step in steps:
        for dep in step.consumes:
            if dep not in available:
                warnings.append(
                    f"step '{step.name}' consumes '{dep}' "
                    f"but nothing provides it before it")
        available.add(step.name)
        available.update(step.produces)
    return warnings


class Workflow:
    def __init__(self, name: str, steps: List[Step], schedule: str = None):
        self.name = name
        self.steps = steps
        self.schedule = schedule

    def execute(self, initial_context: Dict[str, Any],
                strict_validation: bool = False) -> Dict[str, Any]:
        if is_paused(self.name):
            raise RuntimeError(f"workflow '{self.name}' is paused")
        context = dict(initial_context)
        context["_workflow_id"] = str(uuid.uuid4())
        context["_started_at"] = time.time()

        warnings = validate_workflow(
            self.steps, [k for k in initial_context
                          if not k.startswith("_")])
        if strict_validation and warnings:
            raise ValueError("validation failed: " + "; ".join(warnings))

        print(f"[workflow] Starting: {self.name} "
              f"({context['_workflow_id']})")
        _audit({"workflow": self.name, "workflow_id":
                context["_workflow_id"], "status": "started"})

        outputs: Dict[str, Any] = {}
        for step in self.steps:
            print(f"[workflow] Step: {step.name}")
            result = step.run(context, context["_workflow_id"])
            print(f"[workflow] Step complete: {step.name}")
            outputs.update(result)
            context[step.name] = result[step.name]

        context["_finished_at"] = time.time()
        _audit({"workflow": self.name, "workflow_id":
                context["_workflow_id"], "status": "finished"})
        return {
            "workflow": self.name,
            "workflow_id": context["_workflow_id"],
            "started_at": context["_started_at"],
            "finished_at": context["_finished_at"],
            "steps": [s.name for s in self.steps],
            "warnings": warnings,
            "outputs": outputs,
        }

    def version_workflow(self, definition: Dict[str, Any]) -> Dict[str, Any]:
        return version_workflow(self.name, definition)

    def pause_workflow(self) -> bool:
        return pause_workflow(self.name)

    def resume_workflow(self) -> bool:
        return resume_workflow(self.name)

    def get_versions(self) -> List[Dict[str, Any]]:
        return get_versions(self.name)

    def get_pause_status(self) -> Dict[str, Any]:
        return get_pause_status(self.name)


def to_definition(workflow: Workflow) -> Dict[str, Any]:
    """Serialize a Workflow to an importable JSON definition."""
    defn: Dict[str, Any] = {
        "name": workflow.name,
        "steps": [
            {"name": s.name, "agent": s.agent, "consumes": s.consumes,
             "produces": s.produces}
            for s in workflow.steps
        ],
    }
    if workflow.schedule:
        defn["schedule"] = workflow.schedule
    return defn


def from_definition(defn: Dict[str, Any]) -> Workflow:
    """Build a runnable Workflow from a designer-exported definition.
    Each step must carry an explicit `payload` object; otherwise a generic
    orchestrate prompt is built from the spec/context."""
    steps = []
    for s in defn.get("steps", []):
        payload = s.get("payload")
        if payload is not None:
            steps.append(InlineStep(s["name"], s["agent"], payload,
                                    s.get("consumes")))
        else:
            def builder(ctx, _s=s):
                return {
                    "prompt": ctx.get("spec", ctx.get("prompt", "")),
                    "max_tokens": 2048,
                }
            steps.append(Step(s["name"], s["agent"], builder,
                              s.get("consumes")))
    wf = Workflow(defn.get("name", "imported_workflow"), steps,
                  schedule=defn.get("schedule"))
    if wf.schedule and _SCHEDULE_ENABLED and croniter:
        set_schedule(wf.name, wf.schedule)
    return wf


# ---------------------------
# Prompt builders
# ---------------------------

def project_prompt_builder(ctx: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "spec": ctx["spec"],
        "max_tokens": 4096,
        "temperature": 0.2,
    }


def refactor_prompt_builder(ctx: Dict[str, Any]) -> Dict[str, Any]:
    code = _extract_text(ctx.get("project", {})) or ctx.get("code", "")
    return {
        "code": code,
        "language": ctx.get("language", "python"),
        "goals": "clean, idiomatic, production-ready",
        "max_tokens": 2048,
    }


def analysis_prompt_builder(ctx: Dict[str, Any]) -> Dict[str, Any]:
    arch = str(ctx.get("project", {}).get("response", ""))
    return {
        "context": arch,
        "question": "Identify risks, bottlenecks, and improvement "
                    "opportunities.",
        "max_tokens": 2048,
    }


# ---------------------------
# Example workflow: project pipeline
# ---------------------------

project_step = Step(
    name="project",
    agent="project",
    prompt_builder=project_prompt_builder,
)

refactor_step = Step(
    name="refactor",
    agent="refactor",
    prompt_builder=refactor_prompt_builder,
    consumes=["project"],
)

analysis_step = Step(
    name="analysis",
    agent="analyze",
    prompt_builder=analysis_prompt_builder,
    consumes=["project"],
)

PROJECT_WORKFLOW = Workflow(
    name="project_pipeline",
    steps=[project_step, refactor_step, analysis_step],
)


def run_project_workflow(spec: str, language: str = "python") -> Dict[str, Any]:
    ctx = {
        "spec": spec,
        "language": language,
    }
    return PROJECT_WORKFLOW.execute(ctx)


# ---------------------------
# Versioned save
# ---------------------------
def save_workflow_with_version(
    workflow_id: str,
    definition: Dict[str, Any],
) -> Dict[str, Any]:
    """Save a workflow definition and auto-create a version snapshot.
    Returns {'version': str, 'path': str} on success."""
    if not _VERSIONING_ENABLED:
        return {"version": None, "skipped": True}
    try:
        from workflow.versioning import create_version as _cv
    except ImportError:
        from versioning import create_version as _cv
    return _cv(workflow_id, definition)
