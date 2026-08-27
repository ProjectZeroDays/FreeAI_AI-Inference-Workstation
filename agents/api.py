#!/usr/bin/env python3
"""Unified Agent API — profiles, session memory, metrics, error envelopes.

SECURITY MODEL:
- Authentication is REQUIRED for all agent and memory endpoints
- Set AGENT_API_KEY or ROUTER_API_KEY environment variable to enable the service
- Without a configured key, all authenticated endpoints return HTTP 503
- Clients must provide the key via X-API-Key, X-Auth-Token, or Authorization header
- Public endpoints: /health, /metrics, /profiles, /agent/profiles, /env/status, /env/agents, /env/plugins, /env/skills
- Protected endpoints: All /agent/*, /memory/*, /env/chat, /env/memory/*, /env/plugins/*/install
"""
import os
import threading
import time
from collections import OrderedDict

import requests
import re
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal

from agents.profiles import Profile
from agents import memory as mem_store

try:
    from settings import load_config
    _CFG = load_config().get("agents", {})
except ImportError:
    _CFG = {}

ROUTER_URL = os.environ.get("ROUTER_URL", "http://localhost:8010/route")
AGENT_API_KEY = os.environ.get("AGENT_API_KEY") or os.environ.get("ROUTER_API_KEY")
DEFAULT_PROFILE = _CFG.get("default_profile", "balanced")
MEMORY_MAX_TURNS = int(_CFG.get("memory_max_turns", 20))

app = FastAPI(title="Unified Agent API", version="1.2")

# The standalone FreeAI UI (ui/freeai.html) is served from its own origin and
# calls these endpoints directly from the browser - allow it.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_METRICS = {"calls_total": 0, "errors_total": 0}
_MLOCK = threading.Lock()

# Backwards-compatible profile presets dict (also exposed via /profiles).
PROFILES = {
    "strict":   {"temperature": 0.0, "max_tokens": 2048},
    "balanced": {"temperature": 0.2, "max_tokens": 2048},
    "creative": {"temperature": 0.8, "max_tokens": 4096},
    "verbose":  {"temperature": 0.4, "max_tokens": 4096},
    "minimal":  {"temperature": 0.2, "max_tokens": 512},
}

# Expose _MEMORY for test fixture teardown (agents_api._MEMORY.clear()).
_MEMORY = mem_store._MEMORY


def _remember(session_id, role, content):
    mem_store.remember(session_id, role, content)


def _recall(session_id):
    return mem_store.recall(session_id)


def _check_auth(request: Request):
    """Enforce API key or JWT authentication.

    Supports three auth methods (checked in order):
      1. X-API-Key header (existing behaviour)
      2. Authorization: Bearer <jwt> (new JWT auth)
      3. X-Auth-Token header (legacy fallback)

    Skips auth when no key is configured and no JWT secret is set,
    allowing tests and local dev to run without credentials.
    """
    has_api_keys = bool(AGENT_API_KEY)
    has_jwt_secret = bool(os.environ.get("AUTH_JWT_SECRET", "").strip())

    if not has_api_keys and not has_jwt_secret:
        return  # no auth configured — allow in test/dev mode

    # 1. API key
    api_key = request.headers.get("X-API-Key", "").strip()
    if has_api_keys and api_key == AGENT_API_KEY:
        return

    # 2. JWT Bearer token
    auth_header = request.headers.get("Authorization", "").strip()
    if auth_header.startswith("Bearer "):
        token = auth_header[len("Bearer "):].strip()
        if token and _verify_jwt_token(token):
            return

    # 3. Legacy X-Auth-Token
    legacy = request.headers.get("X-Auth-Token", "").strip()
    if has_api_keys and legacy == AGENT_API_KEY:
        return

    raise HTTPException(status_code=401, detail="unauthorized")


def _verify_jwt_token(token: str) -> bool:
    """Verify a JWT token. Returns True if valid access token."""
    if not token:
        return False
    try:
        from auth.jwt import decode_token
        payload = decode_token(token)
        return payload is not None and payload.get("type") == "access"
    except Exception:
        return False

