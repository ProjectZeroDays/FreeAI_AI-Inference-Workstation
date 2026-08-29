"""Custom Pipeline API — manual agent invocation with composable workflows.

Allows users to call individual agent personas directly and chain them
into custom pipelines, bypassing the full autonomous SDLC loop.

Endpoints:
  POST /pipeline/scaffold   - Turn a spec into architecture + files
  POST /pipeline/refactor   - Refactor existing code
  POST /pipeline/debug      - Diagnose and fix bugs
  POST /pipeline/analyze    - Deep technical analysis
  POST /pipeline/review     - Code review with verdict
  POST /pipeline/document   - Generate documentation
  POST /pipeline/custom     - Custom multi-step pipeline
  GET  /pipeline/status     - Check active pipeline runs
"""
import json
import os
import threading
import time
from pathlib import Path

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, Field
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

ROOT = Path(__file__).parent.parent
WORKSPACES_DIR = ROOT / "workspaces"
WORKSPACES_DIR.mkdir(parents=True, exist_ok=True)

PROXY_URL = os.environ.get("PROXY_URL", "http://localhost:8100/proxy")
ROUTER_URL = os.environ.get("ROUTER_URL", "http://localhost:8010/route")
AGENT_API = os.environ.get("AGENT_API", "http://localhost:8020")


def _call_llm(prompt, model=None, max_tokens=4096, temperature=0.2):
    """Call the unified proxy or router."""
    import requests
    url = PROXY_URL if "/proxy" in PROXY_URL else f"{PROXY_URL.rsplit('/', 1)[0]}/proxy"
    payload = {"prompt": prompt, "max_tokens": max_tokens, "temperature": temperature}
    if model:
        payload["model"] = model
    try:
        r = requests.post(url, json=payload, timeout=660)
        r.raise_for_status()
        return r.json()
    except Exception as exc:
        # Fallback to router
        try:
            r2 = requests.post(ROUTER_URL, json={"prompt": prompt,
                        "max_tokens": max_tokens, "temperature": temperature},
                        timeout=660)
            r2.raise_for_status()
            return r2.json()
        except Exception:
            raise HTTPException(status_code=502, detail=f"LLM unavailable: {exc}")


def _extract_text(result):
    resp = result.get("response", {})
    if isinstance(resp, dict):
        return resp.get("content", "")
    return str(resp)


def _write_file(workspace, path, content):
    """Write a file inside a workspace directory."""
    full = workspace / path
    workspace_real = workspace.resolve()
    full_real = full.resolve()
    try:
        full_real.relative_to(workspace_real)
    except ValueError:
        raise Exception("Invalid file path")
    full_real.parent.mkdir(parents=True, exist_ok=True)
    full_real.write_text(content, encoding="utf-8")
    return str(full_real)


def _read_tree(workspace):
    """List files in a workspace as a tree string."""
    lines = []
    for f in sorted(workspace.rglob("*")):
        if f.is_file():
            rel = str(f.relative_to(workspace))
            size = f.stat().st_size
            lines.append(f"  {rel} ({size}B)")
    return "\n".join(lines) or "(empty workspace)"


# ── In-memory pipeline runs ────────────────────────────────────────
_runs = {}
_runs_lock = threading.Lock()


def _new_run(pipeline_id, spec, steps):
    run = {
        "pipeline_id": pipeline_id,
        "spec": spec,
        "steps": steps,
        "status": "running",
        "results": {},
        "started_at": time.time(),
        "completed_at": None,
        "error": None,
    }
    with _runs_lock:
        _runs[pipeline_id] = run
    return run


# ── Pipeline implementations ───────────────────────────────────────
def pipeline_scaffold(spec, profile="creative", max_tokens=4096):
    """Turn a spec into a full project scaffold."""
    prompt = f"""You are a senior production engineer.

Task: Turn this spec into a production-ready project scaffold.

Spec:
{spec}

Deliver a complete project structure with:
1. Architecture overview
2. Tech stack selection with justification
3. Directory structure (tree format)
4. Key module descriptions
5. Data models / schemas
6. API contracts (if applicable)
7. CI/CD outline
8. Infrastructure notes (Docker/K8s if relevant)

Output each file as a markdown code block:
\`\`\`
path/to/file.ext
<full file content>
\`\`\`
"""
    result = _call_llm(prompt, max_tokens=max_tokens,
                       temperature={"creative": 0.8, "balanced": 0.2,
                                    "strict": 0.0}.get(profile, 0.2))
    return {"phase": "scaffold", "result": result}


