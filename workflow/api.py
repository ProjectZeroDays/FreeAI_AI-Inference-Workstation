#!/usr/bin/env python3
import json
import logging
import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

try:
    from workflow.engine import (from_definition, to_definition,
                                  pause_workflow, resume_workflow,
                                  is_paused, get_schedule,
                                  set_schedule, clear_schedule,
                                  save_workflow_with_version,
                                  running_count, start_scheduler_thread,
                                  version_workflow, get_versions,
                                  get_pause_status, clear_versions)
    from workflow.registry import get_workflow, list_workflows
    from workflow.validator import validate_workflow
    from workflow.audit import read_audit
    from workflow.versioning import (list_versions, get_version,
                                       diff_versions, restore_version)
except ImportError:
    from engine import (from_definition, to_definition,
                        pause_workflow, resume_workflow,
                        is_paused, get_schedule,
                        set_schedule, clear_schedule,
                        save_workflow_with_version,
                        running_count, start_scheduler_thread,
                        version_workflow, get_versions,
                        get_pause_status, clear_versions)
    from registry import get_workflow, list_workflows
    from validator import validate_workflow
    from audit import read_audit
    from versioning import (list_versions, get_version,
                            diff_versions, restore_version)

app = FastAPI(title="FreeAI Workflow Engine", version="1.2")

TEMPLATES_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "config", "workflow-templates.json"
)


class WorkflowRequest(BaseModel):
    workflow: str
    context: dict = Field(default_factory=dict)
    strict_validation: bool = False


class InlineWorkflowRequest(BaseModel):
    definition: dict


class ValidateRequest(BaseModel):
    steps: list


class ValidateDefinitionRequest(BaseModel):
    definition: dict


class PauseResumeRequest(BaseModel):
    cron: str = ""


@app.get("/workflows")
def workflows():
    return {"workflows": list_workflows()}


@app.post("/workflow/run")
def run_workflow(req: WorkflowRequest):
    wf = get_workflow(req.workflow)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")

    try:
        result = wf.execute(req.context,
                            strict_validation=req.strict_validation)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Validation error")
    except Exception as e:
        logging.getLogger(__name__).exception("Workflow API error")
        raise HTTPException(status_code=500, detail="An internal error occurred")


@app.post("/workflow/run-inline")
def run_inline_workflow(req: InlineWorkflowRequest):
    """Execute an imported/designer-exported workflow definition."""
    try:
        wf = from_definition(req.definition)
        if not wf.steps:
            raise HTTPException(status_code=422,
                                detail="definition has no steps")
        return wf.execute({"spec": req.definition.get("context", {}).get(
            "spec", "")})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="An internal error occurred")


@app.get("/workflow/export/{name}")
def export_workflow(name: str):
    wf = get_workflow(name)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return to_definition(wf)


@app.post("/workflow/validate")
def validate(req: ValidateRequest):
    """Validate a list of step dicts (plain or Step-like)."""
    class _Shim:
        pass

    steps = []
    for s in req.steps:
        step = _Shim()
        step.name = s.get("name", "?")
        step.agent = s.get("agent", "orchestrate")
        step.consumes = s.get("consumes")
        step.produces = s.get("produces")
        steps.append(step)
    return {"warnings": validate_workflow(steps)}


@app.post("/workflow/validate-definition")
def validate_definition(req: ValidateDefinitionRequest):
    """Validate a full workflow definition dict (name, steps, triggers)."""
    definition = req.definition
    warnings = []

    if "name" not in definition:
        warnings.append("definition is missing 'name'")
    if "steps" not in definition:
        warnings.append("definition is missing 'steps'")
        definition["steps"] = []
    if "triggers" not in definition:
        warnings.append("definition is missing 'triggers'")

    class _Shim:
        pass

    steps = []
    for s in definition.get("steps", []):
        step = _Shim()
        step.name = s.get("name")
        step.agent = s.get("agent", "orchestrate")
        step.consumes = s.get("consumes")
        step.produces = s.get("produces")
        steps.append(step)

    warnings.extend(validate_workflow(steps))
    return {"warnings": warnings}


