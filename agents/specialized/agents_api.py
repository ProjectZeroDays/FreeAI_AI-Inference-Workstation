#!/usr/bin/env python3
"""Seven Specialized Agents — oh-my-opencode-slim style orchestration.

Agents:
  1. orchestrator  - Primary coordinator. Decomposes tasks, dispatches subagents.
  2. explorer      - Codebase exploration and understanding.
  3. oracle        - Architecture review and deep technical analysis.
  4. council       - Multi-model consensus for critical decisions.
  5. librarian     - Documentation generation and maintenance.
  6. designer      - UI/UX design and frontend architecture.
  7. fixer         - Bug diagnosis and repair specialist.

Each agent is a FastAPI endpoint that routes to the best model for the task.
"""
import os
import json
import time
import threading
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

ROOT = Path(__file__).parent.parent
ROUTER_URL = os.environ.get("ROUTER_URL", "http://localhost:8010/route")
PROXY_URL = os.environ.get("PROXY_URL", "http://localhost:8100/proxy")
MEMORY_URL = os.environ.get("MEMORY_URL", "http://localhost:8110")

app = FastAPI(title="Specialized Agents API", version="1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8030", "http://127.0.0.1:8030"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_AGENT_LOCK = threading.Lock()
_RUNS = {}

# ── Agent model preferences ──────────────────────────────────────────
AGENT_MODELS = {
    "orchestrator": os.environ.get("ORCHESTRATOR_MODEL", "anthropic/claude-opus-4-6"),
    "explorer":     os.environ.get("EXPLORER_MODEL", "google/gemini-2.5-flash"),
    "oracle":       os.environ.get("ORACLE_MODEL", "anthropic/claude-opus-4-6"),
    "council":      os.environ.get("COUNCIL_MODEL", "multi"),
    "librarian":    os.environ.get("LIBRARIAN_MODEL", "google/gemini-2.5-flash"),
    "designer":     os.environ.get("DESIGNER_MODEL", "anthropic/claude-sonnet-4-5"),
    "fixer":        os.environ.get("FIXER_MODEL", "deepseek/deepseek-chat"),
}

PROFILES = {
    "strict":  {"temperature": 0.0, "max_tokens": 2048},
    "balanced": {"temperature": 0.2, "max_tokens": 2048},
    "creative": {"temperature": 0.8, "max_tokens": 4096},
    "verbose":  {"temperature": 0.4, "max_tokens": 4096},
}


def call_router(prompt, model=None, profile="balanced", max_tokens=None):
    preset = PROFILES.get(profile, PROFILES["balanced"])
    payload = {
        "prompt": prompt,
        "max_tokens": max_tokens or preset["max_tokens"],
        "temperature": preset["temperature"],
    }
    if model:
        payload["model"] = model
    import requests
    try:
        r = requests.post(ROUTER_URL, json=payload, timeout=660)
        r.raise_for_status()
        return r.json()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"router error: {exc}")


def call_proxy(prompt, model=None, profile="balanced", max_tokens=None):
    preset = PROFILES.get(profile, PROFILES["balanced"])
    payload = {
        "prompt": prompt,
        "max_tokens": max_tokens or preset["max_tokens"],
        "temperature": preset["temperature"],
    }
    if model:
        payload["model"] = model
    import requests
    try:
        r = requests.post(PROXY_URL, json=payload, timeout=660)
        r.raise_for_status()
        return r.json()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"proxy error: {exc}")


def _recall_memory(session_id):
    """Pull cross-session knowledge for context."""
    try:
        import requests
        r = requests.get(f"{MEMORY_URL}/recall",
                         json={"session_id": session_id, "limit": 5},
                         timeout=5)
        if r.ok:
            data = r.json()
            knowledge = data.get("knowledge", [])
            if knowledge:
                return "\n".join(f"[{k['role']}] {k['content'][:300]}"
                                 for k in knowledge[-3:])
    except Exception:
        pass
    return ""


# ── Request models ───────────────────────────────────────────────────
class AgentRequest(BaseModel):
    prompt: str
    session_id: Optional[str] = None
    profile: str = "balanced"
    max_tokens: Optional[int] = None
    model: Optional[str] = None


