#!/usr/bin/env python3
import json
import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

try:
    from workflow.engine import from_definition, to_definition
    from workflow.registry import get_workflow, list_workflows
    from workflow.validator import validate_workflow
    from workflow.audit import read_audit
except ImportError:
    from engine import from_definition, to_definition
    from registry import get_workflow, list_workflows
    from validator import validate_workflow
    from audit import read_audit

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
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
        raise HTTPException(status_code=500, detail=str(e))


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


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
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