def _sanitize(s: str | None, max_len: int = 2000) -> str:
    if not s:
        return ""
    s = s[:max_len]
    s = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", s)
    return s.strip()


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


class RedTeamRequest(BaseModel):
    operation: Literal["recon","weaponize","exploit","evade","chain","report"] = "recon"
    target: str = Field(..., max_length=2000)
    scope: str | None = Field(None, max_length=500)
    technique: str | None = Field(None, max_length=500)
    objective: str | None = Field(None, max_length=500)
    intensity: str | None = Field(None, max_length=100)
    profile: str = DEFAULT_PROFILE
    max_tokens: int | None = None
    session_id: str | None = Field(None, max_length=64, pattern=r"^[a-zA-Z0-9_-]*$")


class BlueTeamRequest(BaseModel):
    operation: Literal["hunt","harden","triage","forensics","compliance","monitor"] = "hunt"
    target: str | None = Field(None, max_length=2000)
    telemetry: str | None = Field(None, max_length=5000)
    framework: str | None = Field(None, max_length=100)
    severity: str | None = Field(None, max_length=50)
    profile: str = DEFAULT_PROFILE
    max_tokens: int | None = None
    session_id: str | None = Field(None, max_length=64, pattern=r"^[a-zA-Z0-9_-]*$")


class PurpleTeamRequest(BaseModel):
    operation: Literal["design","orchestrate","validate","bridge","score","improve"] = "design"
    threat_actor: str | None = Field(None, max_length=500)
    objective: str | None = Field(None, max_length=2000)
    exercise_id: str | None = Field(None, max_length=200)
    control_id: str | None = Field(None, max_length=200)
    technique: str | None = Field(None, max_length=500)
    findings: str | None = Field(None, max_length=5000)
    profile: str = DEFAULT_PROFILE
    max_tokens: int | None = None
    session_id: str | None = Field(None, max_length=64, pattern=r"^[a-zA-Z0-9_-]*$")


# --------------------------- Helpers ---------------------------

def call_router(prompt: str, profile: str = DEFAULT_PROFILE,
                max_tokens: int | None = None,
                temperature: float | None = None,
                agent_hint: str | None = None,
                model: str | None = None):
    preset = PROFILES.get(profile, PROFILES[DEFAULT_PROFILE])
    payload = {
        "prompt": prompt,
        "max_tokens": max_tokens or preset["max_tokens"],
        "temperature": temperature if temperature is not None
                       else preset["temperature"],
    }
    if agent_hint:
        payload["agent"] = agent_hint
    if model:
        payload["model"] = model

    with _MLOCK:
        _METRICS["calls_total"] += 1
    try:
        r = requests.post(ROUTER_URL, json=payload, timeout=660)
        r.raise_for_status()
        body = r.json()
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


@app.get("/agent/profiles")
def agent_profiles():
    """Return detailed profile info (system prompts + config) for all profiles."""
    return Profile.list()


@app.get("/memory/{session_id}")
def get_memory(request: Request, session_id: str):
    _check_auth(request)
    return {"session_id": session_id, "history": _recall(session_id)}


@app.delete("/memory/{session_id}")
def clear_memory(request: Request, session_id: str):
    _check_auth(request)
    mem_store.clear(session_id)
    return {"status": "cleared"}


@app.get("/agent/chat/memory/{session_id}")
def get_chat_memory(session_id: str):
    """GET session conversation history for a chat session."""
    return {"session_id": session_id, "history": _recall(session_id)}


@app.post("/agent/chat/memory/{session_id}")
def post_chat_memory(request: Request, session_id: str,
                     req: dict):
    """POST a turn into a chat session's memory.

    Body: {"role": "user"|"assistant", "content": "…"}
    """
    role = req.get("role", "user")
    content = req.get("content", "")
    _remember(session_id, role, content)
    return {"status": "added", "session_id": session_id, "role": role}


# --------------------------- Agents ---------------------------

