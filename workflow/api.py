#!/usr/bin/env python3
import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

try:
    from workflow.registry import get_workflow, list_workflows
except ImportError:
    from registry import get_workflow, list_workflows

app = FastAPI(title="Tokugawa Workflow Engine", version="1.0")


class WorkflowRequest(BaseModel):
    workflow: str
    context: dict


@app.get("/workflows")
def workflows():
    return {"workflows": list_workflows()}


@app.post("/workflow/run")
def run_workflow(req: WorkflowRequest):
    wf = get_workflow(req.workflow)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")

    try:
        result = wf.execute(req.context)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0",
                port=int(os.environ.get("WORKFLOW_PORT", "8040")))
