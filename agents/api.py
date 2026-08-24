#!/usr/bin/env python3
"""Unified Agent API — profiles, session memory, metrics, error envelopes."""
import os
import threading
import time
from collections import OrderedDict

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

try:
    from settings import load_config
    _CFG = load_config().get("agents", {})
except ImportError:
    _CFG = {}

ROUTER_URL = os.environ.get("ROUTER_URL", "http://localhost:8010/route")
DEFAULT_PROFILE = _CFG.get("default_profile", "balanced")
MEMORY_MAX_TURNS = int(_CFG.get("memory_max_turns", 20))

app = FastAPI(title="Unified Agent API", version="1.1")

_METRICS = {"calls_total": 0, "errors_total": 0}
_MLOCK = threading.Lock()

# Agent profiles: temperature / max_tokens presets.
PROFILES = {
    "strict":   {"temperature": 0.0, "max_tokens": 2048},
    "balanced": {"temperature": 0.2, "max_tokens": 2048},
    "creative": {"temperature": 0.8, "max_tokens": 4096},
    "verbose":  {"temperature": 0.4, "max_tokens": 4096},
    "minimal":  {"temperature": 0.2, "max_tokens": 512},
}

# Session memory: session_id -> list of {"role","content"}
_MEMORY = OrderedDict()
_MMEM_LOCK = threading.Lock()


def _remember(session_id, role, content):
    if not session_id:
        return
    with _MMEM_LOCK:
        hist = _MEMORY.setdefault(session_id, [])
        hist.append({"role": role, "content": content})
        while len(hist) > MEMORY_MAX_TURNS:
            hist.pop(0)
        _MEMORY.move_to_end(session_id)
        while len(_MEMORY) > 100:
            _MEMORY.popitem(last=False)


def _recall(session_id):
    with _MMEM_LOCK:
        return list(_MEMORY.get(session_id, []))


# --------------------------- Request Models ---------------------------

class ProjectSpec(BaseModel):
    spec: str
    profile: str = DEFAULT_PROFILE
    max_tokens: int | None = None
    session_id: str | None = None


class RefactorSpec(BaseModel):
    code: str
    language: str = "python"
    goals: str = "clean, idiomatic, maintainable"
    profile: str = DEFAULT_PROFILE
    max_tokens: int | None = None


class DebugSpec(BaseModel):
    code: str
    error: str
    language: str = "python"
    profile: str = DEFAULT_PROFILE
    max_tokens: int | None = None


class AnalysisSpec(BaseModel):
    context: str
    question: str
    profile: str = DEFAULT_PROFILE
    max_tokens: int | None = None


class OrchestratorSpec(BaseModel):
    prompt: str
    profile: str = DEFAULT_PROFILE
    max_tokens: int | None = None
    temperature: float | None = None
    agent_hint: str | None = None


class ChatSpec(BaseModel):
    message: str
    session_id: str
    profile: str = DEFAULT_PROFILE
    max_tokens: int | None = None


# --------------------------- Helpers ---------------------------

def call_router(prompt: str, profile: str = DEFAULT_PROFILE,
                max_tokens: int | None = None,
                temperature: float | None = None,
                agent_hint: str | None = None):
    preset = PROFILES.get(profile, PROFILES[DEFAULT_PROFILE])
    payload = {
        "prompt": prompt,
        "max_tokens": max_tokens or preset["max_tokens"],
        "temperature": temperature if temperature is not None
                       else preset["temperature"],
    }
    if agent_hint:
        payload["agent"] = agent_hint

    with _MLOCK:
        _METRICS["calls_total"] += 1
    try:
        r = requests.post(ROUTER_URL, json=payload, timeout=660)
        r.raise_for_status()
        body = r.json()
        with _MLOCK:
            pass
        return body
    except Exception as exc:
        with _MLOCK:
            _METRICS["errors_total"] += 1
        raise HTTPException(status_code=502,
                            detail=f"router unreachable: {exc}")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/metrics")
def metrics():
    with _MLOCK:
        return dict(_METRICS)


@app.get("/profiles")
def profiles():
    return PROFILES


@app.get("/memory/{session_id}")
def get_memory(session_id: str):
    return {"session_id": session_id, "history": _recall(session_id)}


@app.delete("/memory/{session_id}")
def clear_memory(session_id: str):
    with _MMEM_LOCK:
        _MEMORY.pop(session_id, None)
    return {"status": "cleared"}


# --------------------------- Agents ---------------------------

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
    result = call_router(prompt, req.profile, req.max_tokens)
    _remember(req.session_id, "user", req.spec)
    _remember(req.session_id, "assistant",
              str(result.get("response", ""))[:2000])
    return result


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
    return call_router(prompt, req.profile, req.max_tokens)


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
    return call_router(prompt, req.profile, req.max_tokens)


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
    return call_router(prompt, req.profile, req.max_tokens)


@app.post("/agent/orchestrate")
def orchestrator(req: OrchestratorSpec):
    return call_router(req.prompt, req.profile, req.max_tokens,
                       req.temperature, req.agent_hint)


@app.post("/agent/chat")
def chat_agent(req: ChatSpec):
    """Multi-turn chat with per-session memory fed back into the prompt."""
    history = _recall(req.session_id)
    transcript = "\n".join(
        f"{h['role']}: {h['content']}" for h in history[-MEMORY_MAX_TURNS:]
    ) if history else ""
    prompt = f"""
You are a helpful senior engineering assistant.

{'Previous conversation:' if transcript else ''}
{transcript}

User: {req.message}

Respond directly.
""".strip()
    result = call_router(prompt, req.profile, req.max_tokens,
                         agent_hint="chat")
    _remember(req.session_id, "user", req.message)
    _remember(req.session_id, "assistant",
              str(result.get("response", ""))[:2000])
    return result
