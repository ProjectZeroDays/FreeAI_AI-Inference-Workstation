#!/usr/bin/env python3
import os

import requests

from fastapi import FastAPI
from pydantic import BaseModel

ROUTER_URL = os.environ.get("ROUTER_URL", "http://localhost:8010/route")

app = FastAPI(title="Unified Agent API", version="1.0")


# ---------------------------
# Request Models
# ---------------------------

class ProjectSpec(BaseModel):
    spec: str
    max_tokens: int = 4096
    temperature: float = 0.2


class RefactorSpec(BaseModel):
    code: str
    language: str = "python"
    goals: str = "clean, idiomatic, maintainable"
    max_tokens: int = 2048


class DebugSpec(BaseModel):
    code: str
    error: str
    language: str = "python"
    max_tokens: int = 2048


class AnalysisSpec(BaseModel):
    context: str
    question: str
    max_tokens: int = 2048


class OrchestratorSpec(BaseModel):
    prompt: str
    max_tokens: int = 2048
    temperature: float = 0.2


# ---------------------------
# Helper: call router
# ---------------------------

def call_router(prompt: str, max_tokens: int, temperature: float):
    payload = {
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    r = requests.post(ROUTER_URL, json=payload)
    r.raise_for_status()
    return r.json()


# ---------------------------
# Agents
# ---------------------------

@app.post("/agent/project")
def project_agent(req: ProjectSpec):
    prompt = f"""
You are a senior production engineer.

Task: Turn this spec into a production-ready project.

Spec:
{req.spec}

Deliver:
- Architecture overview
- Tech stack
- Directory structure
- Key services/modules
- Data models
- API contracts
- CI/CD outline
- Infra notes (Docker/K8s if relevant)
"""
    return call_router(prompt, req.max_tokens, req.temperature)


@app.post("/agent/refactor")
def refactor_agent(req: RefactorSpec):
    prompt = f"""
You are a refactoring specialist for {req.language}.

Task: Refactor the following code.

Goals: {req.goals}

Code:
```{req.language}
{req.code}
```

Deliver:
- Refactored code
- Brief explanation of changes
"""
    return call_router(prompt, req.max_tokens, 0.2)


@app.post("/agent/debug")
def debug_agent(req: DebugSpec):
    prompt = f"""
You are a debugging specialist for {req.language}.

Task: Find and fix the bug.

Code:
```{req.language}
{req.code}
```

Error:
{req.error}

Deliver:
- Root cause explanation
- Fixed code
- Notes on prevention
"""
    return call_router(prompt, req.max_tokens, 0.2)


@app.post("/agent/analyze")
def analysis_agent(req: AnalysisSpec):
    prompt = f"""
You are a reasoning specialist.

Context:
{req.context}

Question:
{req.question}

Think step by step, then answer clearly.
"""
    return call_router(prompt, req.max_tokens, 0.2)


@app.post("/agent/orchestrate")
def orchestrator(req: OrchestratorSpec):
    return call_router(req.prompt, req.max_tokens, req.temperature)


@app.get("/health")
def health():
    return {"status": "ok"}