class ExplorerRequest(BaseModel):
    path: str = "."
    patterns: Optional[list[str]] = None
    depth: int = 3
    session_id: Optional[str] = None
    profile: str = "balanced"


class OracleRequest(BaseModel):
    target: str
    question: str
    context_files: Optional[list[str]] = None
    session_id: Optional[str] = None
    profile: str = "balanced"


class CouncilRequest(BaseModel):
    question: str
    options: list[str]
    criteria: Optional[str] = None
    session_id: Optional[str] = None
    profile: str = "balanced"


class LibrarianRequest(BaseModel):
    scope: str
    format: str = "markdown"
    session_id: Optional[str] = None
    profile: str = "balanced"


class DesignerRequest(BaseModel):
    spec: str
    style: str = "modern"
    constraints: Optional[str] = None
    session_id: Optional[str] = None
    profile: str = "creative"


class FixerRequest(BaseModel):
    code: str
    error: str
    language: str = "python"
    session_id: Optional[str] = None
    profile: str = "strict"


# ── Agent endpoints ──────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "agents": list(AGENT_MODELS.keys())}


@app.get("/agents")
def list_agents():
    return {
        name: {"model": model, "description": _agent_desc(name)}
        for name, model in AGENT_MODELS.items()
    }


def _agent_desc(name):
    descs = {
        "orchestrator": "Primary coordinator. Decomposes tasks, dispatches subagents, aggregates results.",
        "explorer": "Codebase exploration. Maps architecture, dependencies, and data flow.",
        "oracle": "Deep technical analysis. Architecture review, trade-off evaluation.",
        "council": "Multi-model consensus. Runs question through multiple models for robust answers.",
        "librarian": "Documentation. Generates, maintains, and syncs project docs.",
        "designer": "UI/UX design. Creates specs, prototypes, and design systems.",
        "fixer": "Bug fixing. Diagnoses root causes and proposes targeted repairs.",
    }
    return descs.get(name, "")


@app.post("/agent/{name}")
def invoke_agent(name: str, req: AgentRequest):
    if name not in AGENT_MODELS:
        raise HTTPException(status_code=404, detail=f"Unknown agent: {name}")

    model = req.model or AGENT_MODELS[name]
    mem_ctx = _recall_memory(req.session_id) if req.session_id else ""
    _nl = "\n"
    _ctx = f"{_nl}Context from previous sessions:{_nl}{mem_ctx}{_nl}" if mem_ctx else ""

    prompts = {
        "orchestrator": f"""You are the ORCHESTRATOR. Decompose this task and produce a structured plan.
{_ctx}Task: {req.prompt}

Output a JSON plan with:
- objectives (list)
- steps (ordered list with descriptions)
- dependencies (which steps depend on which)
- estimated_complexity (low/medium/high)
- risk_factors (list)""",

        "explorer": f"""You are the EXPLORER. Analyze the codebase at the given path.
{_ctx}Path: {req.prompt}

Produce:
- High-level architecture summary
- Key modules and their responsibilities
- Dependency graph (text description)
- Entry points and data flow
- Potential coupling issues""",

        "oracle": f"""You are the ORACLE. Provide deep technical analysis.
{_ctx}Target: {req.prompt}
Question: {req.prompt}

Think critically. Consider trade-offs, edge cases, and long-term implications.
Deliver a well-reasoned analysis with confidence levels.""",

        "council": f"""You are the COUNCIL. Simulate multiple expert opinions.
{_ctx}Question: {req.prompt}

Role-play 3 different experts (architect, engineer, product) giving their perspective.
Then synthesize a consensus recommendation with reasoning.""",

        "librarian": f"""You are the LIBRARIAN. Create or update documentation.

{_ctx}Scope: {req.prompt}

Produce clear, well-structured documentation. Include:
- Overview and purpose
- Usage examples
- API reference (if applicable)
- Architecture notes
- Troubleshooting section""",

        "designer": f"""You are the DESIGNER. Create UI/UX specifications.

{_ctx}Spec: {req.prompt}

Deliver:
- Design system tokens (colors, typography, spacing)
- Component specifications
- Layout wireframes (ASCII or described)
- Interaction patterns
- Accessibility considerations""",

        "fixer": f"""You are the FIXER. Diagnose and repair bugs.

{_ctx}Code: {req.prompt}

Provide:
- Root cause analysis
- Minimal reproduction steps
- Fixed code with explanations
- Prevention recommendations""",
    }

    prompt = prompts.get(name, f"You are a specialized AI agent. Task: {req.prompt}")
    result = call_proxy(prompt, model=model, profile=req.profile,
                        max_tokens=req.max_tokens)

    # Remember to memory if session provided
    if req.session_id:
        try:
            import requests
            requests.post(f"{MEMORY_URL}/remember", json={
                "session_id": req.session_id,
                "role": "user",
                "content": req.prompt,
            }, timeout=5)
            resp_content = result.get("response", {}).get("content", "")
            requests.post(f"{MEMORY_URL}/remember", json={
                "session_id": req.session_id,
                "role": "assistant",
                "content": resp_content[:2000],
            }, timeout=5)
        except Exception:
            pass

    return {
        **result,
        "agent": name,
        "model_used": model,
    }