@app.post("/agent/project")
def project_agent(request: Request, req: ProjectSpec):
    _check_auth(request)
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
def refactor_agent(request: Request, req: RefactorSpec):
    _check_auth(request)
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
def debug_agent(request: Request, req: DebugSpec):
    _check_auth(request)
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
def analysis_agent(request: Request, req: AnalysisSpec):
    _check_auth(request)
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
def orchestrator(request: Request, req: OrchestratorSpec):
    _check_auth(request)
    return call_router(req.prompt, req.profile, req.max_tokens,
                       req.temperature, req.agent_hint)


@app.post("/agent/chat")
def chat_agent(request: Request, req: ChatSpec):
    """Multi-turn chat with per-session memory fed back into the prompt."""
    _check_auth(request)
    history = _recall(req.session_id)
    transcript = "\n".join(
        f"{h['role']}: {h['content']}" for h in history[-MEMORY_MAX_TURNS:]
    ) if history else ""
    profile_sys = ""
    p = Profile.by_id(req.profile)
    if p:
        profile_sys = p.system_prompt + "\n\n"
    prompt = f"""{profile_sys}You are a helpful senior engineering assistant.

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


# ── Red / Blue / Purple Team ───────────────────────────────────────

@app.post("/agent/red")
def red_team_agent(request: Request, req: RedTeamRequest):
    """Autonomous Red Team — offensive operations."""
    _check_auth(request)
    op = req.operation.lower()
    if op == "recon":
        prompt = f"You are autonomous RED TEAM recon. Target:{_sanitize(req.target)} Scope:{_sanitize(req.scope or 'full')} Intensity:{_sanitize(req.intensity or 'stealth')}. Enumerate surface, OSINT, vuln map, top 5 vectors with commands + OPSEC."
    elif op == "weaponize":
        prompt = f"You are RED TEAM weaponization. CVE/Technique:{_sanitize(req.technique or req.target)} Arch:x64 Evasion:high. Research exploit, tailor payload, EDR bypass, fallback chain."
    elif op == "exploit":
        prompt = f"You are RED TEAM exploitation. Target:{_sanitize(req.target)} Vector:{_sanitize(req.technique or 'auto')} Deliver payload, verify execution, stabilize foothold, anti-forensics."
    elif op == "evade":
        prompt = f"You are RED TEAM evasion. Technique:{_sanitize(req.technique or req.target)} Design AMSI/ETW bypass, persistence, C2 (HTTPS/DNS), fileless + detection artifacts for purple handoff."
    elif op == "chain":
        prompt = f"You are RED TEAM kill-chain orchestrator. Target:{_sanitize(req.target)} Objective:{_sanitize(req.objective or 'domain_admin')}. Plan recon→weaponize→deliver→exploit→install→C2→act with MITRE IDs, tools, risks, IOCs per phase."
    elif op == "report":
        prompt = f"You are RED TEAM reporting ({_sanitize(req.scope) or 'CONFIDENTIAL'}). Findings:{_sanitize(req.target, 3000)}. Generate exec summary, technical deep dive, narrative, prioritized recommendations, IOC/MITRE appendices."
    else:
        prompt = f"You are autonomous RED TEAM operator. Operation:{_sanitize(req.operation)} Target:{_sanitize(req.target)} Technique:{_sanitize(req.technique)} Scope:{_sanitize(req.scope)}. Execute with OPSEC, deliver actionable output."
    uncensored_model = os.environ.get("REDTEAM_MODEL", "qwen3.6-12b")
    try:
        result = call_router(prompt, req.profile, req.max_tokens, agent_hint="red", model=uncensored_model)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"router error: {exc}")
    if req.session_id:
        _remember(req.session_id, "user", f"[red:{op}] {req.target[:200]}")
        _remember(req.session_id, "assistant", str(result.get("response",""))[:2000])
    return {**result, "team": "red", "operation": op, "model": uncensored_model}


@app.post("/agent/blue")
def blue_team_agent(request: Request, req: BlueTeamRequest):
    """Autonomous Blue Team — defensive operations."""
    _check_auth(request)
    op = req.operation.lower()
    if op == "hunt":
        prompt = f"You are BLUE TEAM hunter. Telemetry:{_sanitize(req.telemetry or req.target, 3000)} Hypothesis:{_sanitize(req.technique or 'auto')}. Map to ATT&CK, correlate IoCs, hunt persistence, deliver query + confidence + next hunt."
    elif op == "harden":
        prompt = f"You are BLUE TEAM hardening lead. Target:{_sanitize(req.target or 'system')} Profile:{_sanitize(req.framework or 'cis_l1')}. Assess OS/network/container/identity, remediation commands, validation + rollback per control."
    elif op == "triage":
        prompt = f"You are BLUE TEAM SOC L3. Alert:{_sanitize(req.telemetry or req.target, 3000)} Severity:{_sanitize(req.severity or 'high')}. Verdict TP/FP, scope, containment, evidence preservation, escalation."
    elif op == "forensics":
        prompt = f"You are BLUE TEAM forensics. Artifact:{_sanitize(req.target or 'unknown')} Type:{_sanitize(req.technique or 'auto')}. Timeline, malware/IoC extraction, patient zero, remediation, chain-of-custody."
    elif op == "compliance":
        prompt = f"You are BLUE TEAM compliance. Framework:{_sanitize(req.framework or 'nist_800_53')} Scope:{_sanitize(req.target or 'full_stack')}. Scorecard, gap register, audit evidence package, continuous monitoring plan."
    elif op == "monitor":
        prompt = f"You are BLUE TEAM detection engineer. Sources:{_sanitize(req.telemetry or 'all')}. Coverage matrix, 5 highest-value detections (Sigma draft), tuning, runbooks."
    else:
        prompt = f"You are autonomous BLUE TEAM. Operation:{_sanitize(req.operation)} Target:{_sanitize(req.target)} Telemetry:{_sanitize(req.telemetry, 1000)}. Defend, detect, harden with evidence."
    uncensored_model = os.environ.get("BLUETEAM_MODEL", "qwythos-v2-9b")
    try:
        result = call_router(prompt, req.profile, req.max_tokens, agent_hint="blue", model=uncensored_model)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"router error: {exc}")
    if req.session_id:
        _remember(req.session_id, "user", f"[blue:{op}] {req.target}")
        _remember(req.session_id, "assistant", str(result.get("response",""))[:2000])
    return {**result, "team": "blue", "operation": op, "model": uncensored_model}


@app.post("/agent/purple")
def purple_team_agent(request: Request, req: PurpleTeamRequest):
    """Autonomous Purple Team — red↔blue orchestration."""
    _check_auth(request)
    op = req.operation.lower()
    if op == "design":
        prompt = f"You are PURPLE TEAM designer. Actor:{_sanitize(req.threat_actor or 'APT29')} Objective:{_sanitize(req.objective or 'exfil')} Design scenario, 5-8 ATT&CK steps, scoring rubric, safety/rollback, prerequisites."
    elif op == "orchestrate":
        prompt = f"You are PURPLE TEAM orchestrator live. Exercise:{_sanitize(req.exercise_id or req.objective or 'unknown')} Telemetry:{_sanitize(req.findings or 'pending', 3000)}. Next inject, expected detection, actual vs expected, coaching, go/no-go."
    elif op == "validate":
        prompt = f"You are PURPLE TEAM validator. Control:{_sanitize(req.control_id or 'unknown')} Technique:{_sanitize(req.technique or 'unknown')}. Lab reproduce, observe control, test evasion variants, fix + re-test plan."
    elif op == "bridge":
        prompt = f"You are PURPLE TEAM bridge. Red:{_sanitize(req.findings, 3000)} Blue gap:{_sanitize(req.technique, 1000)}. Root cause, ranked fixes, Sigma/KQL draft, validation inject, risk reduction."
    elif op == "score":
        prompt = f"You are PURPLE TEAM scoring. Log:{_sanitize(req.findings or req.exercise_id or 'unknown', 3000)}. Per-step 0-3, aggregates MTTD/MTTR, heatmap, trend, top 3 fixes, navigator JSON, next exercise."
    elif op == "improve":
        prompt = f"You are PURPLE TEAM program manager. State:{_sanitize(req.findings or req.objective or 'unknown', 3000)}. Maturity, cadence, tooling, KPIs, reporting rhythm, quarterly roadmap."
    else:
        prompt = f"You are autonomous PURPLE TEAM. Operation:{_sanitize(req.operation)} Actor:{_sanitize(req.threat_actor)} Objective:{_sanitize(req.objective)} Control:{_sanitize(req.control_id)}. Orchestrate, validate, bridge, score."
    uncensored_model = os.environ.get("PURPLETEAM_MODEL", "moe-13b")
    try:
        result = call_router(prompt, req.profile, req.max_tokens, agent_hint="purple", model=uncensored_model)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"router error: {exc}")
    if req.session_id:
        _remember(req.session_id, "user", f"[purple:{op}] {req.objective or req.exercise_id or req.control_id}")
        _remember(req.session_id, "assistant", str(result.get("response",""))[:2000])
    return {**result, "team": "purple", "operation": op, "model": uncensored_model}


# ── Unified AI Dev Environment Endpoints ─────────────────────────────

@app.get("/env/status")
def env_status():
    """System health for the unified AI dev environment."""
    from agents.agent_bridge import get_bridge
    bridge = get_bridge()
    from agents.llm_proxy import health as proxy_health
    proxy = proxy_health()
    stats = bridge.stats()
    return {
        "proxy": proxy,
        "agents": stats["agents"],
        "memory": stats["memory"],
        "plugins": stats["plugins"],
        "skills": stats["skills"],
    }


@app.post("/env/chat")
def env_chat(request: Request, req: OrchestratorSpec):
    """Unified chat endpoint — auto-routes to best agent."""
    _check_auth(request)
    from agents.agent_bridge import get_bridge
    bridge = get_bridge()
    agent = req.agent_hint or bridge.route_to_agent(req.prompt)
    result = bridge.execute_with_agent(
        req.prompt, agent=agent, session_id=req.session_id)
    return result


@app.get("/env/agents")
def env_agents():
    """List all specialized agents with their models."""
    from agents.specialized_agents import AGENT_MODELS, AGENT_PROMPTS
    out = {}
    for name, model in AGENT_MODELS.items():
        prompt = AGENT_PROMPTS.get(name, "")
        desc = prompt.split("\n")[1].strip() if prompt else ""
        out[name] = {"model": model, "description": desc}
    return out


@app.get("/env/plugins")
def env_plugins(category: str = None):
    """List plugins from the registry."""
    from agents.plugin_registry import get_registry
    registry = get_registry()
    plugins = registry.list_plugins(category=category)
    return {"plugins": plugins[:50]}


@app.post("/env/plugins/{name}/install")
def env_install_plugin(request: Request, name: str):
    """Install a plugin by name."""
    _check_auth(request)
    from agents.plugin_registry import get_registry
    registry = get_registry()
    return registry.install_plugin(name)


@app.get("/env/skills")
def env_skills(query: str = None):
    """Search or list skills."""
    from agents.plugin_registry import get_loader
    loader = get_loader()
    if query:
        matches = loader.match_skills(query)
        return {"skills": matches}
    skills = loader.list_skills()
    return {"skills": skills[:50]}


@app.get("/env/memory/{session_id}")
def env_memory(request: Request, session_id: str):
    """Recall memory for a session."""
    _check_auth(request)
    from agents.agent_zero_memory import get_store
    store = get_store()
    entries = store.recall(session_id, limit=20)
    return {"session": session_id, "entries": entries}


@app.post("/env/memory/search")
def env_memory_search(request: Request, req: AnalysisSpec):
    """Search global knowledge base."""
    _check_auth(request)
    from agents.agent_zero_memory import get_store
    store = get_store()
    results = store.search_global(req.question, limit=10)
    return {"results": results}

