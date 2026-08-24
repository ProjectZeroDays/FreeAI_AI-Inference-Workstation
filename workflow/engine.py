#!/usr/bin/env python3
import concurrent.futures
import os
import time
import uuid
from typing import Any, Callable, Dict, List

import requests

AGENT_API = os.environ.get("AGENT_API", "http://localhost:8020")


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

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        payload = self.prompt_builder(context)
        url = f"{AGENT_API}/agent/{self.agent}"

        for attempt in range(3):
            try:
                r = requests.post(url, json=payload, timeout=600)
                r.raise_for_status()
                result = r.json()
                return {self.name: result}
            except Exception:
                if attempt == 2:
                    raise
                time.sleep(2)


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


class Workflow:
    def __init__(self, name: str, steps: List[Step]):
        self.name = name
        self.steps = steps

    def execute(self, initial_context: Dict[str, Any]) -> Dict[str, Any]:
        context = dict(initial_context)
        context["_workflow_id"] = str(uuid.uuid4())
        context["_started_at"] = time.time()
        outputs: Dict[str, Any] = {}

        print(f"[workflow] Starting: {self.name} ({context['_workflow_id']})")

        for step in self.steps:
            print(f"[workflow] Step: {step.name}")
            result = step.run(context)
            print(f"[workflow] Step complete: {step.name}")
            outputs.update(result)
            # merge step output into context for downstream steps
            context[step.name] = result[step.name]

        context["_finished_at"] = time.time()
        return {
            "workflow": self.name,
            "workflow_id": context["_workflow_id"],
            "started_at": context["_started_at"],
            "finished_at": context["_finished_at"],
            "steps": [s.name for s in self.steps],
            "outputs": outputs,
        }


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
        "question": "Identify risks, bottlenecks, and improvement opportunities.",
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


if __name__ == "__main__":
    result = run_project_workflow(
        "Build a production-ready REST API for a rideshare app "
        "with auth, trips, payments, and admin dashboard.",
        language="python",
    )
    print(result)