def pipeline_refactor(code, language="python", goals="clean, idiomatic, maintainable",
                      profile="balanced"):
    """Refactor code with the fixer agent."""
    prompt = f"""You are a refactoring specialist for {language}.

Task: Refactor the following code to be {goals}.

Code:
\`\`\`{language}
{code}
\`\`\`

Deliver:
1. Brief explanation of changes
2. Refactored code as complete file blocks
"""
    result = _call_llm(prompt, max_tokens=4096,
                       temperature={"strict": 0.0, "balanced": 0.2,
                                    "creative": 0.8}.get(profile, 0.2))
    return {"phase": "refactor", "result": result}


def pipeline_debug(code, error, language="python", profile="strict"):
    """Debug and fix code with errors."""
    prompt = f"""You are a debugging specialist for {language}.

Task: Find and fix the bug.

Code:
\`\`\`{language}
{code}
\`\`\`

Error:
{error}

Deliver:
1. Root cause explanation
2. Fixed code with explanations
3. Notes on prevention
"""
    result = _call_llm(prompt, max_tokens=4096,
                       temperature=0.0)  # strict for debugging
    return {"phase": "debug", "result": result}


def pipeline_analyze(context, question, profile="balanced"):
    """Deep technical analysis."""
    prompt = f"""You are a reasoning specialist.

Context:
{context}

Question:
{question}

Think step by step, then answer clearly with evidence.
Consider trade-offs, edge cases, and alternatives.
"""
    result = _call_llm(prompt, max_tokens=4096,
                       temperature={"balanced": 0.2, "creative": 0.8}[profile])
    return {"phase": "analyze", "result": result}


def pipeline_review(code, spec="", profile="strict"):
    """Code review with verdict."""
    prompt = f"""You are a strict code reviewer.

Spec:
{spec}

Code to review:
\`\`\`
{code}
\`\`\`

First line MUST be exactly one of:
VERDICT: PASS
VERDICT: FIX

If FIX, list concrete issues after it, one per line, prefixed "- ".
Then suggest the fixed version.
"""
    result = _call_llm(prompt, max_tokens=2048, temperature=0.0)
    return {"phase": "review", "result": result}


def pipeline_document(spec, tree, sample_code="", profile="balanced"):
    """Generate project documentation."""
    prompt = f"""You are a technical writer finishing a generated project.

Spec:
{spec}

Final file tree:
{tree}

Key file excerpts:
{sample_code}

Write comprehensive project documentation:
=== FILE: README.md ===
<overview, setup, usage, architecture>
=== END ===
=== FILE: docs/API.md ===
<endpoints or module reference if applicable>
=== END ===
"""
    result = _call_llm(prompt, max_tokens=3072,
                       temperature={"balanced": 0.2, "creative": 0.4}[profile])
    return {"phase": "document", "result": result}


# ── Custom pipeline runner ─────────────────────────────────────────
def run_custom_pipeline(spec, steps, workspace_dir=None, profile="balanced"):
    """Execute a custom multi-step pipeline.

    steps: list of {"phase": "scaffold|refactor|debug|analyze|review|document",
                    "input": {...}}
    """
    pipeline_id = f"pipe_{int(time.time())}_{os.getpid()}"
    run = _new_run(pipeline_id, spec, steps)

    try:
        ws = Path(workspace_dir) if workspace_dir else WORKSPACES_DIR / pipeline_id
        ws.mkdir(parents=True, exist_ok=True)

        accumulated_code = ""
        accumulated_tree = ""

        for i, step in enumerate(steps):
            phase = step.get("phase", "").lower()
            inp = step.get("input", {})
            run["results"][f"step_{i}"] = {"phase": phase, "status": "running"}

            if phase == "scaffold":
                out = pipeline_scaffold(inp.get("spec", spec),
                                        inp.get("profile", profile))
            elif phase == "refactor":
                out = pipeline_refactor(inp.get("code", accumulated_code),
                                        inp.get("language", "python"),
                                        inp.get("goals", "clean code"),
                                        inp.get("profile", profile))
            elif phase == "debug":
                out = pipeline_debug(inp.get("code", accumulated_code),
                                     inp.get("error", ""),
                                     inp.get("language", "python"),
                                     inp.get("profile", "strict"))
            elif phase == "analyze":
                out = pipeline_analyze(inp.get("context", spec),
                                       inp.get("question", "Analyze this"),
                                       inp.get("profile", profile))
            elif phase == "review":
                out = pipeline_review(inp.get("code", accumulated_code),
                                      inp.get("spec", spec),
                                      inp.get("profile", "strict"))
            elif phase == "document":
                out = pipeline_document(spec, accumulated_tree,
                                        accumulated_code,
                                        inp.get("profile", profile))
            else:
                out = {"phase": phase, "result": {"error": f"Unknown phase: {phase}"}}

            run["results"][f"step_{i}"]["status"] = "done"
            run["results"][f"step_{i}"]["output"] = str(out.get("result", ""))[:2000]

            # Accumulate for next steps
            text = _extract_text(out.get("result", {}))
            if text:
                accumulated_code = text
                # Try to parse tree from output
                import re
                tree_match = re.search(r'(\w+:.*(?:\n\s+\w+.*)*)', text)
                if tree_match:
                    accumulated_tree = tree_match.group(1)

        run["status"] = "done"
        run["completed_at"] = time.time()
        run["workspace"] = str(ws)

    except Exception as exc:
        run["status"] = "failed"
        run["error"] = str(exc)
        run["completed_at"] = time.time()

    with _runs_lock:
        _runs[pipeline_id] = run

    return pipeline_id