@app.get("/workflow/templates")
def get_templates():
    """Return pre-built workflow templates from config."""
    try:
        with open(TEMPLATES_PATH) as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        raise HTTPException(status_code=404,
                            detail="workflow-templates.json not found")
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500,
                            detail=f"invalid JSON: {exc}")


@app.get("/workflow/audit")
def get_audit(limit: int = 50):
    """Return the last *limit* audit-log entries."""
    return {"entries": read_audit(limit)}


# ── Pause / Resume ──────────────────────────────────────────────

@app.post("/workflow/{id}/pause")
def pause_workflow_endpoint(id: str):
    """Pause a workflow so future executions are rejected."""
    pause_workflow(id)
    return {"ok": True, "id": id, "status": "paused"}


@app.post("/workflow/{id}/resume")
def resume_workflow_endpoint(id: str):
    """Resume a previously paused workflow."""
    resume_workflow(id)
    return {"ok": True, "id": id, "status": "resumed"}


@app.get("/workflow/{id}/status")
def workflow_status_endpoint(id: str):
    """Return pause state and schedule info for a workflow."""
    paused = is_paused(id)
    schedule = get_schedule(id)
    wf = get_workflow(id)
    return {
        "id": id,
        "paused": paused,
        "schedule": schedule,
        "exists": wf is not None,
    }


# ── Versions ────────────────────────────────────────────────────

@app.get("/api/workflow/versions/{id}")
def list_workflow_versions(id: str):
    """List all saved versions for a workflow."""
    return {"versions": list_versions(id)}


@app.get("/api/workflow/versions/{id}/{ver}")
def get_workflow_version(id: str, ver: str):
    """Return a specific version's full metadata."""
    data = get_version(id, ver)
    if data is None:
        raise HTTPException(status_code=404,
                            detail=f"version {ver} not found")
    return data


@app.post("/api/workflow/versions/{id}/restore")
def restore_workflow_version(id: str, ver: str):
    """Restore a workflow definition from a saved version."""
    result = restore_version(id, ver)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


# ── Schedule ────────────────────────────────────────────────────

@app.post("/workflow/{id}/schedule")
def set_workflow_schedule(id: str, req: PauseResumeRequest):
    """Assign a cron schedule to a workflow."""
    if not req.cron:
        clear_schedule(id)
        return {"ok": True, "id": id, "schedule": None}
    set_schedule(id, req.cron)
    return {"ok": True, "id": id, "schedule": req.cron}


@app.get("/api/workflow/running")
def get_running_count():
    return {"running": running_count()}


@app.get("/health")
def health():
    return {"status": "ok"}


# ── New API Routes: /api/workflows/<id>/ ──────────────────────

@app.post("/api/workflows/{id}/version")
def create_workflow_version(id: str):
    """Create a version snapshot for a workflow."""
    result = version_workflow(id, {"workflow_id": id, "timestamp": time.time()})
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@app.post("/api/workflows/{id}/pause")
def api_pause_workflow(id: str):
    """Pause a workflow via the /api/workflows/ prefix route."""
    pause_workflow(id)
    return {"ok": True, "id": id, "status": "paused"}


@app.post("/api/workflows/{id}/resume")
def api_resume_workflow(id: str):
    """Resume a paused workflow via the /api/workflows/ prefix route."""
    resume_workflow(id)
    return {"ok": True, "id": id, "status": "resumed"}


@app.get("/api/workflows/{id}/versions")
def api_list_workflow_versions(id: str):
    """List in-memory version records for a workflow."""
    mem_versions = get_versions(id)
    disk_versions = list_versions(id)
    return {"memory_versions": mem_versions, "disk_versions": disk_versions}


@app.get("/api/workflows/{id}/pause-status")
def api_get_pause_status(id: str):
    """Return pause status for a workflow via the /api/workflows/ prefix route."""
    return get_pause_status(id)


if __name__ == "__main__":
    import time
    import uvicorn
    uvicorn.run(app, host="0.0.0.0",
                port=int(os.environ.get("WORKFLOW_PORT",
                                        str(load_cfg_port()))))


def load_cfg_port():
    try:
        from settings import load_config
        return load_config().get("workflow", {}).get("port", 8040)
    except Exception:
        return 8040