# ── Specialized endpoints ────────────────────────────────────────────
@app.post("/agent/explorer/codebase")
def explore_codebase(req: ExplorerRequest):
    model = AGENT_MODELS["explorer"]
    mem_ctx = _recall_memory(req.session_id) if req.session_id else ""
    _nl = "\n"
    _ctx = f"{_nl}Context from previous sessions:{_nl}{mem_ctx}{_nl}" if mem_ctx else ""

    import glob
    structure = []
    try:
        for pattern in req.patterns or ["*.py", "*.js", "*.ts", "*.json", "*.md",
                                        "*.yaml", "*.yml", "*.sh", "*.html", "*.css"]:
            for f in glob.glob(f"{req.path}/**/{pattern}", recursive=True)[:200]:
                structure.append(f)
    except OSError:
        pass

    prompt = f"""You are the EXPLORER analyzing this codebase:

Path: {req.path}
Files found: {len(structure)}

{_ctx}

Produce a comprehensive analysis:
1. Architecture overview (layers, patterns)
2. Key modules and their relationships
3. Entry points and execution flow
4. External dependencies
5. Testing coverage assessment
6. Technical debt indicators"""

    result = call_proxy(prompt, model=model, profile=req.profile)
    return {**result, "agent": "explorer", "files_scanned": len(structure)}


@app.post("/agent/oracle/review")
def oracle_review(req: OracleRequest):
    model = AGENT_MODELS["oracle"]
    mem_ctx = _recall_memory(req.session_id) if req.session_id else ""
    _nl = "\n"
    _ctx = f"{_nl}Context from previous sessions:{_nl}{mem_ctx}{_nl}" if mem_ctx else ""

    context = ""
    if req.context_files:
        import glob
        files = []
        for fp in req.context_files:
            files.extend(glob.glob(fp))
        if files:
            snippets = []
            for fp in files[:10]:
                try:
                    content = Path(fp).read_text()[:3000]
                    snippets.append(f"### {fp}\n{content}")
                except OSError:
                    pass
            context = "\n\n".join(snippets)

    prompt = f"""You are the ORACLE providing deep technical analysis.

{_ctx}
Target: {req.target}
Question: {req.question}
{("Context files:" + _nl + context + _nl) if context else ""}

Deliver a thorough analysis covering:
- Architectural strengths and weaknesses
- Security considerations
- Performance implications
- Scalability assessment
- Recommended improvements with priority"""

    result = call_proxy(prompt, model=model, profile=req.profile)
    return {**result, "agent": "oracle"}


@app.post("/agent/council/decide")
def council_decide(req: CouncilRequest):
    model = AGENT_MODELS["council"]
    mem_ctx = _recall_memory(req.session_id) if req.session_id else ""
    _nl = "\n"
    _ctx = f"{_nl}Context from previous sessions:{_nl}{mem_ctx}{_nl}" if mem_ctx else ""

    prompt = f"""You are the COUNCIL. Simulate a panel of experts debating this question.

{_ctx}Question: {req.question}
Options: {json.dumps(req.options)}
{("Evaluation criteria: " + req.criteria + _nl) if req.criteria else ""}

For each option, have 3 experts (Architect, Engineer, Product) give their view.
Then provide a consensus recommendation with weighted scoring."""

    result = call_proxy(prompt, model=model, profile=req.profile)
    return {**result, "agent": "council", "options_considered": len(req.options)}