# ── FastAPI ────────────────────────────────────────────────────────
if HAS_FASTAPI:
    app = FastAPI(title="Custom Pipeline API", version="1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:8030", "http://127.0.0.1:8030"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    class ScaffoldRequest(BaseModel):
        spec: str
        profile: str = "creative"
        max_tokens: int = 4096

    class RefactorRequest(BaseModel):
        code: str
        language: str = "python"
        goals: str = "clean, idiomatic, maintainable"
        profile: str = "balanced"

    class DebugRequest(BaseModel):
        code: str
        error: str
        language: str = "python"
        profile: str = "strict"

    class AnalyzeRequest(BaseModel):
        context: str
        question: str
        profile: str = "balanced"

    class ReviewRequest(BaseModel):
        code: str
        spec: str = ""
        profile: str = "strict"

    class DocumentRequest(BaseModel):
        spec: str
        tree: str = ""
        sample_code: str = ""
        profile: str = "balanced"

    class PipelineStep(BaseModel):
        phase: str
        input: dict = {}

    class CustomPipelineRequest(BaseModel):
        spec: str
        steps: list[PipelineStep]
        workspace_dir: str | None = None
        profile: str = "balanced"

    @app.get("/health")
    def health():
        return {"status": "ok", "active_pipelines": len(_runs)}

    @app.post("/pipeline/scaffold")
    def scaffold(req: ScaffoldRequest):
        return pipeline_scaffold(req.spec, req.profile, req.max_tokens)

    @app.post("/pipeline/refactor")
    def refactor(req: RefactorRequest):
        return pipeline_refactor(req.code, req.language, req.goals, req.profile)

    @app.post("/pipeline/debug")
    def debug(req: DebugRequest):
        return pipeline_debug(req.code, req.error, req.language, req.profile)

    @app.post("/pipeline/analyze")
    def analyze(req: AnalyzeRequest):
        return pipeline_analyze(req.context, req.question, req.profile)

    @app.post("/pipeline/review")
    def review(req: ReviewRequest):
        return pipeline_review(req.code, req.spec, req.profile)

    @app.post("/pipeline/document")
    def document(req: DocumentRequest):
        return pipeline_document(req.spec, req.tree, req.sample_code, req.profile)

    @app.post("/pipeline/custom")
    def custom_pipeline(req: CustomPipelineRequest):
        pid = run_custom_pipeline(req.spec, [s.model_dump() for s in req.steps],
                                  req.workspace_dir, req.profile)
        return {"pipeline_id": pid, "status": "started"}

    @app.get("/pipeline/status/{pipeline_id}")
    def pipeline_status(pipeline_id: str):
        with _runs_lock:
            run = _runs.get(pipeline_id)
        if not run:
            raise HTTPException(status_code=404, detail="Pipeline not found")
        return run

    @app.get("/pipeline/status")
    def list_pipelines():
        with _runs_lock:
            runs = list(_runs.values())
        return {"pipelines": runs, "total": len(runs)}

    @app.post("/pipeline/cancel/{pipeline_id}")
    def cancel_pipeline(pipeline_id: str):
        with _runs_lock:
            run = _runs.get(pipeline_id)
            if run:
                run["status"] = "cancelled"
                run["completed_at"] = time.time()
                return {"status": "cancelled"}
        raise HTTPException(status_code=404, detail="Pipeline not found")


if __name__ == "__main__":
    if HAS_FASTAPI:
        import uvicorn
        port = int(os.environ.get("PIPELINE_PORT", "8170"))
        print(f"[pipeline] Starting custom pipeline API on :{port}")
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        print("[pipeline] FastAPI not available. Use individual functions directly.")
