#!/usr/bin/env python3
import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

try:
    from workflow.engine import from_definition, to_definition, \
        validate_workflow
    from workflow.registry import get_workflow, list_workflows
except ImportError:
    from engine import from_definition, to_definition, validate_workflow
    from registry import get_workflow, list_workflows

app = FastAPI(title="FreeAI Workflow Engine", version="1.1")


class WorkflowRequest(BaseModel):
    workflow: str
    context: dict = Field(default_factory=dict)
    strict_validation: bool = False


class InlineWorkflowRequest(BaseModel):
    definition: dict


class ValidateRequest(BaseModel):
    steps: list


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
    try:
        from workflow.engine import Step
    except ImportError:
        from engine import Step

    class _Shim:
        pass

    steps = []
    for s in req.steps:
        step = _Shim()
        step.name = s.get("name", "?")
        step.agent = s.get("agent", "orchestrate")
        step.consumes = s.get("consumes", [])
        step.produces = s.get("produces", [])
        steps.append(step)
    return {"warnings": validate_workflow(steps)}


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