@app.post("/agent/librarian/docs")
def librarian_docs(req: LibrarianRequest):
    model = AGENT_MODELS["librarian"]
    mem_ctx = _recall_memory(req.session_id) if req.session_id else ""
    _nl = "\n"
    _ctx = f"{_nl}Context from previous sessions:{_nl}{mem_ctx}{_nl}" if mem_ctx else ""

    prompt = f"""You are the LIBRARIAN creating professional documentation.

{_ctx}Scope: {req.scope}
Format: {req.format}

Produce comprehensive documentation:
- Title and executive summary
- Table of contents
- Detailed sections with examples
- API/reference where applicable
- Getting started guide
- Troubleshooting FAQ"""

    result = call_proxy(prompt, model=model, profile=req.profile)
    return {**result, "agent": "librarian", "format": req.format}


@app.post("/agent/designer/spec")
def designer_spec(req: DesignerRequest):
    model = AGENT_MODELS["designer"]
    mem_ctx = _recall_memory(req.session_id) if req.session_id else ""
    _nl = "\n"
    _ctx = f"{_nl}Context from previous sessions:{_nl}{mem_ctx}{_nl}" if mem_ctx else ""

    prompt = f"""You are the DESIGNER creating UI/UX specifications.

{_ctx}Spec: {req.spec}
Style: {req.style}
{("Constraints: " + req.constraints + _nl) if req.constraints else ""}

Deliver a complete design spec:
- Design tokens (colors, typography, spacing scale)
- Component library specification
- Page layouts (with ASCII wireframes)
- Interaction patterns and states
- Responsive breakpoints
- Accessibility compliance notes"""

    result = call_proxy(prompt, model=model, profile=req.profile)
    return {**result, "agent": "designer", "style": req.style}


@app.post("/agent/fixer/diagnose")
def fixer_diagnose(req: FixerRequest):
    model = AGENT_MODELS["fixer"]
    mem_ctx = _recall_memory(req.session_id) if req.session_id else ""
    _nl = "\n"
    _ctx = f"{_nl}Context from previous sessions:{_nl}{mem_ctx}{_nl}" if mem_ctx else ""

    prompt = f"""You are the FIXER diagnosing and repairing bugs.

{_ctx}Language: {req.language}

Code:
```{req.language}
{req.code}
```

Error:
{req.error}

Follow this process:
1. Reproduce the bug mentally
2. Identify root cause
3. Propose minimal fix
4. Show before/after code
5. Suggest prevention measures"""

    result = call_proxy(prompt, model=model, profile=req.profile)
    return {**result, "agent": "fixer", "language": req.language}


# ── Orchestration endpoint ───────────────────────────────────────────
@app.post("/agent/orchestrate")
def orchestrate(req: AgentRequest):
    """Multi-agent orchestration: decompose and delegate."""
    model = AGENT_MODELS["orchestrator"]
    mem_ctx = _recall_memory(req.session_id) if req.session_id else ""
    _nl = "\n"
    _ctx = f"{_nl}Previous session context:{_nl}{mem_ctx}{_nl}" if mem_ctx else ""

    prompt = f"""You are the MASTER ORCHESTRATOR coordinating specialized agents.

{_ctx}Task: {req.prompt}

Decompose this task and route sub-tasks to appropriate agents:
- orchestrator: coordination and planning
- explorer: codebase understanding
- oracle: architectural analysis
- council: decision-making
- librarian: documentation
- designer: UI/UX
- fixer: bug fixes

For each sub-task, specify:
- Which agent handles it
- What input to give
- Expected output format

Return a structured execution plan."""

    result = call_proxy(prompt, model=model, profile=req.profile,
                        max_tokens=req.max_tokens)

    if req.session_id:
        try:
            import requests
            requests.post(f"{MEMORY_URL}/remember", json={
                "session_id": req.session_id,
                "role": "user",
                "content": req.prompt,
            }, timeout=5)
        except Exception:
            pass

    return {**result, "agent": "orchestrator", "model_used": model}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("AGENTS_PORT", "8120"))
    print(f"[agents] Starting specialized agents on :{port}")
    print(f"[agents] Available: {', '.join(AGENT_MODELS.keys())}")
    uvicorn.run(app, host="0.0.0.0", port=port)
